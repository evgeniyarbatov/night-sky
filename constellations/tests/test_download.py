import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from download import extract_download_links  # noqa: E402

SAMPLE_HTML = """
<html><body>
  <a href="Andromeda.gif">Andromeda GIF</a>
  <a href="Andromeda.txt">Andromeda boundary</a>
  <a href="index.html">Index</a>
  <a href="Aquarius.GIF">wrong case, ignored</a>
</body></html>
"""


class ExtractDownloadLinksTests(unittest.TestCase):
    def test_splits_gif_and_txt_links(self) -> None:
        gif_links, txt_links = extract_download_links(SAMPLE_HTML)
        self.assertEqual(gif_links, ["Andromeda.gif"])
        self.assertEqual(txt_links, ["Andromeda.txt"])

    def test_ignores_unrelated_links(self) -> None:
        gif_links, txt_links = extract_download_links(SAMPLE_HTML)
        all_links = gif_links + txt_links
        self.assertNotIn("index.html", all_links)
        self.assertNotIn("Aquarius.GIF", all_links)

    def test_no_links_returns_two_empty_lists(self) -> None:
        self.assertEqual(extract_download_links("<html></html>"), ([], []))


if __name__ == "__main__":
    unittest.main()
