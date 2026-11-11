"""search / inspect / download / library: the four things an agent needs from a footage library."""
from __future__ import annotations

import json
import re
import shutil
import subprocess
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from footage_mcp import net
from footage_mcp.licensing import warnings_for
from footage_mcp.sources import SOURCES

MANIFEST = "footage.json"
CREDITS = "CREDITS.md"


# ---------- search ----------

def search(query: str, limit: int = 12, sources: list[str] | None = None,
           min_duration: float | None = None, max_duration: float | None = None,
           orientation: str | None = None, commercial_only: bool = False) -> dict:
    query = (query or "").strip()
    if not query:
        raise ValueError("query is empty")
    limit = max(1, min(int(limit), 50))
    names = sources or list(SOURCES)
    unknown = [n for n in names if n not in SOURCES]
    if unknown:
        raise ValueError(f"unknown sources: {unknown}; choose from {list(SOURCES)}")

    status: dict[str, str] = {}
    active = []
    for n in names:
        key = SOURCES[n].needs_key()
        if key:
            status[n] = f"skipped: set {key}"
        else:
            active.append(n)

    per_source = limit if len(active) <= 1 else max(limit, 8)
    buckets: dict[str, list[dict]] = {}
    with ThreadPoolExecutor(max_workers=max(1, len(active))) as pool:
        futures = {n: pool.submit(SOURCES[n].search, query, per_source) for n in active}
        for n, fut in futures.items():
            try:
                found = [c for c in fut.result() if _keep(c, min_duration, max_duration, orientation, commercial_only)]
                buckets[n] = found
                status[n] = f"ok: {len(found)}"
            except Exception as e:  # one broken source must not break the others
                buckets[n] = []
                status[n] = f"error: {e}"

    results: list[dict] = []
    i = 0
    while len(results) < limit and any(i < len(b) for b in buckets.values()):
        for n in active:
            if i < len(buckets[n]) and len(results) < limit:
                results.append(buckets[n][i])
        i += 1
    results = [{k: v for k, v in c.items() if v is not None} for c in results]  # fewer tokens
    return {"query": query, "returned": len(results), "sources": status, "results": results,
            "next_step": "footage_inspect(id) to see frames, then footage_download(id, start, duration, out_dir)"}


def _keep(c: dict, lo, hi, orientation, commercial_only) -> bool:
    d = c.get("duration")
    if d is not None and ((lo and d < lo) or (hi and d > hi)):
        return False
    w, h = c.get("width"), c.get("height")
    if orientation and w and h:
        actual = "landscape" if w > h else "portrait" if h > w else "square"
        if actual != orientation:
            return False
    if commercial_only and (c.get("license") or {}).get("commercial_use") is not True:
        return False
    return True


# ---------- resolve ----------

def resolve(clip_id: str) -> dict:
    source, _, native = (clip_id or "").partition(":")
    if source not in SOURCES or not native:
        raise ValueError(f"bad clip id {clip_id!r}; expected '<source>:<id>' from footage_search")
    key = SOURCES[source].needs_key()
    if key:
        raise ValueError(f"{source} needs {key}")
    c = SOURCES[source].resolve(native)
    if not c.get("video_url"):
        raise net.FetchError(f"no downloadable video file for {clip_id}")
    return c


def _ffmpeg() -> str:
    exe = shutil.which("ffmpeg")
    if not exe:
        raise RuntimeError("ffmpeg not found on PATH; install it (brew install ffmpeg / apt install ffmpeg)")
    return exe


def _probe_duration(url: str) -> float | None:
    exe = shutil.which("ffprobe")
    if not exe:
        return None
    try:
        out = subprocess.run([exe, "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", url],
                             capture_output=True, text=True, timeout=60).stdout.strip()
        return round(float(out), 2)
    except (ValueError, subprocess.TimeoutExpired):
        return None


# ---------- inspect ----------

