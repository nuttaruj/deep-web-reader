# Deep Web Reader Skill

> Zero‑dependency 3‑mode web content extraction (Text, Screenshot, PDF) via Browserless API

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)

## 📋 Summary

A unified Python CLI tool that fetches web content in three distinct modes:

- **Text Mode** – Extracts HTML, cleans JavaScript, and converts to clean Markdown using a powerful Markdown engine that supports headings, lists, links, code blocks, bold/italic text, and more.
- **Screenshot Mode** – Captures full‑page screenshots (PNG/JPEG/WebP) with optional stealth and ad‑blocking.
- **PDF Mode** – Generates print‑ready PDF documents with configurable paper size, margins, and orientation.

Built on the [Browserless](https://browserless.io) API, it handles modern JavaScript‑heavy sites without requiring a local browser installation.

## 🎯 Intended Use

- **Web content extraction** for AI agents that need clean, structured text.
- **Visual archiving** of webpages as screenshots or PDFs.
- **Headless browser automation** without maintaining a local Chromium instance.

## ✨ Markdown Engine

The Text Mode includes a powerful Markdown engine that converts HTML to clean, structured Markdown with full support for:

- **Headings** (h1–h6) with proper `#` syntax
- **Lists** (ordered and unordered) with correct indentation
- **Links** with `[text](url)` formatting
- **Code blocks** with triple backticks and language detection
- **Inline code** with single backticks
- **Bold** (`**bold**`) and *italic* (`*italic*`) text
- **Horizontal rules** (`---`)
- **Paragraphs**, line breaks, and divs

The engine uses Python's standard `html.parser` library, ensuring zero external dependencies while maintaining high‑quality Markdown output.

## 🔧 Installation & Configuration

### Dependencies

**Zero‑dependency**: Uses only Python 3 standard libraries (`urllib`, `json`, `argparse`, etc.). No external packages needed.

Ensure Python 3.8+ is installed:

```bash
python3 --version
```

### Environment Variables

| Variable | Required | Purpose | Example |
|----------|----------|---------|---------|
| `BROWSERLESS_HOST` | ✅ | Browserless API endpoint | `https://chrome.browserless.io` |
| `BROWSERLESS_TOKEN` | ✅ | API authentication token | `your‑api‑token‑here` |
| `BROWSERLESS_REGION` | ❌ | API region (`SFO_US`, `LON_UK`, `AMS_NL`) | `SFO_US` |

Set them before running:

```bash
export BROWSERLESS_HOST="https://chrome.browserless.io"
export BROWSERLESS_TOKEN="your‑token"
```

## 🛠️ CLI Parameters (for AI Agents)

### General Syntax

```bash
python3 deep_web_reader.py <URL> [--mode <mode>] [options]
```

### Mode Selection

| Parameter | Values | Description |
|-----------|--------|-------------|
| `--mode` | `text`, `screenshot`, `pdf` | Operation mode (default: `text`) |

### Common Options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--wait‑for` | int (ms) | `5000` | Milliseconds to wait for page load before capture |
| `--output`, `-o` | path | *auto‑generated* | Output file path |
| `--stealth` | flag | `false` | Enable stealth mode (bypass bot detection) |
| `--block‑ads` | flag | `false` | Block ads and consent modals |

### Text‑Mode Specific

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--tags‑to‑remove` | space‑separated list | `script style nav footer noscript` | HTML tags to strip during cleaning |

### Screenshot‑Mode Specific

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--full‑page` / `--no‑full‑page` | flag | `true` | Capture entire page (vs. viewport) |
| `--format` | `png`, `jpeg`, `webp` | `png` | Image format |
| `--quality` | 0‑100 | `80` | JPEG/WebP quality |

### PDF‑Mode Specific

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--pdf‑format` | `A4`, `Letter`, `Legal`, etc. | `A4` | Paper size |
| `--landscape` | flag | `false` | Landscape orientation |
| `--print‑background` | flag | `false` | Include background graphics |
| `--margin‑top`, `--margin‑bottom`, etc. | float (inches) | `0.5` | Page margins |

## 📝 Usage Examples for Agents

### Example 1: Extract Clean Text (with wait time)

```bash
python3 deep_web_reader.py https://example.com --mode text --wait-for 5000
```

**Output:** JSON with `markdown_text` field containing cleaned content.

### Example 2: Capture Screenshot with Stealth

```bash
python3 deep_web_reader.py https://example.com \
  --mode screenshot \
  --stealth \
  --block-ads \
  --output page.png
```

**Output:** PNG file saved to `page.png`.

### Example 3: Generate Landscape PDF

```bash
python3 deep_web_reader.py https://docs.example.com \
  --mode pdf \
  --landscape \
  --margin-top 1.0 \
  --margin-bottom 1.0 \
  --output doc.pdf
```

**Output:** PDF file saved to `doc.pdf`.

## 🔍 Return Values

### Text Mode

```json
{
  "success": true,
  "html": "<original HTML>",
  "markdown_text": "# Clean Markdown\n...",
  "content_length": 1234,
  "original_html_length": 5678,
  "mode": "text"
}
```

### Screenshot Mode

```json
{
  "success": true,
  "output": "/path/to/screenshot.png",
  "url": "https://example.com",
  "mode": "screenshot",
  "format": "png",
  "full_page": true
}
```

### PDF Mode

```json
{
  "success": true,
  "output": "/path/to/report.pdf",
  "url": "https://example.com",
  "mode": "pdf",
  "format": "A4",
  "landscape": false
}
```

## ⚠️ Error Handling

If an operation fails, the JSON will contain:

```json
{
  "success": false,
  "error": "Human‑readable error message",
  "mode": "..."
}
```

Common errors:

- `BROWSERLESS_HOST environment variable not set`
- `HTTP Error 401: Unauthorized`
- `No HTML content found in Browserless API response`
- Timeout errors (increase wait time or use `--stealth`)

## 🧠 Integration Notes for AI Agents

- **Stateless:** Each call is independent; no session persistence.
- **Idempotent:** Repeated calls with the same parameters produce the same output (assuming the webpage hasn’t changed).
- **Resource‑light:** No local browser needed; all rendering happens on Browserless servers.
- **Rate‑limited:** Subject to Browserless API rate limits (check your plan).

## 📁 File Structure

```
deep-web-reader/
├── SKILL.md              # This file (AI‑oriented documentation)
├── README.md             # Human‑oriented documentation
├── LICENSE               # MIT License
└── deep_web_reader.py    # Main Python script
```

## 🔗 References

- **GitHub Repository:** https://github.com/nuttaruj/deep-web-reader
- **Browserless API Docs:** https://docs.browserless.io
- **OpenClaw Skills Guide:** https://docs.openclaw.dev/guides/skills

---

**Created with ❤️**  
*Making web scraping accessible for AI agents*