"""Optional MCP adapter coverage; install .[mcp] to run these tests."""
import importlib.util
import json
import unittest
from unittest import mock


@unittest.skipUnless(importlib.util.find_spec("mcp"), "install .[mcp] for MCP adapter tests")
class EuropeanaMCPTests(unittest.TestCase):
    def test_mcp_adapters_route_europeana(self):
        from footage_mcp import mcp_server as server

        clip_id = "europeana:123/train"
        meta = {"id": clip_id, "license": {"commercial_use": True}}
        with mock.patch.object(server.S, "search", return_value={"results": [meta]}) as search:
            result = json.loads(server.footage_search("train", sources=["europeana"]))
            self.assertEqual(result["results"][0]["id"], clip_id)
            self.assertEqual(search.call_args.args[2], ["europeana"])
        with mock.patch.object(server.S, "inspect", return_value=(meta, b"jpeg")) as inspect:
            result = server.footage_inspect(clip_id, frames=1)
            self.assertEqual(json.loads(result[0]), meta)
            inspect.assert_called_once_with(clip_id, 1)
        with mock.patch.object(server.S, "download", return_value={"entry": meta}) as download:
            result = json.loads(server.footage_download(clip_id, "footage", duration=2))
            self.assertEqual(result["entry"], meta)
            download.assert_called_once_with(clip_id, "footage", 0, 2, "", keep_audio=False)
        with mock.patch.object(server.S, "library", return_value={"clips": []}):
            result = json.loads(server.footage_library("footage"))
            self.assertEqual(result["sources"]["europeana"], "ready")


if __name__ == "__main__":
    unittest.main()
