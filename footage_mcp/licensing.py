"""Turn messy license strings into fields an agent can act on.

This is a best-effort reading, not legal advice. The original license name and URL
are always kept so a human can check.
"""
from __future__ import annotations

import re


def license_info(name: str = "", url: str = "", *, attribution: str = "", notes: str = "") -> dict:
    text = f"{name} {url}".lower()
    commercial: bool | None = None
    attribution_required: bool | None = None
    modifiable: bool | None = None

    if re.search(r"publicdomain|public domain|\bcc0\b|\bpd\b|zero/1\.0|pdm", text):
        commercial, attribution_required, modifiable = True, False, True
    elif "creativecommons.org" in text or re.search(r"\bcc[- ]by", text):
        attribution_required = True
        commercial = not re.search(r"\bnc\b|-nc|noncommercial|by-nc", text)
        modifiable = not re.search(r"\bnd\b|-nd|noderiv|by-nd|nc-nd", text)
    return {
        "name": name.strip() or "unknown",
        "url": url or None,
        "commercial_use": commercial,
        "attribution_required": attribution_required,
        "modifiable": modifiable,
        "attribution": attribution.strip() or None,
        "notes": notes or None,
    }


def warnings_for(lic: dict) -> list[str]:
    out = []
    if lic.get("commercial_use") is False:
        out.append("non-commercial license: do not use in monetized or company videos")
    if lic.get("commercial_use") is None:
        out.append("license not recognized: check the source page before publishing")
    if lic.get("modifiable") is False:
        out.append("no-derivatives license: trimming or re-editing may not be allowed")
    if lic.get("attribution_required"):
        out.append("attribution required: keep the CREDITS.md line in the video description")
    return out
