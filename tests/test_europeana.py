"""Europeana contract tests; HTTP and ffmpeg are isolated from the network."""
from __future__ import annotations

import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock

from footage_mcp import net, service
from footage_mcp.sources import SOURCES, europeana

PD = "http://creativecommons.org/publicdomain/mark/1.0/"
BY = "https://creativecommons.org/licenses/by/4.0/"
NC = "https://creativecommons.org/licenses/by-nc/4.0/"
VIDEO = "https://www.openbeelden.nl/files/train.mp4"
NATIVE_ID = "123/train"
ITEM = {
    "id": "/" + NATIVE_ID, "type": "VIDEO", "title": ["Train"],
    "edmIsShownBy": [VIDEO], "rights": [PD], "dataProvider": ["Film archive"],
    "dcCreator": ["Ann"], "dcDescription": ["<p>A train</p>"],
    "edmPreview": ["https://api.europeana.eu/thumbnail.jpg"],
}
RECORD = {
    "about": "/" + NATIVE_ID, "type": "VIDEO", "title": ["Train"],
    "proxies": [{"dcCreator": {"en": ["Ann"]}, "dcDescription": {"en": ["A train"]}}],
    "aggregations": [{
        "edmIsShownBy": VIDEO, "edmDataProvider": {"en": ["Film archive"]},
        "edmRights": {"def": [PD]},
        "webResources": [{"about": VIDEO, "textAttributionSnippet": "Ann, Film archive, Public Domain Mark"}],
    }],
}


class EuropeanaParsingTests(unittest.TestCase):
    def test_open_licenses_and_metadata(self):
        for rights, name, credit in (
            (PD, "Public Domain Mark", False),
            ("https://creativecommons.org/publicdomain/zero/1.0/", "CC0 1.0", False),
            (BY, "CC BY 4.0", True),
            ("http://creativecommons.org/licenses/by-sa/3.0/nl/", "CC BY-SA 3.0", True),
        ):
            with self.subTest(rights=rights):
                c = europeana._to_clip(ITEM | {"rights": [rights]})
                self.assertEqual(c["id"], "europeana:" + NATIVE_ID)
                self.assertEqual(c["description"], "A train")
                self.assertEqual(c["license"]["url"], rights)
                self.assertEqual(c["license"]["name"], name)
                self.assertIs(c["license"]["commercial_use"], True)
                self.assertIs(c["license"]["modifiable"], True)
                self.assertIs(c["license"]["attribution_required"], credit)
                self.assertIn("Ann", c["license"]["attribution"])
                self.assertEqual(c["page_url"], "https://www.europeana.eu/item/" + NATIVE_ID)

    def test_rejects_unapproved_and_ambiguous_rights(self):
        for rights in (None, [], [""], [NC], ["All rights reserved"],
                       ["https://creativecommons.org/licenses/by-nd/4.0/"],
                       ["https://rightsstatements.org/vocab/NoC-NC/1.0/"],
                       ["https://creativecommons.org.evil.example/licenses/by/4.0/"],
                       ["https://example.org/publicdomain/mark/1.0/"], [PD, NC], [PD, BY],
                       ["https://[invalid/"], {"en": [PD], "def": [NC]}):
            with self.subTest(rights=rights):
                self.assertIsNone(europeana._to_clip(ITEM | {"rights": rights}))

    def test_handles_empty_fields(self):
        c = europeana._to_clip(ITEM | {"title": [], "dcCreator": [], "dataProvider": [], "dcDescription": []})
        self.assertEqual(c["title"], "/" + NATIVE_ID)
        self.assertEqual(c["creator"], "Europeana")

    def test_selects_video_from_all_links(self):
        c = europeana._to_clip(ITEM | {"edmIsShownBy": ["https://vimeo.com/123", VIDEO + "?dl=1#video"]})
        self.assertEqual(c["video_url"], VIDEO + "?dl=1#video")

    def test_only_http_video_files(self):
        for link in ("https://vimeo.com/123", "file:///tmp/train.mp4", "ftp://example.org/a.mp4",
                     "https://example.org/a.jpg?file=video.mp4", "http://localhost/a.mp4",
                     "http://127.0.0.1/a.mp4", "http://192.168.1.2/a.mp4"):
            with self.subTest(link=link):
                self.assertIsNone(europeana._to_clip(ITEM | {"edmIsShownBy": [link]}))

    def test_upgrades_only_openbeelden_http(self):
        c = europeana._to_clip(ITEM | {"edmIsShownBy": [VIDEO.replace("https:", "http:")]})
        self.assertEqual(c["video_url"], VIDEO)

    def test_rejects_non_video_and_missing_id(self):
        self.assertIsNone(europeana._to_clip(ITEM | {"type": "SOUND"}))
        self.assertIsNone(europeana._to_clip(ITEM | {"id": ""}))


