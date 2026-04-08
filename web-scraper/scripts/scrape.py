#!/usr/bin/env python3
"""
Web Scraper - pobiera artykuły jako markdown z obrazkami i embedami.
Najpierw próbuje pobrać stronę bezpośrednio (direct fetch), a jeśli to się nie uda
(403, 429, timeout, pusta treść) — używa Firecrawl API jako fallback.

Użycie: python scrape.py <URL> [--output plik.md] [--format markdown|json] [--force-firecrawl]
"""

import argparse
import json
import os
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

def _load_config():
    """Load joe-config.json from ~/.claude/skills/."""
    config_path = Path.home() / ".claude" / "skills" / "joe-config.json"
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    return {}

FIRECRAWL_API_KEY = os.environ.get("FIRECRAWL_API_KEY") or _load_config().get("firecrawl_api_key", "")
FIRECRAWL_API_URL = "https://api.firecrawl.dev/v1/scrape"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
)

# Minimalna długość treści (w znakach) żeby uznać direct fetch za udany
MIN_CONTENT_LENGTH = 200


# ---------------------------------------------------------------------------
# HTML -> Markdown converter (lightweight, no dependencies)
# ---------------------------------------------------------------------------

class HTMLToMarkdown(HTMLParser):
    """Prosty konwerter HTML -> Markdown wystarczający do artykułów."""

    BLOCK_TAGS = {"p", "div", "section", "article", "main", "blockquote", "li", "tr", "br", "hr"}
    SKIP_TAGS = {"script", "style", "noscript", "nav", "footer", "header", "aside", "form", "button", "svg", "title"}
    HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}

    def __init__(self):
        super().__init__()
        self.result = []
        self.skip_depth = 0
        self.tag_stack = []
        self.current_link = None
        self.link_text = []
        self.images = []
        self.meta = {}
        self.in_title = False
        self.title_text = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)

        # Zbieramy meta tagi
        if tag == "meta":
            name = attrs_dict.get("name", attrs_dict.get("property", ""))
            content = attrs_dict.get("content", "")
            if name and content:
                self.meta[name] = content

        if tag == "title":
            self.in_title = True
            self.title_text = []

        if self.skip_depth > 0:
            if tag in self.SKIP_TAGS:
                self.skip_depth += 1
            return

        if tag in self.SKIP_TAGS:
            self.skip_depth += 1
            return

        self.tag_stack.append(tag)

        if tag in self.HEADING_TAGS:
            level = int(tag[1])
            self.result.append(f"\n\n{'#' * level} ")
        elif tag == "p":
            self.result.append("\n\n")
        elif tag == "br":
            self.result.append("\n")
        elif tag == "hr":
            self.result.append("\n\n---\n\n")
        elif tag == "li":
            self.result.append("\n- ")
        elif tag == "blockquote":
            self.result.append("\n\n> ")
        elif tag == "strong" or tag == "b":
            self.result.append("**")
        elif tag == "em" or tag == "i":
            self.result.append("*")
        elif tag == "a":
            href = attrs_dict.get("href", "")
            if href and not href.startswith(("#", "javascript:")):
                self.current_link = href
                self.link_text = []
        elif tag == "img":
            src = attrs_dict.get("src", attrs_dict.get("data-src", ""))
            alt = attrs_dict.get("alt", "")
            if src and not src.endswith(".svg"):
                self.result.append(f"\n![{alt}]({src})\n")
                self.images.append({"alt": alt, "url": src})

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
            if "title" not in self.meta:
                self.meta["title"] = "".join(self.title_text).strip()

        if self.skip_depth > 0:
            if tag in self.SKIP_TAGS:
                self.skip_depth -= 1
            return

        if tag in ("strong", "b"):
            self.result.append("**")
        elif tag in ("em", "i"):
            self.result.append("*")
        elif tag == "a" and self.current_link is not None:
            text = "".join(self.link_text).strip()
            if text:
                self.result.append(f"[{text}]({self.current_link})")
            self.current_link = None
            self.link_text = []
        elif tag in self.HEADING_TAGS:
            self.result.append("\n")

        if self.tag_stack and self.tag_stack[-1] == tag:
            self.tag_stack.pop()

    def handle_data(self, data):
        if self.in_title:
            self.title_text.append(data)

        if self.skip_depth > 0:
            return

        if self.current_link is not None:
            self.link_text.append(data)
        else:
            self.result.append(data)

    def get_markdown(self, article_mode: bool = False) -> str:
        text = "".join(self.result)
        # Normalizuj line endings
        text = text.replace('\r\n', '\n')
        # Zamień ciągi 2+ spacji/tabów na jedną spację (w obrębie linii)
        text = re.sub(r'[^\S\n]{2,}', ' ', text)
        # Usuń trailing whitespace z każdej linii
        text = re.sub(r'(?m)[ \t]+$', '', text)
        # Zamień 3+ nowych linii na 2
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = text.strip()
        if article_mode:
            # Utnij wszystko przed pierwszym h1
            h1_pos = text.find("\n# ")
            if h1_pos == -1:
                h1_pos = 0 if text.startswith("# ") else -1
            if h1_pos >= 0:
                text = text[h1_pos:].lstrip("\n")
        return text

    def get_metadata(self) -> dict:
        return {
            "title": self.meta.get("og:title", self.meta.get("title", "Bez tytułu")),
            "description": self.meta.get("og:description", self.meta.get("description", "")),
            "og_image": self.meta.get("og:image", ""),
            "author": self.meta.get("author", self.meta.get("article:author", "")),
            "published": self.meta.get("article:published_time", self.meta.get("publishedTime", "")),
            "source_url": self.meta.get("og:url", ""),
            "site_name": self.meta.get("og:site_name", ""),
        }


