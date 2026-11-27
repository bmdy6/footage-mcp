import importlib.util, subprocess, sys, unittest

from footage_mcp import service as S


class GuideTest(unittest.TestCase):
    def test_guide_bundled(self):
        text = S.video_script_guide()
        self.assertIn("文稿结构", text)
        self.assertIn("交付前自查", text)

    def test_cli_guide(self):
        out = subprocess.run([sys.executable, "-m", "footage_mcp", "guide"], capture_output=True, text=True, check=True).stdout
        self.assertIn("选题", out)

    def test_talking_head_guide_bundled(self):
        text = S.talking_head_guide()
        for key in ("按文字剪", "强制对齐", "verify.py", "踩过的坑"):
            self.assertIn(key, text)

    def test_cli_talking_head_guide(self):
        out = subprocess.run([sys.executable, "-m", "footage_mcp", "guide", "--talking-head"], capture_output=True, text=True, check=True).stdout
        self.assertIn("剪辑稿", out)

    @unittest.skipUnless(importlib.util.find_spec("mcp"), "install .[mcp] for MCP adapter tests")
    def test_mcp_tool_registered(self):
        from footage_mcp import mcp_server
        self.assertEqual(mcp_server.talking_head_guide(), S.talking_head_guide())


if __name__ == "__main__":
    unittest.main()
