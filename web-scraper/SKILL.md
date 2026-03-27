---
name: web-scraper
description: "Scrapes web pages and articles to get clean markdown content, images with captions, and social media embeds (X/Twitter, Facebook, Instagram, YouTube). First tries direct fetch (free, fast), then falls back to Firecrawl API if the site blocks bots (403/429) or returns insufficient content. Use this skill whenever you need to fetch the content of a web page that returns 403/forbidden with normal fetch, when web_fetch fails or returns blocked content, when the user asks to scrape or download an article, when you need full article content with images and embeds, or when a site requires JavaScript rendering. Also trigger when the user says 'pobierz stronę', 'zescrapuj', 'scrape this', 'get the article from', or mentions Firecrawl."
---

# Web Scraper (direct fetch + Firecrawl fallback)

Scrapes web pages with a two-step strategy:
1. **Direct fetch** — free, fast, no API needed. Fetches HTML and converts to markdown.
2. **Firecrawl fallback** — used automatically when direct fetch fails (403, 429, empty content, JS-heavy sites).

Returns clean markdown content with images, captions, and social media embeds.

## How to Use

### Basic usage — output to stdout:

```bash
python /path/to/scripts/scrape.py "https://example.com/article"
```

### Save to file:

```bash
python /path/to/scripts/scrape.py "https://example.com/article" -o /home/claude/article.md
```

### JSON output:

```bash
python /path/to/scripts/scrape.py "https://example.com/article" -f json -o /home/claude/article.json
```

### Force Firecrawl (skip direct fetch):

```bash
python /path/to/scripts/scrape.py "https://example.com/article" --force-firecrawl
```

## How It Works

1. Script tries **direct fetch** with a browser User-Agent
2. If the response is HTTP 200 and has enough content (>200 chars of text), it uses that
3. If direct fetch fails (403, 429, timeout, empty content), it automatically falls back to **Firecrawl API**
4. Output includes `**Metoda:**` line showing which method was used

## Output Format

### Markdown output includes:
- **Metadata header:** title, author, publication date, source, URL, method used
- **Main image:** og:image if available
- **Article content:** clean markdown
- **Image list:** all images found in article with alt-text captions
- **Social embeds:** links to embedded X/Twitter, Facebook, Instagram, YouTube posts

### JSON output includes:
```json
{
  "metadata": { "title", "author", "published", "og_image", "source_url", "site_name" },
  "source": "direct | firecrawl",
  "content": "markdown string",
  "images": [{ "alt": "caption", "url": "https://..." }],
  "social_embeds": [{ "type": "x/twitter", "url": "https://..." }]
}
```

## Configuration

Set `FIRECRAWL_API_KEY` env var or add `firecrawl_api_key` to `~/.claude/skills/joe-config.json`.

## Important Notes

- **Direct fetch is tried first** — saves Firecrawl API credits.
- **Firecrawl is the fallback** for sites that block bots or need JS rendering.
- **`--force-firecrawl`** skips direct fetch if you know the site needs it.
- **No binary image download.** Returns image URLs only.

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `[direct] HTTP 403` | Site blocks bots | Automatic fallback to Firecrawl |
| `[direct] Za mało treści` | JS-rendered site | Automatic fallback to Firecrawl |
| `[firecrawl] HTTP 401` | Invalid API key | Check `FIRECRAWL_API_KEY` |
| `[firecrawl] HTTP 429` | Rate limited | Wait and retry |
| `[firecrawl] HTTP 402` | Out of credits | Top up Firecrawl account |