# ---------------------------------------------------------------------------
# HTML extraction helpers
# ---------------------------------------------------------------------------

def _extract_div_by_id(html: str, div_id: str) -> str | None:
    """Extract content of a div with given id from HTML. Returns inner HTML or None."""
    # Find opening tag with id
    pattern = re.compile(
        rf'<div[^>]*\bid=["\']?{re.escape(div_id)}["\']?[^>]*>',
        re.IGNORECASE | re.DOTALL,
    )
    match = pattern.search(html)
    if not match:
        return None

    start = match.start()
    pos = match.end()
    depth = 1

    while depth > 0 and pos < len(html):
        open_match = re.search(r'<div[\s>]', html[pos:], re.IGNORECASE)
        close_match = re.search(r'</div\s*>', html[pos:], re.IGNORECASE)

        if close_match is None:
            break

        if open_match and open_match.start() < close_match.start():
            depth += 1
            pos += open_match.end()
        else:
            depth -= 1
            if depth == 0:
                end = pos + close_match.end()
                return html[start:end]
            pos += close_match.end()

    return None


# ---------------------------------------------------------------------------
# Direct fetch (bez Firecrawl)
# ---------------------------------------------------------------------------

def direct_fetch(url: str, article_mode: bool = False) -> dict | None:
    """Próbuje pobrać stronę bezpośrednio. Zwraca dict kompatybilny z Firecrawl lub None."""
    req = Request(url, headers={"User-Agent": USER_AGENT})

    try:
        with urlopen(req, timeout=15) as resp:
            # Obsługa redirectów
            content_type = resp.headers.get("Content-Type", "")
            if "text/html" not in content_type and "application/xhtml" not in content_type:
                print(f"[direct] Pominięto — Content-Type: {content_type}", file=sys.stderr)
                return None

            charset = "utf-8"
            if "charset=" in content_type:
                charset = content_type.split("charset=")[-1].split(";")[0].strip()

            raw = resp.read()
            html = raw.decode(charset, errors="replace")

    except HTTPError as e:
        print(f"[direct] HTTP {e.code} — przechodzę na Firecrawl", file=sys.stderr)
        return None
    except (URLError, TimeoutError, OSError) as e:
        print(f"[direct] Błąd: {e} — przechodzę na Firecrawl", file=sys.stderr)
        return None

    # JoeMonster /art/ — wyciągnij treść z div#arcik, metadane z pełnego HTML
    article_html = html
    if re.search(r'joemonster\.org/art/\d+', url):
        extracted = _extract_div_by_id(html, "arcik")
        if extracted:
            article_html = extracted
            print(f"[direct] JoeMonster /art/ — użyto div#arcik", file=sys.stderr)

    # Parsuj metadane z pełnego HTML
    meta_parser = HTMLToMarkdown()
    try:
        meta_parser.feed(html)
    except Exception:
        pass

    # Parsuj treść z artykułu (może być div#arcik lub pełny HTML)
    parser = HTMLToMarkdown()
    try:
        parser.feed(article_html)
    except Exception as e:
        print(f"[direct] Błąd parsowania HTML: {e} — przechodzę na Firecrawl", file=sys.stderr)
        return None

    # Użyj metadanych z pełnego HTML, treści z artykułu
    parser.meta = {**parser.meta, **meta_parser.meta}

    markdown = parser.get_markdown(article_mode=article_mode)

    if len(markdown) < MIN_CONTENT_LENGTH:
        print(f"[direct] Za mało treści ({len(markdown)} znaków) — przechodzę na Firecrawl", file=sys.stderr)
        return None

    meta = parser.get_metadata()
    if not meta["source_url"]:
        meta["source_url"] = url

    print(f"[direct] Pobrano {len(markdown)} znaków", file=sys.stderr)

    # Zwracamy format kompatybilny z odpowiedzią Firecrawl
    return {
        "success": True,
        "source": "direct",
        "data": {
            "markdown": markdown,
            "metadata": {
                "title": meta["title"],
                "og:title": meta["title"],
                "description": meta["description"],
                "og:description": meta["description"],
                "og:image": meta["og_image"],
                "author": meta["author"],
                "article:published_time": meta["published"],
                "sourceURL": meta["source_url"],
                "og:site_name": meta["site_name"],
            },
        },
    }


