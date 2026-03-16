# Deep Web Reader

> Zero-dependency 3-in-1 web scraper using Browserless API (Text, Screenshot, PDF)

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)

## 🚀 Introduction

**Deep Web Reader** is a unified CLI tool that extracts web content in three different modes:

1. **Text Mode** – Fetches HTML, cleans JavaScript, and converts to clean Markdown.
2. **Screenshot Mode** – Captures full‑page screenshots (PNG, JPEG, WebP) with optional stealth and ad‑blocking.
3. **PDF Mode** – Generates print‑ready PDF documents with configurable paper size, margins, and orientation.

Built on the [Browserless](https://browserless.io) API, it works with modern JavaScript‑heavy sites without requiring a local browser.

## 📦 Installation

**Zero‑dependency**: This tool uses only Python 3 standard libraries (`urllib`, `json`, `argparse`, etc.). No external packages needed.

Just ensure you have Python 3.8 or newer:

```bash
python3 --version
```

## 🔧 Setup

Set two environment variables before running:

```bash
export BROWSERLESS_HOST="https://chrome.browserless.io"  # or your self‑hosted instance
export BROWSERLESS_TOKEN="your‑api‑token"
```

> **Note:** Get a free token at [browserless.io](https://browserless.io).

## 🎯 Usage Examples

### Text Mode (default)

Extract clean Markdown from any webpage:

```bash
python3 deep_web_reader.py https://example.com --mode text
```

### Screenshot Mode

Capture a full‑page screenshot:

```bash
python3 deep_web_reader.py https://example.com --mode screenshot --output shot.png
```

### PDF Mode

Generate a PDF report (A4 format):

```bash
python3 deep_web_reader.py https://example.com --mode pdf --pdf-format A4
```

## ⚙️ Command‑Line Options

### General Options

| Option | Description | Default |
|--------|-------------|---------|
| `URL` | Target website URL | **Required** |
| `--mode` | Operation mode: `text`, `screenshot`, `pdf` | `text` |
| `--wait‑for` | Milliseconds to wait for page load before capture | `5000` |
| `--output`, `-o` | Output file path (auto‑generated if omitted) | – |
| `--stealth` | Enable stealth mode to bypass bot detection | `false` |
| `--block‑ads` | Block ads and consent modals | `false` |

### Text‑Mode Options

| Option | Description | Default |
|--------|-------------|---------|
| `--tags‑to‑remove` | HTML tags to strip (space‑separated) | `script style nav footer noscript` |

### Screenshot‑Mode Options

| Option | Description | Default |
|--------|-------------|---------|
| `--full‑page` / `--no‑full‑page` | Capture entire page vs. viewport | `true` |
| `--format` | Image format: `png`, `jpeg`, `webp` | `png` |
| `--quality` | JPEG/WebP quality (0–100) | `80` |

### PDF‑Mode Options

| Option | Description | Default |
|--------|-------------|---------|
| `--pdf‑format` | Paper size: `A4`, `Letter`, `Legal`, etc. | `A4` |
| `--landscape` | Landscape orientation | `false` |
| `--print‑background` | Include background graphics | `false` |
| `--margin‑top` / `--margin‑bottom` / `--margin‑left` / `--margin‑right` | Margins in inches | `0.5` |

## 📄 Output Formats

### Text Mode

Returns a JSON object with:
- `success`: boolean
- `html`: original HTML
- `markdown_text`: cleaned Markdown
- `content_length`: character count
- `error`: error message (if any)

### Screenshot Mode

Saves an image file and returns:
- `success`: boolean
- `output`: file path
- `format`: image format
- `full_page`: boolean

### PDF Mode

Saves a PDF file and returns:
- `success`: boolean
- `output`: file path
- `format`: paper size
- `landscape`: boolean

## 🧪 Advanced Examples

### Long Wait for JavaScript‑Heavy Sites

```bash
# Wait 15 seconds for the page to fully render
python3 deep_web_reader.py https://app.example.com --mode text --wait-for 15000
```

### Stealth Screenshot with Ad Blocking

```bash
python3 deep_web_reader.py https://news.ycombinator.com \
  --mode screenshot \
  --stealth \
  --block-ads \
  --output hn.png
```

### Landscape PDF with Custom Margins

```bash
python3 deep_web_reader.py https://docs.example.com \
  --mode pdf \
  --landscape \
  --margin-top 1.0 \
  --margin-bottom 1.0 \
  --output documentation.pdf
```

## 🔍 Troubleshooting

### Common Issues

| Symptom | Likely Cause | Solution |
|---------|--------------|----------|
| `BROWSERLESS_HOST environment variable not set` | Missing environment variable | Set `export BROWSERLESS_HOST="https://chrome.browserless.io"` |
| `HTTP Error 401: Unauthorized` | Invalid or expired token | Regenerate token in Browserless dashboard |
| `No HTML content found in Browserless API response` | API response format changed | Check the script’s `fetch_with_browserless` function |
| Timeout errors | Page load too slow | Increase wait time (default 5 s) or use `--stealth` |

### Debug Mode

Enable verbose logging by adding debug code:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 📁 File Structure

```
deep-web-reader/
├── README.md             # This documentation
├── SKILL.md              # OpenClaw skill metadata
├── LICENSE               # MIT License
└── deep_web_reader.py    # Main Python script
```

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## 📄 License

MIT License – see [LICENSE](LICENSE) for details.

## 🔗 Links

- **GitHub Repository:** https://github.com/nuttaruj/deep-web-reader
- **Browserless API:** https://browserless.io
- **OpenClaw Documentation:** https://docs.openclaw.dev

---

**Created with ❤️**  
*Making web scraping accessible for everyone*