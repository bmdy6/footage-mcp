import subprocess, sys, unittest

from footage_mcp import service as S


class GuideTest(unittest.TestCase):
    def test_guide_bundled(self):
        text = S.video_script_guide()
        self.assertIn("文稿结构", text)
        self.assertIn("交付前自查", text)

    def test_cli_guide(self):
        out = subprocess.run([sys.executable, "-m", "footage_mcp", "guide"], capture_output=True, text=True, check=True).stdout
        self.assertIn("选题", out)


if __name__ == "__main__":
    unittest.main()