# ---------------------------------------------------------------------------
# Firecrawl fetch (fallback)
# ---------------------------------------------------------------------------

def scrape_url(url: str, formats: list[str] = None) -> dict:
    """Wywołuje Firecrawl API i zwraca wynik."""
    if not FIRECRAWL_API_KEY:
        print("ERROR: No Firecrawl API key. Set FIRECRAWL_API_KEY environment variable.", file=sys.stderr)
        sys.exit(1)

    if formats is None:
        formats = ["markdown"]

    payload = json.dumps({
        "url": url,
        "formats": formats,
        "onlyMainContent": True,
        "includeTags": ["article", "main", ".post-content", ".article-body", ".entry-content"],
        "waitFor": 3000,
    }).encode("utf-8")

    req = Request(
        FIRECRAWL_API_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {FIRECRAWL_API_KEY}",
        },
        method="POST",
    )

    try:
        with urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            data["source"] = "firecrawl"
            return data
    except HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        print(f"[firecrawl] Błąd HTTP {e.code}: {body}", file=sys.stderr)
        sys.exit(1)
    except URLError as e:
        print(f"[firecrawl] Błąd połączenia: {e.reason}", file=sys.stderr)
        sys.exit(1)


# ---------------------------------------------------------------------------
# Ekstrakcja danych
# ---------------------------------------------------------------------------

def extract_metadata(data: dict) -> dict:
    """Wyciąga metadane z odpowiedzi."""
    meta = data.get("data", {}).get("metadata", {})
    return {
        "title": meta.get("title", meta.get("og:title", "Bez tytułu")),
        "description": meta.get("description", meta.get("og:description", "")),
        "og_image": meta.get("og:image", ""),
        "author": meta.get("author", ""),
        "published": meta.get("publishedTime", meta.get("article:published_time", "")),
        "source_url": meta.get("sourceURL", meta.get("url", "")),
        "site_name": meta.get("og:site_name", ""),
    }


def extract_social_embeds(markdown: str) -> list[dict]:
    """Znajduje linki do postów X/Twitter i Facebook w markdown."""
    embeds = []

    x_patterns = [
        r'https?://(?:twitter\.com|x\.com)/\w+/status/\d+[^\s\)]*',
    ]
    for pattern in x_patterns:
        for match in re.finditer(pattern, markdown):
            embeds.append({"type": "x/twitter", "url": match.group(0).rstrip(')')})

    fb_patterns = [
        r'https?://(?:www\.)?facebook\.com/[^\s\)]+/posts/[^\s\)]+',
        r'https?://(?:www\.)?facebook\.com/permalink\.php\?[^\s\)]+',
        r'https?://(?:www\.)?facebook\.com/watch/?\?[^\s\)]+',
        r'https?://fb\.watch/[^\s\)]+',
    ]
    for pattern in fb_patterns:
        for match in re.finditer(pattern, markdown):
            embeds.append({"type": "facebook", "url": match.group(0).rstrip(')')})

    ig_patterns = [
        r'https?://(?:www\.)?instagram\.com/p/[^\s\)]+',
        r'https?://(?:www\.)?instagram\.com/reel/[^\s\)]+',
    ]
    for pattern in ig_patterns:
        for match in re.finditer(pattern, markdown):
            embeds.append({"type": "instagram", "url": match.group(0).rstrip(')')})

    yt_patterns = [
        r'https?://(?:www\.)?youtube\.com/watch\?[^\s\)]+',
        r'https?://youtu\.be/[^\s\)]+',
    ]
    for pattern in yt_patterns:
        for match in re.finditer(pattern, markdown):
            embeds.append({"type": "youtube", "url": match.group(0).rstrip(')')})

    seen = set()
    unique = []
    for e in embeds:
        if e["url"] not in seen:
            seen.add(e["url"])
            unique.append(e)

    return unique


