#!/usr/bin/env python3
"""Static and optional live checks for the site's agent-facing contracts."""

from __future__ import annotations

import json
import os
import re
import unittest
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse


ROOT = Path(__file__).resolve().parents[1]
CANONICAL_ORIGIN = "https://jamesoncodes.github.io"
SITEMAP_NAMESPACE = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}


class DocumentParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.anchors: list[dict[str, str]] = []
        self.links: list[dict[str, str]] = []
        self.metas: list[dict[str, str]] = []
        self.headings: list[tuple[str, str]] = []
        self.json_ld: list[str] = []
        self._heading_tag: str | None = None
        self._heading_text: list[str] = []
        self._json_ld_script = False
        self._script_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {key: value or "" for key, value in attrs}
        if tag == "a":
            self.anchors.append(attributes)
        elif tag == "link":
            self.links.append(attributes)
        elif tag == "meta":
            self.metas.append(attributes)
        elif tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self._heading_tag = tag
            self._heading_text = []
        elif tag == "script" and attributes.get("type") == "application/ld+json":
            self._json_ld_script = True
            self._script_text = []

    def handle_endtag(self, tag: str) -> None:
        if tag == self._heading_tag:
            self.headings.append((tag, "".join(self._heading_text).strip()))
            self._heading_tag = None
            self._heading_text = []
        elif tag == "script" and self._json_ld_script:
            self.json_ld.append("".join(self._script_text).strip())
            self._json_ld_script = False
            self._script_text = []

    def handle_data(self, data: str) -> None:
        if self._heading_tag:
            self._heading_text.append(data)
        if self._json_ld_script:
            self._script_text.append(data)


def parse_html(path: Path) -> DocumentParser:
    parser = DocumentParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser


def sitemap_urls() -> list[str]:
    root = ET.parse(ROOT / "sitemap.xml").getroot()
    return [node.text or "" for node in root.findall("sm:url/sm:loc", SITEMAP_NAMESPACE)]


class StaticAgentReadinessTests(unittest.TestCase):
    def test_custom_404_has_machine_recovery_contract(self) -> None:
        source = (ROOT / "404.html").read_text(encoding="utf-8")
        parser = parse_html(ROOT / "404.html")
        robots = next(meta["content"] for meta in parser.metas if meta.get("name") == "robots")
        self.assertEqual(robots.replace(" ", "").lower(), "noindex,follow")
        self.assertIn(("h1", "This path doesn’t exist."), parser.headings)

        hrefs = {anchor.get("href") for anchor in parser.anchors}
        self.assertTrue({"/", "/llm.html", "/llms.txt", "/sitemap.xml"}.issubset(hrefs))

        describedby = [
            link for link in parser.links
            if link.get("rel") == "describedby" and link.get("type") == "text/markdown"
        ]
        self.assertEqual(len(describedby), 1)
        self.assertEqual(describedby[0].get("href"), f"{CANONICAL_ORIGIN}/llms.txt")
        self.assertIn("width: min(calc(100% - 3rem), 72rem);", source)
        self.assertRegex(source, r"\.error-card\s*\{\s*width: 100%;")
        self.assertIn("# 404: Resource not found", source)
        self.assertIn("- [Site index](https://jamesoncodes.github.io/llm.html)", source)
        self.assertIn("- [Agent instructions](https://jamesoncodes.github.io/llms.txt)", source)
        self.assertIn("- [XML sitemap](https://jamesoncodes.github.io/sitemap.xml)", source)

    def test_llms_txt_follows_v2_shape_and_contains_actionable_guidance(self) -> None:
        content = (ROOT / "llms.txt").read_text(encoding="utf-8")
        lines = content.splitlines()
        self.assertEqual(lines[0], "# Jameson Campbell")
        self.assertTrue(next(line for line in lines[1:] if line.strip()).startswith("> "))
        self.assertEqual(sum(line.startswith("# ") for line in lines), 1)
        self.assertNotRegex(content, r"(?m)^[-=]{3,}$")

        h2_indexes = [index for index, line in enumerate(lines) if line.startswith("## ")]
        self.assertGreaterEqual(len(h2_indexes), 1)
        for section_number, start in enumerate(h2_indexes):
            end = h2_indexes[section_number + 1] if section_number + 1 < len(h2_indexes) else len(lines)
            entries = [line for line in lines[start + 1:end] if line.strip()]
            self.assertTrue(entries, f"{lines[start]} must contain at least one link")
            self.assertTrue(
                all(re.match(r"^- \[[^]]+\]\(https://[^)]+\)(?:: .+)?$", line) for line in entries),
                f"{lines[start]} must contain only markdown link-list items",
            )

        lower_content = content.lower()
        self.assertIn("when to use this site", lower_content)
        for phrase in ("workflow friction", "gtm", "revops", "internal tools", "automations", "agents"):
            self.assertIn(phrase, lower_content)
        self.assertIn("first obtain their approval", lower_content)
        self.assertIn("cite the specific page", lower_content)

    def test_retired_ai_model_advisor_is_not_published(self) -> None:
        references = []
        for path in (ROOT / "llm.html", ROOT / "llms.txt", ROOT / "sitemap.xml"):
            if "ai-model-advisor" in path.read_text(encoding="utf-8").lower():
                references.append(path.name)
        self.assertEqual(references, [])
        self.assertFalse((ROOT / "ai-model-advisor").exists())

    def test_llms_public_page_links_are_in_the_sitemap(self) -> None:
        content = (ROOT / "llms.txt").read_text(encoding="utf-8")
        links = re.findall(r"\[[^]]+\]\((https://[^)]+)\)", content)
        indexed = set(sitemap_urls())
        allowed_discovery_files = {f"{CANONICAL_ORIGIN}/robots.txt", f"{CANONICAL_ORIGIN}/sitemap.xml"}
        for link in links:
            parsed = urlparse(link)
            without_fragment = parsed._replace(fragment="").geturl()
            self.assertIn(without_fragment, indexed | allowed_discovery_files)

    def test_homepage_has_consistent_brand_identity(self) -> None:
        parser = parse_html(ROOT / "index.html")
        site_name = next(meta["content"] for meta in parser.metas if meta.get("property") == "og:site_name")
        self.assertEqual(site_name, "Jameson Campbell")
        self.assertIn(("h2", "About Jameson Campbell"), parser.headings)

        describedby = [link for link in parser.links if link.get("rel") == "describedby"]
        self.assertEqual(describedby[0].get("type"), "text/markdown")
        self.assertEqual(describedby[0].get("href"), f"{CANONICAL_ORIGIN}/llms.txt")

        graph = json.loads(parser.json_ld[0])["@graph"]
        entities = {entity["@type"]: entity for entity in graph}
        website = entities["WebSite"]
        person = entities["Person"]
        profile = entities["ProfilePage"]
        self.assertEqual(website["name"], "Jameson Campbell")
        self.assertEqual(website["alternateName"], "JamesonCodes")
        self.assertEqual(website["url"], f"{CANONICAL_ORIGIN}/")
        self.assertEqual(person["@id"], f"{CANONICAL_ORIGIN}/#person")
        self.assertEqual(profile["mainEntity"]["@id"], person["@id"])
        self.assertEqual(len(person["sameAs"]), 3)

        me_links = [anchor for anchor in parser.anchors if "me" in anchor.get("rel", "").split()]
        self.assertEqual({link["href"] for link in me_links}, set(person["sameAs"]))

    def test_llm_html_uses_homepage_design_system(self) -> None:
        source = (ROOT / "llm.html").read_text(encoding="utf-8")
        styles = (ROOT / "styles.css").read_text(encoding="utf-8")
        parser = parse_html(ROOT / "llm.html")

        for marker in (
            "content-index-page",
            "content-index-hero",
            "font-display",
            "Bricolage+Grotesque",
            "geist-sans.css",
            "geist-mono.css",
            "styles.css?v=20260825-content-index",
        ):
            self.assertIn(marker, source)
        self.assertNotIn("#2E9DFB", source)
        self.assertIn(".content-index-page", styles)
        self.assertIn(".content-index-card-grid", styles)

        hrefs = {anchor.get("href") for anchor in parser.anchors}
        self.assertIn("index.html#ai-arsenal", hrefs)
        self.assertIn("workflow-friction-audit.html", hrefs)

    def test_sitemap_and_robots_reference_real_public_files(self) -> None:
        urls = sitemap_urls()
        self.assertEqual(len(urls), len(set(urls)))
        self.assertNotIn(f"{CANONICAL_ORIGIN}/404.html", urls)

        for url in urls:
            parsed = urlparse(url)
            self.assertEqual(f"{parsed.scheme}://{parsed.netloc}", CANONICAL_ORIGIN)
            relative_path = parsed.path.lstrip("/")
            local_path = ROOT / relative_path
            if not relative_path or parsed.path.endswith("/"):
                local_path = local_path / "index.html"
            self.assertTrue(local_path.is_file(), f"Sitemap target does not exist locally: {url}")

        robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
        self.assertIn(f"Sitemap: {CANONICAL_ORIGIN}/sitemap.xml", robots)
        ET.parse(ROOT / "sitemap.xml")


