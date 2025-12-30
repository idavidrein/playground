#!/usr/bin/env python3
import argparse
import dataclasses
import os
import re
import time
from typing import Iterable, List, Optional

import requests
from bs4 import BeautifulSoup
from ebooklib import epub


USER_AGENT = "WanderingInnBookDownloader/1.0 (+https://wanderinginn.com)"
DEFAULT_VOLUME_URL = "https://wanderinginn.com/volume-1/"


@dataclasses.dataclass
class ChapterLink:
    title: str
    url: str


def _soup_from_html(html: str) -> BeautifulSoup:
    return BeautifulSoup(html, "html.parser")


def fetch(url: str, session: requests.Session, timeout: int = 30) -> str:
    response = session.get(url, timeout=timeout)
    response.raise_for_status()
    return response.text


def extract_volume_links(html: str, chapter_prefix: str) -> List[ChapterLink]:
    soup = _soup_from_html(html)
    content = soup.select_one("article") or soup.select_one("main") or soup
    links: List[ChapterLink] = []
    chapter_regex = re.compile(rf"^{re.escape(chapter_prefix)}\d+", re.IGNORECASE)
    for anchor in content.select("a[href]"):
        href = anchor.get("href", "").strip()
        if not href.startswith("http"):
            continue
        if "wanderinginn.com" not in href:
            continue
        text = " ".join(anchor.get_text(" ", strip=True).split())
        if not text:
            continue
        if not chapter_regex.search(text):
            continue
        links.append(ChapterLink(title=text, url=href))
    seen = set()
    unique_links: List[ChapterLink] = []
    for link in links:
        if link.url in seen:
            continue
        seen.add(link.url)
        unique_links.append(link)
    return unique_links


def extract_chapter_body(html: str) -> tuple[str, str]:
    soup = _soup_from_html(html)
    title = soup.title.get_text(strip=True) if soup.title else "Untitled"
    article = soup.select_one("article") or soup.select_one("main") or soup
    content = article.select_one(".entry-content") or article
    for selector in ["script", "style", "nav", "header", "footer", ".sharedaddy"]:
        for node in content.select(selector):
            node.decompose()
    chapter_title = content.select_one("h1")
    if chapter_title:
        chapter_title_text = chapter_title.get_text(strip=True)
    else:
        chapter_title_text = title
    html_body = "".join(str(node) for node in content.contents)
    return chapter_title_text, html_body


def write_chapter_html(output_dir: str, chapter: ChapterLink, body_html: str) -> str:
    safe_title = re.sub(r"[^a-zA-Z0-9_-]+", "_", chapter.title).strip("_")
    filename = f"{safe_title}.html"
    path = os.path.join(output_dir, filename)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write("<!doctype html>\n")
        handle.write("<html lang=\"en\">\n<head>\n")
        handle.write("<meta charset=\"utf-8\">\n")
        handle.write(f"<title>{chapter.title}</title>\n")
        handle.write("</head>\n<body>\n")
        handle.write(f"<h1>{chapter.title}</h1>\n")
        handle.write(body_html)
        handle.write("\n</body>\n</html>\n")
    return filename


def build_epub(output_path: str, chapters: Iterable[tuple[ChapterLink, str]]) -> None:
    book = epub.EpubBook()
    book.set_identifier("wandering-inn-volume-1")
    book.set_title("The Wandering Inn - Volume 1")
    book.set_language("en")
    spine = ["nav"]
    toc = []
    for index, (chapter, body_html) in enumerate(chapters, start=1):
        file_name = f"chapter_{index:03d}.xhtml"
        content = f"<h1>{chapter.title}</h1>\n{body_html}"
        epub_chapter = epub.EpubHtml(
            title=chapter.title,
            file_name=file_name,
            lang="en",
            content=content,
        )
        book.add_item(epub_chapter)
        toc.append(epub_chapter)
        spine.append(epub_chapter)
    book.toc = toc
    book.spine = spine
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    epub.write_epub(output_path, book, {})


def scrape(
    volume_url: str,
    output_dir: str,
    chapter_prefix: str,
    max_chapters: Optional[int],
    delay_seconds: float,
    no_proxy: bool,
) -> None:
    os.makedirs(output_dir, exist_ok=True)
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    if no_proxy:
        session.trust_env = False
    volume_html = fetch(volume_url, session=session)
    links = extract_volume_links(volume_html, chapter_prefix=chapter_prefix)
    if max_chapters:
        links = links[:max_chapters]
    if not links:
        raise RuntimeError("No chapter links found. Check the volume URL or prefix.")
    chapter_entries: List[tuple[ChapterLink, str]] = []
    index_items = []
    for chapter in links:
        chapter_html = fetch(chapter.url, session=session)
        chapter_title, body_html = extract_chapter_body(chapter_html)
        chapter.title = chapter_title or chapter.title
        filename = write_chapter_html(output_dir, chapter, body_html)
        index_items.append(f"<li><a href=\"{filename}\">{chapter.title}</a></li>")
        chapter_entries.append((chapter, body_html))
        if delay_seconds:
            time.sleep(delay_seconds)
    index_path = os.path.join(output_dir, "index.html")
    with open(index_path, "w", encoding="utf-8") as handle:
        handle.write("<!doctype html>\n<html lang=\"en\">\n<head>\n")
        handle.write("<meta charset=\"utf-8\">\n")
        handle.write("<title>Wandering Inn - Volume 1</title>\n")
        handle.write("</head>\n<body>\n")
        handle.write("<h1>Wandering Inn - Volume 1</h1>\n")
        handle.write("<ol>\n")
        handle.write("\n".join(index_items))
        handle.write("\n</ol>\n</body>\n</html>\n")
    epub_path = os.path.join(output_dir, "wandering_inn_volume_1.epub")
    build_epub(epub_path, chapter_entries)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download Volume 1 of The Wandering Inn into HTML + EPUB."
    )
    parser.add_argument(
        "--volume-url",
        default=DEFAULT_VOLUME_URL,
        help="URL of the volume table-of-contents page.",
    )
    parser.add_argument(
        "--output-dir",
        default="wandering_inn_volume_1",
        help="Directory to store HTML chapters + EPUB.",
    )
    parser.add_argument(
        "--chapter-prefix",
        default="1.",
        help="Prefix used to identify chapter links on the volume page.",
    )
    parser.add_argument(
        "--max-chapters",
        type=int,
        default=None,
        help="Limit number of chapters to download (for test runs).",
    )
    parser.add_argument(
        "--delay-seconds",
        type=float,
        default=1.0,
        help="Delay between chapter downloads.",
    )
    parser.add_argument(
        "--no-proxy",
        action="store_true",
        help="Disable proxy environment variables for requests.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    scrape(
        volume_url=args.volume_url,
        output_dir=args.output_dir,
        chapter_prefix=args.chapter_prefix,
        max_chapters=args.max_chapters,
        delay_seconds=args.delay_seconds,
        no_proxy=args.no_proxy,
    )


if __name__ == "__main__":
    main()
