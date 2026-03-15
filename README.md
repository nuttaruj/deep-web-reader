---
name: deep-web-reader
description: "Zero-dependency web scraping tool using Browserless API for OpenClaw. Fetch and clean web content with standard Python libraries only. Created by nuttaruj."
homepage: https://github.com/nuttaruj/deep-web-reader
metadata: { "openclaw": { "emoji": "🌐", "requires": { "bins": ["python3"] } } }
---

# Deep Web Reader Skill

Zero-dependency web scraping tool using Browserless API. Created by **nuttaruj**.

## 🎯 Purpose

Fetch clean text content from websites (including JavaScript-rendered pages) using Browserless API with no external dependencies. Perfect for OpenClaw agents that need web content extraction without heavy browser automation.

## 📦 Installation

### For OpenClaw Users

1. **Clone or download the skill folder** to your OpenClaw skills directory:
   ```bash
   # Clone from GitHub
   git clone https://github.com/nuttaruj/deep-web-reader.git ~/.openclaw/skills/deep-web-reader
   ```

2. **Ensure the skill is recognized** by OpenClaw:
   ```bash
   openclaw skills list  # Should show "deep-web-reader"
   ```

## 🔧 Configuration

### Environment Variables

This tool requires **Browserless API** credentials. Set these environment variables before use:

#### **BROWSERLESS_HOST**
- **Purpose:** URL of your Browserless instance
- **Example:** `https://chrome.browserless.io`
- **Default value:** None (required)
- **How to get:** Sign up at [browserless.io](https://browserless.io) for a free tier or self-host

#### **BROWSERLESS_TOKEN**
- **Purpose:** API token for authentication
- **Example:** `your-api-token-here`
- **Default value:** None (required)
- **How to get:** From Browserless dashboard after registration

### Setting Environment Variables

#### For OpenClaw (Global)
Add to your OpenClaw environment configuration file (`~/.openclaw/env` or similar):

```bash
export BROWSERLESS_HOST="https://chrome.browserless.io"
export BROWSERLESS_TOKEN="your-actual-token-here"
```

#### For Single Session (Temporary)
```bash
# In the terminal before running OpenClaw
export BROWSERLESS_HOST="https://chrome.browserless.io"
export BROWSERLESS_TOKEN="your-token"
openclaw start
```

#### For Docker/Container Deployments
Add to your Dockerfile or docker-compose.yml:
```yaml
environment:
  - BROWSERLESS_HOST=https://chrome.browserless.io
  - BROWSERLESS_TOKEN=${BROWSERLESS_TOKEN}
```

## 🚀 Usage

### Basic Command

```bash
# From within the skill directory
cd ~/.openclaw/skills/deep-web-reader
python3 deep_web_reader.py
```

### Programmatic Usage

Import and use in your Python scripts:

```python
from deep_web_reader import deep_web_read

# Fetch and clean content
result = deep_web_read("https://example.com", clean_html=True)

if result["success"]:
    print(f"Got {result['content_length']} characters of clean text")
    print(result["cleaned_text"][:500])  # First 500 chars
else:
    print(f"Error: {result.get('error')}")
```

### OpenClaw Agent Integration

Agents can use this tool via exec:

```python
# In agent code
import os
import subprocess

# Set environment variables
os.environ["BROWSERLESS_HOST"] = "https://chrome.browserless.io"
os.environ["BROWSERLESS_TOKEN"] = "your-token"

# Run the reader
result = subprocess.run(
    ["python3", "/path/to/deep_web_reader.py"],
    capture_output=True,
    text=True
)
```

## 📖 Examples

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

## 🔍 Testing

### Run the Built-in Test

```bash
cd ~/.openclaw/skills/deep-web-reader
python3 deep_web_reader.py
```

Expected output:
```
============================================================
Deep Web Reader - Test Block
Testing example website
============================================================

[1] Checking environment variables...
✓ BROWSERLESS_HOST: https://chrome.browserless.io
✓ BROWSERLESS_TOKEN: ****************

[2] Fetching from example site: https://example.com

[3] SUCCESS! Content fetched and cleaned
    Original HTML size: 15,234 characters
    Cleaned text size: 4,567 characters

[4] Sample of cleaned text (first 500 chars):
----------------------------------------
[Actual website text...]
----------------------------------------

[5] SUCCESS: Successfully extracted 4,567 characters of clean text
    Content validation: ✓ Text extraction successful

[6] Test completed successfully!
    Ready for QA testing with example website by น้องเทส
============================================================
Test block completed
============================================================
```

## 🐛 Troubleshooting

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

## 📁 File Structure

```
deep-web-reader/
├── SKILL.md                    # This file
├── deep_web_reader.py          # Main Python script
├── Requirement.md              # Project requirements
├── CHANGE-SUMMARY.md           # Change history
├── programmer/                 # Development files
│   ├── debug_*.py              # Debug utilities
│   └── test_*.py               # Test scripts
├── qa/                         # Quality assurance
└── reports/                    # Project reports
```

## 🤝 Contributing

Contributions welcome! This is an open-source project by **nuttaruj**.

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## 📄 License

MIT License - See LICENSE file for details.

## 🔗 Links

- **GitHub Repository:** https://github.com/nuttaruj/deep-web-reader
- **Browserless API:** https://browserless.io
- **OpenClaw Documentation:** https://docs.openclaw.dev

---

**Created with ❤️ by nuttaruj**  
*Making web scraping accessible for OpenClaw agents worldwide* 
