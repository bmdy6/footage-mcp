"""Offline tests: no network, API responses are fixtures."""
from __future__ import annotations

import json
import unittest
from unittest import mock

from footage_mcp import licensing, service
from footage_mcp.sources import archive, commons, nasa, parse_duration, pexels, pixabay

PEXELS_VIDEO = {
    "id": 3195394, "width": 3840, "height": 2160, "duration": 12,
    "url": "https://www.pexels.com/video/server-room-lights-3195394/",
    "image": "https://images.pexels.com/videos/3195394/pictures/preview-0.jpg",
    "user": {"name": "Jane Doe"},
    "video_files": [
        {"link": "https://videos.pexels.com/a-uhd.mp4", "file_type": "video/mp4", "width": 3840},
        {"link": "https://videos.pexels.com/a-hd.mp4", "file_type": "video/mp4", "width": 1920},
        {"link": "https://videos.pexels.com/a-sd.mp4", "file_type": "video/mp4", "width": 960},
    ],
}

PIXABAY_HIT = {
    "id": 125, "pageURL": "https://pixabay.com/videos/id-125/", "tags": "flowers, yellow",
    "duration": 12, "user": "Coverr-Free-Footage",
    "videos": {
        "large": {"url": "https://cdn.pixabay.com/l.mp4", "width": 3840, "height": 2160, "thumbnail": "https://cdn.pixabay.com/l.jpg"},
        "medium": {"url": "https://cdn.pixabay.com/m.mp4", "width": 1920, "height": 1080, "thumbnail": "https://cdn.pixabay.com/m.jpg"},
    },
}


class LicenseTests(unittest.TestCase):
    def test_public_domain(self):
        lic = licensing.license_info("", "http://creativecommons.org/licenses/publicdomain/")
        self.assertEqual((lic["commercial_use"], lic["attribution_required"]), (True, False))

    def test_cc_by_sa(self):
        lic = licensing.license_info("CC BY-SA 4.0", "https://creativecommons.org/licenses/by-sa/4.0")
        self.assertEqual((lic["commercial_use"], lic["attribution_required"], lic["modifiable"]), (True, True, True))

    def test_non_commercial_no_derivs(self):
        lic = licensing.license_info("CC BY-NC-ND 3.0", "https://creativecommons.org/licenses/by-nc-nd/3.0/")
        self.assertEqual((lic["commercial_use"], lic["modifiable"]), (False, False))
        self.assertEqual(len(licensing.warnings_for(lic)), 3)

    def test_unknown(self):
        self.assertIsNone(licensing.license_info("All rights reserved")["commercial_use"])


class SourceParsingTests(unittest.TestCase):
    def test_pexels_picks_hd_file(self):
        c = pexels._to_clip(PEXELS_VIDEO)
        self.assertEqual(c["id"], "pexels:3195394")
        self.assertEqual(c["video_url"], "https://videos.pexels.com/a-hd.mp4")
        self.assertEqual(c["title"], "server room lights")
        self.assertTrue(c["license"]["commercial_use"])

    def test_pixabay_skips_4k(self):
        c = pixabay._to_clip(PIXABAY_HIT)
        self.assertEqual(c["video_url"], "https://cdn.pixabay.com/m.mp4")
        self.assertEqual(c["thumbnail"], "https://cdn.pixabay.com/m.jpg")

    def test_archive_file_choice(self):
        files = [
            {"name": "x_64kb.mp4", "format": "64Kb MPEG4", "width": "160"},
            {"name": "x.mp4", "format": "h.264", "width": "640"},
            {"name": "x.ogv", "format": "Ogg Video", "width": "400"},
        ]
        self.assertEqual(archive._pick_file(files)["name"], "x.mp4")

    def test_commons_accepts_ogv_rejects_audio(self):
        page = {"title": "File:A.ogv", "imageinfo": [{"mime": "application/ogg", "width": 640, "height": 360,
                                                      "url": "https://upload.wikimedia.org/a.ogv", "extmetadata": {}}]}
        self.assertIsNotNone(commons._to_clip(page))
        page["imageinfo"][0]["width"] = 0
        self.assertIsNone(commons._to_clip(page))

    def test_nasa_license(self):
        self.assertTrue(nasa._license("GSFC")["commercial_use"])

    def test_duration(self):
        self.assertEqual(parse_duration("1:02:03"), 3723)
        self.assertEqual(parse_duration("812.58"), 812.58)
        self.assertIsNone(parse_duration(""))


class SearchTests(unittest.TestCase):
    def test_interleave_and_failures(self):
        fake = {
            "pexels": mock.Mock(needs_key=lambda: None, search=lambda q, n: [pexels._to_clip(PEXELS_VIDEO)] * 3),
            "pixabay": mock.Mock(needs_key=lambda: "PIXABAY_API_KEY"),
            "commons": mock.Mock(needs_key=lambda: None, search=mock.Mock(side_effect=RuntimeError("boom"))),
            "nasa": mock.Mock(needs_key=lambda: None, search=lambda q, n: [nasa._to_clip({"data": [{"nasa_id": "x"}]})] * 3),
        }
        with mock.patch.object(service, "SOURCES", fake):
            r = service.search("servers", limit=4)
        self.assertEqual([c["source"] for c in r["results"]], ["pexels", "nasa", "pexels", "nasa"])
        self.assertTrue(r["sources"]["pixabay"].startswith("skipped"))
        self.assertTrue(r["sources"]["commons"].startswith("error"))
        self.assertNotIn("video_url", r["results"][1])  # None fields dropped

    def test_filters(self):
        c = pexels._to_clip(PEXELS_VIDEO)
        self.assertFalse(service._keep(c, 20, None, None, False))
        self.assertFalse(service._keep(c, None, None, "portrait", False))
        self.assertTrue(service._keep(c, 5, 30, "landscape", True))

    def test_bad_ids(self):
        with self.assertRaises(ValueError):
            service.resolve("nope")
        with self.assertRaises(ValueError):
            service.search("  ")


class LibraryTests(unittest.TestCase):
    def test_manifest_and_credits(self):
        import tempfile
        from pathlib import Path

        with tempfile.TemporaryDirectory() as d:
            lic = licensing.license_info("CC BY 4.0", "https://creativecommons.org/licenses/by/4.0", attribution="Ann, CC BY 4.0")
            service._save(Path(d), {"version": 1, "clips": [{
                "file": "a.mp4", "clip_id": "commons:File:A.webm", "title": "A", "source": "commons",
                "page_url": "https://commons.wikimedia.org/wiki/File:A.webm", "start": 0, "duration": 4,
                "note": "line 1", "license": lic, "downloaded_at": "now"}]})
            lib = service.library(d)
            self.assertEqual(lib["count"], 1)
            self.assertFalse(lib["clips"][0]["exists"])
            self.assertIn("Ann, CC BY 4.0", (Path(d) / "CREDITS.md").read_text())
            json.loads((Path(d) / "footage.json").read_text())


if __name__ == "__main__":
    unittest.main()