class EuropeanaAPITests(unittest.TestCase):
    def test_search_registered_and_no_key_required(self):
        self.assertIs(SOURCES["europeana"], europeana)
        self.assertIsNone(europeana.needs_key())
        self.assertEqual(service.source_status()["europeana"], "ready")

    def test_demo_and_custom_key_and_query_filters(self):
        for key in ("", "test-user-key"):
            with self.subTest(custom=bool(key)), mock.patch.dict("os.environ", {"EUROPEANA_API_KEY": key}), \
                    mock.patch.object(net, "get_json", return_value={"success": True, "items": [ITEM]}) as get:
                result = service.search("train", sources=["europeana"], limit=1)
                self.assertEqual(result["returned"], 1)
                params = get.call_args.args[1]
                self.assertEqual(params["wskey"], key or "api2demo")
                self.assertEqual(params["qf"], "TYPE:VIDEO")
                self.assertEqual(params["reusability"], "open")
                self.assertEqual(params["query"], "train")
                self.assertLessEqual(params["rows"], 100)

    def test_search_filters_before_limiting(self):
        items = [ITEM | {"rights": [NC]}, ITEM | {"edmIsShownBy": ["https://vimeo.com/1"]}, ITEM, ITEM]
        with mock.patch.object(net, "get_json", return_value={"items": items}):
            self.assertEqual(len(europeana.search("train", 1)), 1)

    def test_empty_search(self):
        with mock.patch.object(net, "get_json", return_value={"success": True}):
            self.assertEqual(europeana.search("train", 5), [])

    def test_api_error(self):
        with mock.patch.object(net, "get_json", return_value={"success": False, "error": "quota exceeded"}):
            with self.assertRaisesRegex(net.FetchError, "quota exceeded"):
                europeana.search("train", 1)
            with self.assertRaisesRegex(net.FetchError, "quota exceeded"):
                europeana.resolve(NATIVE_ID)

    def test_resolve_uses_record_endpoint(self):
        for native in (NATIVE_ID, "/" + NATIVE_ID):
            with self.subTest(native=native), mock.patch.object(net, "get_json", return_value={"object": RECORD}) as get:
                c = europeana.resolve(native)
                self.assertEqual(c["id"], "europeana:" + NATIVE_ID)
                self.assertEqual(c["video_url"], VIDEO)
                self.assertEqual(c["creator"], "Ann")
                self.assertEqual(c["license"]["attribution"], RECORD["aggregations"][0]["webResources"][0]["textAttributionSnippet"])
                self.assertEqual(get.call_args.args[0], "https://api.europeana.eu/record/v2/123/train.json")

    def test_resolve_honors_file_specific_rights(self):
        for rights, allowed in ((NC, False), (BY, True)):
            record = copy.deepcopy(RECORD)
            record["aggregations"][0]["webResources"][0]["webResourceEdmRights"] = {"def": [rights]}
            with self.subTest(rights=rights), mock.patch.object(net, "get_json", return_value={"object": record}):
                if allowed:
                    self.assertEqual(europeana.resolve(NATIVE_ID)["license"]["url"], BY)
                else:
                    with self.assertRaises(net.FetchError):
                        europeana.resolve(NATIVE_ID)

    def test_resolve_rejects_conflicting_aggregation_rights(self):
        record = copy.deepcopy(RECORD)
        record["aggregations"].append({"edmIsShownBy": VIDEO, "edmRights": {"def": [NC]}})
        with mock.patch.object(net, "get_json", return_value={"object": record}):
            with self.assertRaises(net.FetchError):
                europeana.resolve(NATIVE_ID)

    def test_record_proxy_metadata_and_custom_key(self):
        record = copy.deepcopy(RECORD)
        del record["title"]
        record["proxies"][0]["dcTitle"] = {"nl": ["Trein"], "en": ["Train"]}
        with mock.patch.dict("os.environ", {"EUROPEANA_API_KEY": "test-user-key"}), \
                mock.patch.object(net, "get_json", return_value={"object": record}) as get:
            self.assertEqual(europeana.resolve(NATIVE_ID)["title"], "Train")
            self.assertEqual(get.call_args.args[1]["wskey"], "test-user-key")

    def test_whitespace_key_falls_back_to_demo(self):
        with mock.patch.dict("os.environ", {"EUROPEANA_API_KEY": "  "}):
            self.assertEqual(europeana._key(), "api2demo")

    def test_resolve_rejects_missing_restricted_or_viewer(self):
        for record in ({}, RECORD | {"type": "SOUND"}, RECORD | {"about": "/123/other"},
                       RECORD | {"aggregations": [{"edmIsShownBy": VIDEO, "edmRights": {"def": [NC]}}]},
                       RECORD | {"aggregations": [{"edmIsShownBy": "https://vimeo.com/1", "edmRights": {"def": [PD]}}]}):
            with self.subTest(record=record), mock.patch.object(net, "get_json", return_value={"object": record}):
                with self.assertRaises(net.FetchError):
                    service.resolve("europeana:" + NATIVE_ID)

    def test_invalid_ids_do_not_request(self):
        for native in ("", "123", "../train", "123/../train", "123/a?query=x", "123/a#x", "123/a/b"):
            with self.subTest(native=native), mock.patch.object(net, "get_json") as get:
                with self.assertRaises(ValueError):
                    europeana.resolve(native)
                get.assert_not_called()