@unittest.skipUnless(os.environ.get("LIVE_SITE_URL"), "Set LIVE_SITE_URL to run deployed endpoint checks")
class LiveAgentReadinessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.origin = os.environ["LIVE_SITE_URL"].rstrip("/")

    def fetch(self, url: str) -> tuple[int, str, str]:
        request = urllib.request.Request(url, headers={"User-Agent": "JamesonCodes-agent-readiness-test/1.0"})
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                return response.status, response.headers.get_content_type(), response.read().decode("utf-8")
        except urllib.error.HTTPError as error:
            return error.code, error.headers.get_content_type(), error.read().decode("utf-8")

    def test_every_published_endpoint(self) -> None:
        expected_machine_types = {
            "/llms.txt": "text/plain",
            "/robots.txt": "text/plain",
            "/sitemap.xml": "application/xml",
        }
        paths = {urlparse(url).path for url in sitemap_urls()} | {"/robots.txt", "/sitemap.xml", "/llms.txt"}
        for path in sorted(paths):
            with self.subTest(path=path):
                status, content_type, _ = self.fetch(urljoin(f"{self.origin}/", path.lstrip("/")))
                self.assertEqual(status, 200)
                self.assertEqual(content_type, expected_machine_types.get(path, "text/html"))

    def test_missing_path_returns_recoverable_404(self) -> None:
        status, content_type, body = self.fetch(f"{self.origin}/agent-readiness-deployment-20260825-not-found")
        self.assertEqual(status, 404)
        self.assertEqual(content_type, "text/html")
        self.assertIn("This path doesn’t exist.", body)
        for path in ("/llm.html", "/llms.txt", "/sitemap.xml"):
            self.assertIn(f'href="{path}"', body)

    def test_retired_ai_model_advisor_returns_404(self) -> None:
        status, content_type, body = self.fetch(f"{self.origin}/ai-model-advisor/")
        self.assertEqual(status, 404)
        self.assertEqual(content_type, "text/html")
        self.assertIn("This path doesn’t exist.", body)


if __name__ == "__main__":
    unittest.main(verbosity=2)
