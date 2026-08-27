#!/usr/bin/env python3
"""Static and optional live checks for the site's agent-facing contracts."""

from __future__ import annotations

import json
import os
import re
import struct
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
AI_EMAIL_ARTICLE_PATH = ROOT / "articles" / "ai-native-email-system.html"
AI_EMAIL_ARTICLE_URL = f"{CANONICAL_ORIGIN}/articles/ai-native-email-system.html"
AI_EMAIL_ARTICLE_TITLE = "Building an AI-Native Email System, One Job at a Time"
AI_EMAIL_ARTICLE_DESCRIPTION = (
    "How I'm building an AI-native email system at Sock Club using job-based workflows, "
    "shadow mode, human review, and evaluation datasets."
)
AI_EMAIL_ARTICLE_DATE = "2026-08-27"
AI_EMAIL_IMAGE_URL = f"{CANONICAL_ORIGIN}/assets/og/ai-native-email-system-og-v2.png"


class DocumentParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.anchors: list[dict[str, str]] = []
        self.links: list[dict[str, str]] = []
        self.metas: list[dict[str, str]] = []
        self.headings: list[tuple[str, str]] = []
        self.json_ld: list[str] = []
        self.title = ""
        self._heading_tag: str | None = None
        self._heading_text: list[str] = []
        self._json_ld_script = False
        self._script_text: list[str] = []
        self._title_tag = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {key: value or "" for key, value in attrs}
        if tag == "a":
            self.anchors.append(attributes)
        elif tag == "link":
            self.links.append(attributes)
        elif tag == "meta":
            self.metas.append(attributes)
        elif tag == "title":
            self._title_tag = True
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
        elif tag == "title":
            self._title_tag = False
        elif tag == "script" and self._json_ld_script:
            self.json_ld.append("".join(self._script_text).strip())
            self._json_ld_script = False
            self._script_text = []

    def handle_data(self, data: str) -> None:
        if self._heading_tag:
            self._heading_text.append(data)
        if self._title_tag:
            self.title += data
        if self._json_ld_script:
            self._script_text.append(data)


def parse_html(path: Path) -> DocumentParser:
    parser = DocumentParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser


def sitemap_urls() -> list[str]:
    root = ET.parse(ROOT / "sitemap.xml").getroot()
    return [node.text or "" for node in root.findall("sm:url/sm:loc", SITEMAP_NAMESPACE)]


def sitemap_entries() -> dict[str, str]:
    root = ET.parse(ROOT / "sitemap.xml").getroot()
    entries: dict[str, str] = {}
    for node in root.findall("sm:url", SITEMAP_NAMESPACE):
        location = node.findtext("sm:loc", default="", namespaces=SITEMAP_NAMESPACE)
        last_modified = node.findtext("sm:lastmod", default="", namespaces=SITEMAP_NAMESPACE)
        entries[location] = last_modified
    return entries