class EuropeanaServiceTests(unittest.TestCase):
    @mock.patch.object(net, "get_json", return_value={"object": RECORD})
    def test_inspect_accepts_provider_host_and_preserves_licenses(self, get):
        def run(cmd, **kwargs):
            Path(cmd[-1]).write_bytes(b"\xff\xd8fixture")
            return mock.Mock(returncode=0)

        with mock.patch.object(service, "_probe_duration", return_value=10), \
                mock.patch.object(service, "_ffmpeg", return_value="ffmpeg"), \
                mock.patch.object(service.subprocess, "run", side_effect=run):
            meta, jpeg = service.inspect("europeana:" + NATIVE_ID, frames=1)
        self.assertEqual(meta["frame_times"], [5.0])
        self.assertEqual(jpeg, b"\xff\xd8fixture")
        self.assertTrue(meta["license"]["commercial_use"])

    @mock.patch.object(net, "get_json", return_value={"object": RECORD})
    def test_download_writes_license_and_credits(self, get):
        def run(cmd, **kwargs):
            Path(cmd[-1]).write_bytes(b"mp4 fixture")
            self.assertEqual(cmd[cmd.index("-i") + 1], VIDEO)
            return mock.Mock(returncode=0)

        with tempfile.TemporaryDirectory() as d, mock.patch.object(service, "_ffmpeg", return_value="ffmpeg"), \
                mock.patch.object(service.subprocess, "run", side_effect=run):
            result = service.download("europeana:" + NATIVE_ID, d, duration=2)
            manifest = json.loads((Path(d) / "footage.json").read_text())
            self.assertTrue(Path(result["path"]).is_file())
            self.assertEqual(manifest["clips"][0]["license"]["url"], PD)
            self.assertIn("Public Domain Mark", (Path(d) / "CREDITS.md").read_text())

    def test_inspect_keeps_other_sources_host_guard(self):
        with mock.patch.object(service, "resolve", return_value={"source": "nasa", "video_url": VIDEO}), \
                mock.patch.object(service, "_probe_duration", return_value=10), \
                mock.patch.object(service.subprocess, "run", return_value=mock.Mock(returncode=1)):
            with self.assertRaisesRegex(net.FetchError, "host not allowed"):
                service.inspect("nasa:x")


if __name__ == "__main__":
    unittest.main()
