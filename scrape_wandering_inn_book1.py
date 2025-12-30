#!/usr/bin/env python3
"""Scrape The Wandering Inn Book 1 (rewritten) into EPUB and plain text."""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
import zipfile
from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Iterable, List, Optional

BASE_URL = "https://wanderinginn.com"
WP_API = f"{BASE_URL}/wp-json/wp/v2"
USER_AGENT = "Mozilla/5.0 (WanderingInnScraper/1.0; +https://wanderinginn.com/)"


@dataclass
class Chapter:
    order: int
    title: str
    link: str
    content_html: str


class HTMLTextExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: List[str] = []
        self._last_was_newline = False

    def handle_starttag(self, tag: str, attrs) -> None:
        if tag in {"p", "br", "div", "h1", "h2", "h3", "h4", "li", "blockquote"}:
            self._newline()

    def handle_endtag(self, tag: str) -> None:
        if tag in {"p", "div", "h1", "h2", "h3", "h4", "li", "blockquote"}:
            self._newline()

    def handle_data(self, data: str) -> None:
        text = html.unescape(data)
        if text.strip():
            if self._last_was_newline:
                self.parts.append(text.strip())
            else:
                self.parts.append(text)
            self._last_was_newline = False

    def _newline(self) -> None:
        if not self._last_was_newline:
            self.parts.append("\n")
            self._last_was_newline = True

    def get_text(self) -> str:
        text = "".join(self.parts)
        text = re.sub(r"\n\s+", "\n", text)
        return text.strip() + "\n"


def fetch_json(url: str, delay_s: float) -> dict | list:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req) as response:
        payload = json.loads(response.read().decode("utf-8"))
    time.sleep(delay_s)
    return payload


def fetch_posts(search_term: str, delay_s: float) -> List[dict]:
    posts: List[dict] = []
    page = 1
    while True:
        params = {
            "search": search_term,
            "per_page": 100,
            "page": page,
        }
        url = f"{WP_API}/posts?{urllib.parse.urlencode(params)}"
        try:
            batch = fetch_json(url, delay_s)
        except urllib.error.HTTPError as exc:
            if exc.code == 400:
                break
            raise
        if not batch:
            break
        posts.extend(batch)
        page += 1
    return posts


def strip_scripts(html_content: str) -> str:
    html_content = re.sub(r"<script.*?>.*?</script>", "", html_content, flags=re.S)
    html_content = re.sub(r"<style.*?>.*?</style>", "", html_content, flags=re.S)
    return html_content


def parse_chapters(posts: Iterable[dict]) -> List[Chapter]:
    chapters: List[Chapter] = []
    for post in posts:
        slug = post.get("slug", "")
        match = re.match(r"^rw1-(\d+)$", slug)
        if match:
            order = int(match.group(1))
        elif slug == "vol1-foreword":
            order = -1
        else:
            continue

        title = html.unescape(post.get("title", {}).get("rendered", "Untitled"))
        link = post.get("link", "")
        content = strip_scripts(post.get("content", {}).get("rendered", ""))
        chapters.append(
            Chapter(
                order=order,
                title=title,
                link=link,
                content_html=content,
            )
        )
    chapters.sort(key=lambda ch: ch.order)
    return chapters


def html_to_text(html_content: str) -> str:
    parser = HTMLTextExtractor()
    parser.feed(html_content)
    return parser.get_text()


def build_plain_text(chapters: List[Chapter]) -> str:
    parts = []
    for chapter in chapters:
        header = f"{chapter.title}\n{chapter.link}\n"
        body = html_to_text(chapter.content_html)
        parts.append("\n".join([header, body]).strip())
        parts.append("\n" + ("-" * 80) + "\n")
    return "\n".join(parts).strip() + "\n"


def write_epub(chapters: List[Chapter], output_path: str, book_title: str) -> None:
    tmp_dir = os.path.join(os.path.dirname(output_path), "epub_tmp")
    oebps_dir = os.path.join(tmp_dir, "OEBPS")
    meta_inf = os.path.join(tmp_dir, "META-INF")
    os.makedirs(oebps_dir, exist_ok=True)
    os.makedirs(meta_inf, exist_ok=True)

    with open(os.path.join(tmp_dir, "mimetype"), "w", encoding="utf-8") as f:
        f.write("application/epub+zip")

    with open(os.path.join(meta_inf, "container.xml"), "w", encoding="utf-8") as f:
        f.write(
            """<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>
"""
        )

    manifest_items = []
    spine_items = []
    toc_nav_points = []

    for index, chapter in enumerate(chapters, start=1):
        filename = f"chapter-{index:03}.xhtml"
        filepath = os.path.join(oebps_dir, filename)
        body_html = chapter.content_html
        xhtml = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <title>{html.escape(chapter.title)}</title>
  <meta charset="utf-8" />
