# Deep Web Reader

> Zero-dependency web scraping tool using Browserless API

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)

## Description

Fetch and clean web content using Browserless API (Playwright-based browser automation).
This tool extracts HTML from JavaScript-heavy websites and converts it to clean Markdown.

## Installation

```bash
pip3 install --break-system-packages deep-web-reader
```

## Configuration

Set environment variables before running:

```bash
export BROWSERLESS_HOST="http://your-browserless-server:32768"
export BROWSERLESS_TOKEN="your-api-token"
```

## Usage

```bash
# Basic usage
python3 deep_web_reader.py https://example.com

# Show help
python3 deep_web_reader.py --help

# Fetch without HTML cleaning
python3 deep_web_reader.py https://example.com --no-clean
```

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `<URL>` | Target website URL | Required |
| `--no-clean` | Skip HTML to Markdown conversion | False |
| `--wait <ms>` | Wait time for page load | 5000ms |
| `--timeout <ms>` | Request timeout | 30000ms |

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `BROWSERLESS_HOST` | ✅ | Browserless API server URL |
| `BROWSERLESS_TOKEN` | ✅ | API authentication token |

## Output Format

Returns JSON with:
- `success`: boolean
- `html`: original HTML content
- `markdown_text`: cleaned Markdown
- `content_length`: number of characters
- `error`: error message (if failed)

## Examples

### Example 1: Basic Website Fetch

```python
from deep_web_reader import deep_web_read

result = deep_web_read("https://news.ycombinator.com")
if result["success"]:
    print(f"✅ Fetched {result['content_length']} chars from Hacker News")
```

### Example 2: Longer Wait for JavaScript Sites

```python
# Some sites need more time to render
result = deep_web_read(
    "https://app.somejsframework.com",
    wait_for=10000  # Wait 10 seconds
)
```

### Example 3: Keep HTML (No Cleaning)

```python
# Get raw HTML for parsing with other tools
result = deep_web_read("https://example.com", clean_html=False)
html_content = result["html"]
```

## Troubleshooting

### Common Issues

#### "BROWSERLESS_HOST environment variable not set"
**Solution:** Set the environment variable before running:
```bash
export BROWSERLESS_HOST="https://chrome.browserless.io"
```

#### "HTTP Error 401: Unauthorized"
**Solution:** Check your `BROWSERLESS_TOKEN` is valid and not expired.

#### "No HTML content found in Browserless API response"
**Solution:** Browserless API response format may have changed. Check the script's `fetch_with_browserless` function for proper parsing.

#### Timeout Errors
**Solution:** Increase the `wait_for` parameter (default 5000ms = 5 seconds):
```python
result = deep_web_read(url, wait_for=15000)  # 15 seconds
```

### Debug Mode

Enable debug output by modifying the script or checking logs:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## File Structure

```
deep-web-reader/
├── README.md             # This documentation
├── LICENSE               # MIT License
├── SKILL.md              # OpenClaw skill metadata
└── deep_web_reader.py    # Main Python script
```

## Contributing

Contributions welcome!

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Links

- **GitHub Repository:** https://github.com/nuttaruj/deep-web-reader
- **Browserless API:** https://browserless.io
- **OpenClaw Documentation:** https://docs.openclaw.dev

---

**Created with ❤️**  
*Making web scraping accessible for everyone*
