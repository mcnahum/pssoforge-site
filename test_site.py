"""Check generated public content, routes and the dependency-free page contract."""

from html.parser import HTMLParser
from pathlib import Path
import unittest
from urllib.parse import urlparse

import build_site


ROOT = Path(__file__).resolve().parent


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


class SiteTests(unittest.TestCase):
    def test_all_routes_and_internal_links_exist(self):
        pages = list(ROOT.rglob("*.html"))
        self.assertEqual(len(pages), 8)
        for path in pages:
            with self.subTest(path=str(path.relative_to(ROOT))):
                parser = PageParser()
                parser.feed(path.read_text(encoding="utf-8"))
                for tag, attrs in parser.tags:
                    if tag == "a" and attrs.get("href", "").startswith("/"):
                        target = ROOT / urlparse(attrs["href"]).path.lstrip("/")
                        if target.is_dir():
                            target /= "index.html"
                        self.assertTrue(target.is_file(), attrs["href"])

    def test_self_contained_accessible_pages(self):
        for path in ROOT.rglob("*.html"):
            with self.subTest(path=str(path.relative_to(ROOT))):
                text = path.read_text(encoding="utf-8")
                parser = PageParser()
                parser.feed(text)
                self.assertEqual(sum(tag == "h1" for tag, _ in parser.tags), 1)
                self.assertEqual(sum(tag == "main" for tag, _ in parser.tags), 1)
                self.assertEqual(sum(tag == "script" for tag, _ in parser.tags), 1)
                self.assertIn(build_site.THEME_SCRIPT, text)
                self.assertIn(build_site.THEME_CSS, text)
                self.assertIn('href="#content"', text)
                for tag, attrs in parser.tags:
                    if tag == "html":
                        expected = "fr" if "fr" in path.relative_to(ROOT).parts else "en"
                        self.assertEqual(attrs.get("lang"), expected)
                    self.assertNotIn(tag, ("iframe", "form", "img", "video", "audio"))
                    self.assertNotIn("src", attrs)
                    if tag == "link":
                        self.assertEqual(attrs.get("rel"), "canonical")

    def test_published_text_has_no_editorial_markers(self):
        for path in ROOT.rglob("*.html"):
            text = path.read_text(encoding="utf-8")
            for marker in ("TO BE SET", "À FIXER", "OWNER TO CONFIRM", "NOT PUBLISHED",
                           "Editorial references", "planned to use GitHub", "prévu sur GitHub"):
                self.assertNotIn(marker, text)
        for language in ("en", "fr"):
            privacy = (ROOT / language / "privacy" / "index.html").read_text(encoding="utf-8")
            self.assertIn("2026", privacy)
            self.assertIn("12", privacy)
            self.assertIn("pssoforge@e-nahum.net", privacy)
            self.assertIn("Google", privacy)
            self.assertIn("GitHub", privacy)
            self.assertIn("TestFlight", privacy)
            self.assertIn("crash", privacy)

    def test_renderer_escapes_text_and_rejects_unsafe_links(self):
        self.assertEqual(build_site.inline("<script>"), "&lt;script&gt;")
        with self.assertRaises(ValueError):
            build_site.inline("[unsafe](javascript:alert)")
        with self.assertRaises(ValueError):
            build_site.inline("[unsafe](//example.com)")
        with self.assertRaises(ValueError):
            build_site.markdown("```unsupported")

    def test_rebuild_is_idempotent(self):
        before = {path: path.read_bytes() for path in ROOT.rglob("*.html")}
        build_site.build()
        self.assertEqual(before, {path: path.read_bytes() for path in ROOT.rglob("*.html")})


if __name__ == "__main__":
    unittest.main()