class StaticAgentReadinessTests(unittest.TestCase):
    def test_ai_email_article_has_consistent_seo_metadata_and_schema(self) -> None:
        parser = parse_html(AI_EMAIL_ARTICLE_PATH)
        source = AI_EMAIL_ARTICLE_PATH.read_text(encoding="utf-8")

        self.assertEqual(parser.title.strip(), AI_EMAIL_ARTICLE_TITLE)
        self.assertEqual(
            [heading for tag, heading in parser.headings if tag == "h1"],
            [AI_EMAIL_ARTICLE_TITLE],
        )

        canonical = [link for link in parser.links if link.get("rel") == "canonical"]
        self.assertEqual(canonical, [{"rel": "canonical", "href": AI_EMAIL_ARTICLE_URL}])
        describedby = [link for link in parser.links if link.get("rel") == "describedby"]
        self.assertEqual(
            describedby,
            [{"rel": "describedby", "href": f"{CANONICAL_ORIGIN}/llms.txt", "type": "text/markdown"}],
        )

        meta_by_name = {meta["name"]: meta["content"] for meta in parser.metas if meta.get("name")}
        meta_by_property = {
            meta["property"]: meta["content"] for meta in parser.metas if meta.get("property")
        }
        for value in (
            meta_by_name["description"],
            meta_by_name["twitter:description"],
            meta_by_property["og:description"],
        ):
            self.assertEqual(value, AI_EMAIL_ARTICLE_DESCRIPTION)
        self.assertEqual(meta_by_property["og:site_name"], "Jameson Campbell")
        self.assertEqual(meta_by_property["og:locale"], "en_US")
        self.assertEqual(meta_by_property["og:image"], AI_EMAIL_IMAGE_URL)
        self.assertEqual(meta_by_name["twitter:image"], AI_EMAIL_IMAGE_URL)
        self.assertEqual(meta_by_name["twitter:image:alt"], meta_by_property["og:image:alt"])
        robots_directives = {item.strip() for item in meta_by_name["robots"].lower().split(",")}
        self.assertEqual(robots_directives, {"index", "follow", "max-image-preview:large"})

        schemas = [json.loads(block) for block in parser.json_ld]
        article = next(schema for schema in schemas if schema.get("@type") == "BlogPosting")
        breadcrumb = next(schema for schema in schemas if schema.get("@type") == "BreadcrumbList")
        self.assertEqual(article["@id"], f"{AI_EMAIL_ARTICLE_URL}#article")
        self.assertEqual(article["url"], AI_EMAIL_ARTICLE_URL)
        self.assertEqual(article["headline"], AI_EMAIL_ARTICLE_TITLE)
        self.assertEqual(article["description"], AI_EMAIL_ARTICLE_DESCRIPTION)
        self.assertEqual(article["datePublished"][:10], AI_EMAIL_ARTICLE_DATE)
        self.assertEqual(article["dateModified"][:10], AI_EMAIL_ARTICLE_DATE)
        self.assertEqual(article["inLanguage"], "en-US")
        self.assertEqual(article["isPartOf"]["@id"], f"{CANONICAL_ORIGIN}/#website")
        self.assertEqual(article["author"]["@id"], f"{CANONICAL_ORIGIN}/#person")
        self.assertEqual(article["publisher"]["@id"], f"{CANONICAL_ORIGIN}/#person")
        self.assertEqual(article["mainEntityOfPage"]["@id"], AI_EMAIL_ARTICLE_URL)
        self.assertEqual(
            article["image"],
            {"@type": "ImageObject", "url": AI_EMAIL_IMAGE_URL, "width": 1200, "height": 630},
        )
        self.assertEqual(len(breadcrumb["itemListElement"]), 3)
        self.assertIn(
            f'<time datetime="{AI_EMAIL_ARTICLE_DATE}">August 27, 2026</time>',
            source,
        )

    def test_ai_email_article_preserves_launch_content_and_image_contract(self) -> None:
        source = AI_EMAIL_ARTICLE_PATH.read_text(encoding="utf-8")
        image_path = ROOT / "assets" / "og" / "ai-native-email-system-og-v2.png"
        image_header = image_path.read_bytes()[:24]

        self.assertTrue(image_path.is_file())
        self.assertEqual(image_header[:8], b"\x89PNG\r\n\x1a\n")
        self.assertEqual(struct.unpack(">II", image_header[16:24]), (1200, 630))
        self.assertIn("500+", source)
        self.assertNotIn("400+", source)
        self.assertNotIn("—", source)
        self.assertIn('href="https://custom.sockclub.com/"', source)
        self.assertIn('href="../workflow-friction-audit.html"', source)

    def test_ai_email_article_is_synchronized_across_discovery_surfaces(self) -> None:
        homepage = (ROOT / "index.html").read_text(encoding="utf-8")
        internal_tools = (ROOT / "articles" / "internal-tools-builder.html").read_text(encoding="utf-8")
        llm_html = (ROOT / "llm.html").read_text(encoding="utf-8")
        llms_txt = (ROOT / "llms.txt").read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        sitemap = sitemap_entries()

        self.assertIn('href="articles/ai-native-email-system.html"', homepage)
        self.assertIn("human-reviewed evaluations", homepage)
        self.assertIn('href="ai-native-email-system.html"', internal_tools)
        self.assertGreaterEqual(llm_html.count('/articles/ai-native-email-system.html'), 2)
        for phrase in ("500+", "24-second median", "human-reviewed evaluation datasets"):
            self.assertIn(phrase, llm_html)
        for phrase in ("500+ submissions", "human-reviewed evaluations", "earned autonomy"):
            self.assertIn(phrase, llms_txt)
        for phrase in ("500+ submissions", "24-second median", "evaluation datasets"):
            self.assertIn(phrase, readme)
        self.assertEqual(sitemap[AI_EMAIL_ARTICLE_URL], AI_EMAIL_ARTICLE_DATE)
        for url in (
            f"{CANONICAL_ORIGIN}/",
            f"{CANONICAL_ORIGIN}/llm.html",
            f"{CANONICAL_ORIGIN}/llms.txt",
        ):
            self.assertEqual(sitemap[url], AI_EMAIL_ARTICLE_DATE)

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
        self.assertIn(("h2", "About Me"), parser.headings)

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

    def test_ai_email_article_deploys_with_its_canonical_contract(self) -> None:
        status, content_type, body = self.fetch(f"{self.origin}/articles/ai-native-email-system.html")
        parser = DocumentParser()
        parser.feed(body)

        self.assertEqual(status, 200)
        self.assertEqual(content_type, "text/html")
        canonical = [link for link in parser.links if link.get("rel") == "canonical"]
        self.assertEqual(canonical[0].get("href"), AI_EMAIL_ARTICLE_URL)
        self.assertIn("500+", body)

    def test_ai_email_social_preview_image_is_public(self) -> None:
        request = urllib.request.Request(
            f"{self.origin}/assets/og/ai-native-email-system-og-v2.png",
            headers={"User-Agent": "JamesonCodes-agent-readiness-test/1.0"},
        )
        with urllib.request.urlopen(request, timeout=20) as response:
            image_header = response.read(24)
            self.assertEqual(response.status, 200)
            self.assertEqual(response.headers.get_content_type(), "image/png")
            self.assertEqual(image_header[:8], b"\x89PNG\r\n\x1a\n")
            self.assertEqual(struct.unpack(">II", image_header[16:24]), (1200, 630))

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