</head>
<body>
  <h1>{html.escape(chapter.title)}</h1>
  <p><a href="{html.escape(chapter.link)}">{html.escape(chapter.link)}</a></p>
  {body_html}
</body>
</html>
"""
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(xhtml)

        manifest_items.append(
            f"<item id=\"chapter{index}\" href=\"{filename}\" media-type=\"application/xhtml+xml\"/>"
        )
        spine_items.append(f"<itemref idref=\"chapter{index}\"/>")
        toc_nav_points.append(
            f"""<navPoint id="navPoint-{index}" playOrder="{index}">
  <navLabel><text>{html.escape(chapter.title)}</text></navLabel>
  <content src="{filename}"/>
</navPoint>"""
        )

    now = dt.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    manifest_block = "\n    ".join(manifest_items)
    spine_block = "\n    ".join(spine_items)
    content_opf = f"""<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="BookId" version="2.0">
  <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
    <dc:title>{html.escape(book_title)}</dc:title>
    <dc:language>en</dc:language>
    <dc:identifier id="BookId">wandering-inn-book1-rewrite</dc:identifier>
    <dc:creator>The Wandering Inn</dc:creator>
    <dc:date>{now}</dc:date>
  </metadata>
  <manifest>
    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
    {manifest_block}
  </manifest>
  <spine toc="ncx">
    {spine_block}
  </spine>
</package>
"""
    with open(os.path.join(oebps_dir, "content.opf"), "w", encoding="utf-8") as f:
        f.write(content_opf)

    nav_block = "\n    ".join(toc_nav_points)
    toc_ncx = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN"
  "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
  <head>
    <meta name="dtb:uid" content="wandering-inn-book1-rewrite"/>
    <meta name="dtb:depth" content="1"/>
    <meta name="dtb:totalPageCount" content="0"/>
    <meta name="dtb:maxPageNumber" content="0"/>
  </head>
  <docTitle><text>{html.escape(book_title)}</text></docTitle>
  <navMap>
    {nav_block}
  </navMap>
</ncx>
"""
    with open(os.path.join(oebps_dir, "toc.ncx"), "w", encoding="utf-8") as f:
        f.write(toc_ncx)

    with zipfile.ZipFile(output_path, "w") as epub:
        epub.write(os.path.join(tmp_dir, "mimetype"), "mimetype", compress_type=zipfile.ZIP_STORED)
        for root, _, files in os.walk(tmp_dir):
            for name in files:
                if name == "mimetype":
                    continue
                full_path = os.path.join(root, name)
                rel_path = os.path.relpath(full_path, tmp_dir)
                epub.write(full_path, rel_path, compress_type=zipfile.ZIP_DEFLATED)

    for root, dirs, files in os.walk(tmp_dir, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    os.rmdir(tmp_dir)


def build_book(
    limit: Optional[int],
    delay_s: float,
    output_dir: str,
) -> None:
    posts = fetch_posts("rw1-", delay_s)
    posts.extend(fetch_posts("vol1-foreword", delay_s))

    chapters = parse_chapters(posts)
    if limit:
        chapters = chapters[:limit]
    print(f"Found {len(chapters)} chapters to process.")

    if not chapters:
        raise RuntimeError("No chapters found. The search query may need updating.")

    os.makedirs(output_dir, exist_ok=True)

    book_title = "The Wandering Inn - Book 1 (Rewritten)"
    text_output = os.path.join(output_dir, "wandering-inn-book1-rewrite.txt")
    epub_output = os.path.join(output_dir, "wandering-inn-book1-rewrite.epub")

    with open(text_output, "w", encoding="utf-8") as f:
        f.write(build_plain_text(chapters))

    write_epub(chapters, epub_output, book_title)

    print(f"Wrote {len(chapters)} chapters")
    print(f"Plain text: {text_output}")
    print(f"EPUB: {epub_output}")


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=None, help="Limit number of chapters for test runs")
    parser.add_argument("--delay", type=float, default=0.5, help="Delay between requests in seconds")
    parser.add_argument("--output", default="output", help="Output directory")
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    build_book(args.limit, args.delay, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