def extract_images(markdown: str) -> list[dict]:
    """Wyciąga obrazki z markdown wraz z podpisami (alt text)."""
    images = []
    for match in re.finditer(r'!\[([^\]]*)\]\(([^)]+)\)', markdown):
        alt = match.group(1).strip()
        url = match.group(2).strip()
        if url and not url.endswith(('.svg', '.gif')) and 'logo' not in url.lower() and 'icon' not in url.lower():
            images.append({"alt": alt, "url": url})
    return images


# ---------------------------------------------------------------------------
# Formatowanie wyjścia
# ---------------------------------------------------------------------------

def format_output(url: str, data: dict, output_format: str = "markdown") -> str:
    """Formatuje wynik do markdown lub JSON."""
    markdown_content = data.get("data", {}).get("markdown", "")
    meta = extract_metadata(data)
    images = extract_images(markdown_content)
    embeds = extract_social_embeds(markdown_content)
    source = data.get("source", "unknown")

    if output_format == "json":
        return json.dumps({
            "metadata": meta,
            "source": source,
            "content": markdown_content,
            "images": images,
            "social_embeds": embeds,
        }, ensure_ascii=False, indent=2)

    # Format markdown
    parts = []

    parts.append(f"# {meta['title']}\n")

    if meta["author"]:
        parts.append(f"**Autor:** {meta['author']}")
    if meta["published"]:
        parts.append(f"**Data publikacji:** {meta['published']}")
    if meta["site_name"]:
        parts.append(f"**Źródło:** {meta['site_name']}")
    parts.append(f"**URL:** {url}")
    parts.append(f"**Metoda:** {'direct fetch' if source == 'direct' else 'Firecrawl API'}")

    if meta["og_image"]:
        parts.append(f"\n**Obraz główny:**\n![{meta['title']}]({meta['og_image']})")

    parts.append("\n---\n")
    parts.append(markdown_content)

    if images:
        parts.append("\n---\n## Obrazki w artykule\n")
        for i, img in enumerate(images, 1):
            caption = img["alt"] if img["alt"] else f"Obrazek {i}"
            parts.append(f"{i}. **{caption}**\n   {img['url']}\n")

    if embeds:
        parts.append("\n---\n## Embedy social media\n")
        for e in embeds:
            parts.append(f"- [{e['type']}] {e['url']}")

    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Web Scraper (direct fetch + Firecrawl fallback)")
    parser.add_argument("url", help="URL do zescrapowania")
    parser.add_argument("--output", "-o", help="Plik wyjściowy (opcjonalny)")
    parser.add_argument("--format", "-f", choices=["markdown", "json"], default="markdown",
                        help="Format wyjścia (domyślnie: markdown)")
    parser.add_argument("--force-firecrawl", action="store_true",
                        help="Pomiń direct fetch, od razu użyj Firecrawl")
    parser.add_argument("--article", action="store_true",
                        help="Tryb artykułu: utnij nawigację przed pierwszym <h1>")
    args = parser.parse_args()

    data = None

    # Krok 1: Direct fetch (chyba że wymuszono Firecrawl)
    if not args.force_firecrawl:
        print(f"[direct] Próbuję pobrać: {args.url}", file=sys.stderr)
        data = direct_fetch(args.url, article_mode=args.article)

    # Krok 2: Firecrawl jako fallback
    if data is None:
        print(f"[firecrawl] Pobieram: {args.url}", file=sys.stderr)
        data = scrape_url(args.url)

    if not data.get("success"):
        print(f"Błąd: {json.dumps(data, ensure_ascii=False)}", file=sys.stderr)
        sys.exit(1)

    result = format_output(args.url, data, args.format)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(result)
        print(f"Zapisano do: {args.output}", file=sys.stderr)
    else:
        print(result)


if __name__ == "__main__":
    main()