def inspect(clip_id: str, frames: int = 6) -> tuple[dict, bytes]:
    """Grab evenly spaced frames from the real video and tile them into one contact sheet JPEG."""
    c = resolve(clip_id)
    url = c["video_url"]  # comes from the source API, never from the caller
    # Europeana aggregates files on provider domains; its resolver validates the
    # direct HTTP(S) link. Keep the existing host guard for the other sources.
    if c["source"] != "europeana" and not net.is_media_host(url):
        raise net.FetchError("video host not allowed")
    duration = c.get("duration") or _probe_duration(url)
    if duration:
        c["duration"] = duration
    frames = max(1, min(int(frames), 12))
    total = duration or 10.0
    times = [round(total * (i + 0.5) / frames, 2) for i in range(frames)]
    cols = 3 if frames > 4 else frames
    rows = -(-frames // cols)
    ff = _ffmpeg()
    with tempfile.TemporaryDirectory() as tmp:
        def grab(i_t):
            i, t = i_t
            out = Path(tmp) / f"raw{i:02d}.jpg"
            try:
                r = subprocess.run([ff, "-v", "error", "-ss", str(t), "-i", url, "-frames:v", "1",
                                    "-vf", "scale=360:-2", "-q:v", "4", "-y", str(out)],
                                   capture_output=True, timeout=90)
            except subprocess.TimeoutExpired:
                return None
            return (t, out) if r.returncode == 0 and out.exists() else None

        with ThreadPoolExecutor(max_workers=frames) as pool:
            ok = [g for g in pool.map(grab, enumerate(times)) if g]
        if not ok:
            raise RuntimeError("could not read any frame from the video")
        for n, (_, path) in enumerate(ok, 1):  # renumber so the tile input has no gaps
            path.rename(Path(tmp) / f"f{n:02d}.jpg")
        got = len(ok)
        times = [t for t, _ in ok]
        sheet = Path(tmp) / "sheet.jpg"
        rows = -(-got // cols)
        subprocess.run([ff, "-v", "error", "-framerate", "1", "-i", str(Path(tmp) / "f%02d.jpg"),
                        "-vf", f"tile={cols}x{rows}:padding=4:color=white", "-frames:v", "1", "-q:v", "4",
                        "-y", str(sheet)], check=True, capture_output=True, timeout=60)
        image = sheet.read_bytes()
    c["frame_times"] = times[:got]
    c["license_warnings"] = warnings_for(c.get("license") or {})
    return c, image


# ---------- download ----------

def _safe(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "-", s).strip("-")[:60] or "clip"


def download(clip_id: str, out_dir: str, start: float = 0, duration: float | None = None,
             note: str = "", max_width: int = 1920, keep_audio: bool = False) -> dict:
    c = resolve(clip_id)
    out = Path(out_dir).expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)
    start = max(0.0, float(start or 0))
    if duration is not None:
        duration = max(0.5, min(float(duration), 600.0))
    elif not c.get("duration") or c["duration"] > 600:
        duration = 30.0  # long films: never pull a whole hour by accident
    name = f"{c['source']}-{_safe(c['id'].split(':', 1)[1])}-{int(start)}s.mp4"
    target = out / name
    cmd = [_ffmpeg(), "-v", "error", "-ss", str(start), "-i", c["video_url"]]
    if duration:
        cmd += ["-t", str(duration)]
    cmd += ["-vf", f"scale='min({int(max_width)},iw)':-2", "-c:v", "libx264", "-preset", "veryfast",
            "-crf", "20", "-pix_fmt", "yuv420p", "-movflags", "+faststart"]
    cmd += ["-c:a", "aac", "-b:a", "128k"] if keep_audio else ["-an"]
    r = subprocess.run(cmd + ["-y", str(target)], capture_output=True, text=True, timeout=900)
    if r.returncode != 0:
        raise RuntimeError(f"ffmpeg failed: {r.stderr.strip()[-400:]}")

    entry = {
        "file": name,
        "clip_id": c["id"],
        "title": c["title"],
        "source": c["source"],
        "page_url": c["page_url"],
        "start": start,
        "duration": duration or c.get("duration"),
        "note": note or None,
        "license": c["license"],
        "downloaded_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
    }
    manifest = _load(out)
    manifest["clips"] = [e for e in manifest["clips"] if e["file"] != name] + [entry]
    _save(out, manifest)
    return {"path": str(target), "entry": entry, "license_warnings": warnings_for(c["license"]),
            "credits_file": str(out / CREDITS)}


# ---------- library (the footage context of a video project) ----------

def _load(out: Path) -> dict:
    p = out / MANIFEST
    if p.exists():
        return json.loads(p.read_text("utf-8"))
    return {"version": 1, "clips": []}


def _save(out: Path, manifest: dict) -> None:
    (out / MANIFEST).write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", "utf-8")
    lines = ["# Footage credits", "", "Generated by footage-mcp. Keep this with the video description.", ""]
    for e in manifest["clips"]:
        lic = e["license"] or {}
        who = lic.get("attribution") or e["source"]
        lines.append(f"- **{e['title']}** — {who}. License: {lic.get('name')}"
                     f"{' (' + lic['url'] + ')' if lic.get('url') else ''}. Source: {e['page_url']}")
    (out / CREDITS).write_text("\n".join(lines) + "\n", "utf-8")


def library(out_dir: str) -> dict:
    out = Path(out_dir).expanduser().resolve()
    m = _load(out)
    for e in m["clips"]:
        e["exists"] = (out / e["file"]).exists()
    return {"dir": str(out), "count": len(m["clips"]), "clips": m["clips"]}


def source_status() -> dict:
    return {n: ("needs " + k) if (k := m.needs_key()) else "ready" for n, m in SOURCES.items()}
