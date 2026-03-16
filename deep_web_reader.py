#!/usr/bin/env python3
"""
Deep Web Reader - Multi-mode web content extraction tool
==========================================================

A unified CLI tool supporting:
- text: Extract and clean HTML to Markdown
- screenshot: Capture full-page screenshots
- pdf: Generate PDF documents from web pages

Modes:
  --mode text      : Extract text content (default)
  --mode screenshot: Capture screenshot (PNG/JPEG)
  --mode pdf       : Generate PDF document

Author: WalnutZtudio
"""

import argparse
import base64
import os
import sys
import json
import urllib.request
import urllib.error
import urllib.parse
import re
from html import unescape
from pathlib import Path

# ===================== CONFIGURATION =====================


def get_browserless_config():
    """Read Browserless configuration from environment variables"""
    host = os.getenv("BROWSERLESS_HOST")
    token = os.getenv("BROWSERLESS_TOKEN") or os.getenv("BROWSERLESS_API_TOKEN")
    region = os.getenv("BROWSERLESS_REGION", "SFO_US")

    if not host and not token:
        raise ValueError(
            "BROWSERLESS_HOST or BROWSERLESS_TOKEN environment variable not set"
        )

    if not host:
        raise ValueError("BROWSERLESS_HOST environment variable not set")

    # Ensure host has proper scheme
    if not host.startswith("http"):
        host = f"https://{host}"

    return {
        "host": host.rstrip("/"),
        "token": token,
        "region": region,
    }





# ===================== TEXT MODE (Existing functionality) =====================

def fetch_with_browserless(url, wait_for=5000, timeout=30000):
    """
    Fetch web content using Browserless API

    Args:
        url (str): Target URL to fetch
        wait_for (int): Milliseconds to wait for page load (default: 5000)
        timeout (int): Request timeout in milliseconds (default: 30000)

    Returns:
        dict: Response containing HTML content and metadata
    """
    config = get_browserless_config()
    api_url = f"{config['host']}/scrape"

    # Prepare request payload
    payload = {
        "url": url,
        "elements": [
            {
                "selector": "body",
                "timeout": timeout,
            }
        ],
        "gotoOptions": {
            "waitUntil": "networkidle2",
            "timeout": timeout,
        },
        "waitForTimeout": wait_for,
    }

    # Create HTTP request
    headers = {
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
    }

    # Add API token if provided
    if config.get("token"):
        headers["Authorization"] = f"Bearer {config['token']}"

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(api_url, data=data, headers=headers, method="POST")

        with urllib.request.urlopen(req, timeout=60) as response:
            result = json.loads(response.read().decode("utf-8"))

            # Extract HTML from Browserless response
            html_content = ""

            if "data" in result and result["data"]:
                first_data = result["data"][0]

                # Try path: data[0].results[0].html (common in newer versions)
                if "results" in first_data and first_data["results"]:
                    first_result = first_data["results"][0]
                    if "html" in first_result:
                        html_content = first_result["html"]
                # Try path: data[0].html (older versions or direct)
                elif "html" in first_data:
                    html_content = first_data["html"]
                # Try path: data[0].text (some responses)
                elif "text" in first_data:
                    html_content = first_data["text"]

            if html_content:
                return {
                    "success": True,
                    "html": html_content,
                    "url": url,
                    "status": "fetched",
                }
            else:
                return {
                    "success": False,
                    "html": "",
                    "url": url,
                    "error": "No HTML content found in Browserless API response",
                    "status": "empty_response",
                }

    except urllib.error.HTTPError as e:
        return {
            "success": False,
            "html": "",
            "url": url,
            "error": f"HTTP Error {e.code}: {e.reason}",
            "status": "http_error",
        }
    except urllib.error.URLError as e:
        return {
            "success": False,
            "html": "",
            "url": url,
            "error": f"URL Error: {e.reason}",
            "status": "url_error",
        }
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "html": "",
            "url": url,
            "error": f"JSON Decode Error: {str(e)}",
            "status": "json_error",
        }
    except Exception as e:
        return {
            "success": False,
            "html": "",
            "url": url,
            "error": f"Unexpected error: {str(e)}",
            "status": "unknown_error",
        }


def clean_html_to_markdown(
    html_content, remove_scripts=True, remove_styles=True, tags_to_remove=None
):
    """
    Convert HTML to clean Markdown using HTMLParser (standard library)

    Args:
        html_content (str): Raw HTML content
        remove_scripts (bool): Remove <script> tags
        remove_styles (bool): Remove <style> tags
        tags_to_remove (list): List of additional tag names to remove

    Returns:
        str: Cleaned Markdown content
    """
    if not html_content:
        return ""

    # Default tags to remove based on parameters
    tags_to_remove = tags_to_remove or []
    if remove_scripts:
        if "script" not in tags_to_remove:
            tags_to_remove.append("script")
    if remove_styles:
        if "style" not in tags_to_remove:
            tags_to_remove.append("style")

    try:
        from html.parser import HTMLParser
        from html import unescape

        class MarkdownExtractor(HTMLParser):
            def __init__(self, tags_to_remove):
                super().__init__()
                self.output = []
                self.ignore = False
                self.tags_to_remove = tags_to_remove
                self.tag_stack = []
                self.list_stack = []
                self.list_item_counters = []
                self.in_pre = False
                self.in_code = False
                self.in_anchor = False
                self.current_href = ""
                self.last_char = ""
                self.pre_language = ""

            def _needs_space_before(self):
                """Return True if we need a space before inline content"""
                if not self.output:
                    return False
                last = self.output[-1]
                if not last:
                    return False
                last_char = last[-1] if last else ""
                if last_char in (
                    " ",
                    "\n",
                    "[",
                    "(",
                    "*",
                    "`",
                    "#",
                    "-",
                    ".",
                    ",",
                    ";",
                    ":",
                    "?",
                    "!",
                    ")",
                    "]",
                    "}",
                    ">",
                ):
                    return False
                return last_char.isalnum()

            def _add_space_if_needed(self):
                """Add a space if needed before inline content"""
                if self._needs_space_before():
                    self.output.append(" ")

            def handle_starttag(self, tag, attrs):
                tag_lower = tag.lower()

                # Ignore tags in the removal list
                if tag_lower in self.tags_to_remove:
                    self.ignore = True
                    return

                self.tag_stack.append(tag_lower)

                if tag_lower in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                    level = int(tag_lower[1])
                    self.output.append("\n" + "#" * level + " ")
                elif tag_lower == "a":
                    self.in_anchor = True
                    self.current_href = ""
                    for attr, val in attrs:
                        if attr.lower() == "href":
                            self.current_href = val
                            break
                    self._add_space_if_needed()
                    self.output.append("[")
                elif tag_lower == "ul":
                    depth = len(
                        [l for l in self.list_stack if l[0] == "ul" or l[0] == "ol"]
                    )
                    self.list_stack.append(("ul", depth))
                    self.list_item_counters.append(0)
                    if self.output and not self.output[-1].endswith("\n"):
                        self.output.append("\n")
                elif tag_lower == "ol":
                    depth = len(
                        [l for l in self.list_stack if l[0] == "ul" or l[0] == "ol"]
                    )
                    self.list_stack.append(("ol", depth))
                    self.list_item_counters.append(0)
                    if self.output and not self.output[-1].endswith("\n"):
                        self.output.append("\n")
                elif tag_lower == "li":
                    if self.list_stack:
                        list_type, depth = self.list_stack[-1]
                        counter_index = len(self.list_stack) - 1
                        self.list_item_counters[counter_index] += 1
                        counter = self.list_item_counters[counter_index]

                        # Determine indentation
                        indent = "  " * depth
                        if list_type == "ul":
                            self.output.append(f"\n{indent}- ")
                        else:  # 'ol'
                            self.output.append(f"\n{indent}{counter}. ")
                    else:
                        self.output.append("\n- ")
                elif tag_lower == "pre":
                    self.in_pre = True
                    if self.output and not self.output[-1].endswith("\n"):
                        self.output.append("\n")
                    self.output.append("```\n")
                elif tag_lower == "code":
                    if not self.in_pre:
                        self.in_code = True
                        self._add_space_if_needed()
                        self.output.append("`")
                elif tag_lower in ["strong", "b"]:
                    self._add_space_if_needed()
                    self.output.append("**")
                elif tag_lower in ["em", "i"]:
                    self._add_space_if_needed()
                    self.output.append("*")
                elif tag_lower == "p":
                    if self.output and not self.output[-1].endswith("\n\n"):
                        if not self.output[-1].endswith("\n"):
                            self.output.append("\n")
                        self.output.append("\n")
                elif tag_lower == "br":
                    self.output.append("\n")
                elif tag_lower == "hr":
                    self.output.append("\n---\n")
                elif tag_lower == "div":
                    if self.output and not self.output[-1].endswith("\n"):
                        self.output.append("\n")

            def handle_endtag(self, tag):
                tag_lower = tag.lower()

                if self.ignore:
                    if tag_lower in self.tags_to_remove:
                        self.ignore = False
                    return

                if self.tag_stack and self.tag_stack[-1] == tag_lower:
                    self.tag_stack.pop()

                if tag_lower in ["h1", "h2", "h3", "h4", "h5", "h6"]:
                    self.output.append("\n")
                elif tag_lower == "a":
                    if self.in_anchor:
                        self.in_anchor = False
                        href = self.current_href if self.current_href else "#"
                        self.output.append(f"]({href})")
                elif tag_lower == "ul":
                    if self.list_stack and self.list_stack[-1][0] == "ul":
                        self.list_stack.pop()
                        self.list_item_counters.pop()
                    self.output.append("\n")
                elif tag_lower == "ol":
                    if self.list_stack and self.list_stack[-1][0] == "ol":
                        self.list_stack.pop()
                        self.list_item_counters.pop()
                    self.output.append("\n")
                elif tag_lower == "li":
                    pass
                elif tag_lower == "pre":
                    self.in_pre = False
                    self.output.append("\n```\n")
                elif tag_lower == "code":
                    if not self.in_pre and self.in_code:
                        self.in_code = False
                        self.output.append("`")
                elif tag_lower in ["strong", "b"]:
                    self.output.append("**")
                elif tag_lower in ["em", "i"]:
                    self.output.append("*")
                elif tag_lower == "p":
                    self.output.append("\n")
                elif tag_lower == "div":
                    self.output.append("\n")

            def handle_data(self, data):
                if self.ignore:
                    return

                # Preserve whitespace in pre/code blocks
                if self.in_pre or self.in_code:
                    self.output.append(data)
                    return

                # Normalize whitespace outside code blocks
                if not data.strip():
                    if self.output and self.output[-1] and self.output[-1][-1] not in (
                        " ",
                        "\n",
                    ):
                        self.output.append(" ")
                    return

                # Clean up multiple spaces within text
                cleaned = " ".join(data.split())

                # Add space before if original data has leading space
                if self.output and self.output[-1] and self.output[-1][-1] not in (
                    " ",
                    "\n",
                ):
                    if data[0].isspace() or self._needs_space_before():
                        self.output.append(" ")

                self.output.append(cleaned)

                # Add trailing space if original data has trailing space
                if data[-1].isspace():
                    self.output.append(" ")

            def get_markdown(self):
                # Join all parts
                result = "".join(self.output)

                # Clean up multiple blank lines
                import re

                result = re.sub(r"\n\s*\n\s*\n+", "\n\n", result)

                # Fix any double spaces
                result = re.sub(r"[ \t]+", " ", result)

                # Remove leading/trailing whitespace on each line
                lines = result.split("\n")
                lines = [line.rstrip() for line in lines]
                result = "\n".join(lines)

                # Remove multiple empty lines again
                result = re.sub(r"\n\s*\n\s*\n+", "\n\n", result)

                # Final trim
                return result.strip()

        # Decode HTML entities first
        content = unescape(html_content)
        parser = MarkdownExtractor(tags_to_remove)
        parser.feed(content)
        markdown = parser.get_markdown()

        return markdown

    except Exception as e:
        # Fallback to basic text extraction if parser fails
        import re
        from html import unescape

        content = html_content

        # Remove all tags in tags_to_remove
        for tag in tags_to_remove:
            pattern = rf"<{tag}\b[^>]*>.*?</{tag}>"
            content = re.sub(pattern, "", content, flags=re.DOTALL | re.IGNORECASE)

        content = re.sub(r"<!--.*?-->", "", content, flags=re.DOTALL)
        content = re.sub(r"<[^>]+>", " ", content)
        content = unescape(content)
        content = re.sub(r"\s+", " ", content).strip()

        return content


def text_mode(url, wait_for=5000, tags_to_remove=None):
    """
    Text mode: Fetch URL and convert to clean Markdown

    Args:
        url: Target URL
        wait_for: Milliseconds to wait for page load
        tags_to_remove: List of HTML tags to remove

    Returns:
        dict: Result with markdown text and metadata
    """
    # Fetch content via Browserless
    result = fetch_with_browserless(url, wait_for=wait_for)

    if not result.get("success"):
        return result

    # Clean HTML if requested
    if result.get("html"):
        if tags_to_remove is None:
            tags_to_remove = ["script", "style", "nav", "footer", "noscript"]
        markdown = clean_html_to_markdown(result["html"], tags_to_remove=tags_to_remove)
        result["markdown_text"] = markdown
        result["content_length"] = len(markdown)
        result["original_html_length"] = len(result["html"])
        result["mode"] = "text"
    else:
        result["markdown_text"] = ""
        result["content_length"] = 0
        result["original_html_length"] = len(result.get("html", ""))
        result["mode"] = "text"

    return result


# ===================== SCREENSHOT MODE =====================

def screenshot_mode(
    url,
    output=None,
    full_page=True,
    image_format="png",
    quality=80,
    stealth=False,
    block_ads=False,
    wait_for=5000,
):
    """
    Screenshot mode: Capture screenshot of web page

    Args:
        url: Target URL
        output: Output file path (default: auto-generated)
        full_page: Capture full page or just viewport
        image_format: Image format (png, jpeg, webp)
        quality: JPEG/WebP quality (0-100)
        stealth: Enable stealth mode
        block_ads: Block ads and consent modals
        wait_for: Milliseconds to wait for page load

    Returns:
        dict: Result with screenshot path and metadata
    """
    try:
        config = get_browserless_config()
        token = config.get("token")
        host = config["host"]
        
        # Build API URL
        api_url = f"{host}/screenshot"
        if token:
            api_url += f"?token={token}"
        
        # Prepare payload
        payload = {
            "url": url,
            "options": {
                "type": image_format,
                "fullPage": full_page,
            },
            "waitForTimeout": wait_for,
        }
        
        # Add quality for JPEG/WebP
        if image_format in ("jpeg", "webp"):
            payload["options"]["quality"] = quality
        
        # Add stealth and ad blocking
        if stealth:
            payload["stealth"] = True
        if block_ads:
            payload["blockAds"] = True
            payload["blockConsentModals"] = True
        
        # Generate output filename if not provided
        if not output:
            from datetime import datetime
            import re

            # Clean URL for filename
            clean_name = re.sub(r"[^a-zA-Z0-9]", "_", url)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output = f"screenshot_{clean_name}_{timestamp}.{image_format}"
        
        # Ensure output directory exists
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Make API request
        headers = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
        }
        
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(api_url, data=data, headers=headers, method="POST")
        
        with urllib.request.urlopen(req, timeout=120) as response:
            # Read binary response
            image_data = response.read()
            
            # Save to file
            with open(output, "wb") as f:
                f.write(image_data)
        
        result = {
            "success": True,
            "output": output,
            "url": url,
            "mode": "screenshot",
            "format": image_format,
            "full_page": full_page,
        }

        return result

    except urllib.error.HTTPError as e:
        return {
            "success": False,
            "error": f"HTTP Error {e.code}: {e.reason}",
            "mode": "screenshot",
        }
    except urllib.error.URLError as e:
        return {
            "success": False,
            "error": f"URL Error: {e.reason}",
            "mode": "screenshot",
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"Screenshot error: {str(e)}",
            "mode": "screenshot",
        }


# ===================== PDF MODE =====================

def pdf_mode(
    url,
    output=None,
    paper_format="A4",
    landscape=False,
    print_background=False,
    margin_top=0.5,
    margin_bottom=0.5,
    margin_left=0.5,
    margin_right=0.5,
    stealth=False,
    block_ads=False,
    wait_for=5000,
):
    """
    PDF mode: Generate PDF from web page

    Args:
        url: Target URL
        output: Output file path (default: auto-generated)
        paper_format: Paper format (A4, Letter, etc.)
        landscape: Landscape orientation
        print_background: Print background graphics
        margin_top: Top margin in inches
        margin_bottom: Bottom margin in inches
        margin_left: Left margin in inches
        margin_right: Right margin in inches
        stealth: Enable stealth mode
        block_ads: Block ads and consent modals
        wait_for: Milliseconds to wait for page load

    Returns:
        dict: Result with PDF path and metadata
    """
    try:
        config = get_browserless_config()
        token = config.get("token")
        host = config["host"]
        
        # Build API URL
        api_url = f"{host}/pdf"
        if token:
            api_url += f"?token={token}"
        
        # Prepare payload
        payload = {
            "url": url,
            "options": {
                "format": paper_format,
                "landscape": landscape,
                "printBackground": print_background,
                "margin": {
                    "top": f"{margin_top}in",
                    "bottom": f"{margin_bottom}in",
                    "left": f"{margin_left}in",
                    "right": f"{margin_right}in",
                },
            },
            "waitForTimeout": wait_for,
        }
        
        # Add stealth and ad blocking
        if stealth:
            payload["stealth"] = True
        if block_ads:
            payload["blockAds"] = True
            payload["blockConsentModals"] = True
        
        # Generate output filename if not provided
        if not output:
            from datetime import datetime
            import re

            # Clean URL for filename
            clean_name = re.sub(r"[^a-zA-Z0-9]", "_", url)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output = f"report_{clean_name}_{timestamp}.pdf"
        
        # Ensure output directory exists
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Make API request
        headers = {
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
        }
        
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(api_url, data=data, headers=headers, method="POST")
        
        with urllib.request.urlopen(req, timeout=120) as response:
            # Read binary response
            pdf_data = response.read()
            
            # Save to file
            with open(output, "wb") as f:
                f.write(pdf_data)
        
        result = {
            "success": True,
            "output": output,
            "url": url,
            "mode": "pdf",
            "format": paper_format,
            "landscape": landscape,
        }

        return result

    except urllib.error.HTTPError as e:
        return {
            "success": False,
            "error": f"HTTP Error {e.code}: {e.reason}",
            "mode": "pdf",
        }
    except urllib.error.URLError as e:
        return {
            "success": False,
            "error": f"URL Error: {e.reason}",
            "mode": "pdf",
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"PDF error: {str(e)}",
            "mode": "pdf",
        }


# ===================== MAIN FUNCTION =====================


def main():
    """Main entry point for CLI"""
    parser = argparse.ArgumentParser(
        description="Deep Web Reader - Multi-mode web content extraction tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Text mode (extract clean markdown)
  python3 deep_web_reader.py https://example.com

  # Screenshot mode
  python3 deep_web_reader.py https://example.com --mode screenshot --output screenshot.png

  # PDF mode
  python3 deep_web_reader.py https://example.com --mode pdf --output report.pdf

  # Advanced options
  python3 deep_web_reader.py https://example.com --mode screenshot --full-page --stealth --block-ads
  python3 deep_web_reader.py https://example.com --mode pdf --format A4 --landscape --block-ads

Environment Variables:
  BROWSERLESS_HOST      : Browserless API host (e.g., https://browserless.io)
  BROWSERLESS_TOKEN     : Browserless API token
  BROWSERLESS_REGION    : API region (SFO_US, LON_UK, AMS_NL)
        """,
    )

    parser.add_argument("url", help="Target URL to fetch")

    parser.add_argument(
        "--mode",
        choices=["text", "screenshot", "pdf"],
        default="text",
        help="Operation mode: text (extract markdown), screenshot (capture PNG), pdf (generate PDF)",
    )

    # Screenshot options
    parser.add_argument(
        "--output", "-o",
        help="Output file path (auto-generated if not specified)",
    )

    parser.add_argument(
        "--full-page",
        action="store_true",
        default=True,
        help="Capture full page (not just viewport)",
    )

    parser.add_argument(
        "--no-full-page",
        action="store_false",
        dest="full_page",
        help="Capture only viewport (opposite of --full-page)",
    )

    parser.add_argument(
        "--format",
        choices=["png", "jpeg", "webp"],
        default="png",
        help="Output format for screenshot (default: png)",
    )

    parser.add_argument(
        "--quality",
        type=int,
        default=80,
        help="JPEG/WebP quality (0-100, default: 80)",
    )

    parser.add_argument(
        "--stealth",
        action="store_true",
        help="Enable stealth mode to bypass bot detection",
    )

    parser.add_argument(
        "--block-ads",
        action="store_true",
        help="Block ads and consent modals for cleaner output",
    )

    # PDF options
    parser.add_argument(
        "--pdf-format",
        choices=[
            "Letter",
            "Legal",
            "Tabloid",
            "Ledger",
            "A0",
            "A1",
            "A2",
            "A3",
            "A4",
            "A5",
            "A6",
        ],
        default="A4",
        help="PDF paper format (default: A4)",
    )

    parser.add_argument(
        "--landscape",
        action="store_true",
        help="Landscape orientation for PDF",
    )

    parser.add_argument(
        "--print-background",
        action="store_true",
        help="Print background graphics in PDF",
    )

    parser.add_argument(
        "--margin-top",
        type=float,
        default=0.5,
        help="Top margin in inches (default: 0.5)",
    )

    parser.add_argument(
        "--margin-bottom",
        type=float,
        default=0.5,
        help="Bottom margin in inches (default: 0.5)",
    )

    parser.add_argument(
        "--margin-left",
        type=float,
        default=0.5,
        help="Left margin in inches (default: 0.5)",
    )

    parser.add_argument(
        "--margin-right",
        type=float,
        default=0.5,
        help="Right margin in inches (default: 0.5)",
    )

    parser.add_argument(
        "--tags-to-remove",
        nargs="*",
        default=["script", "style", "nav", "footer", "noscript"],
        help="HTML tags to remove during text cleaning (default: script style nav footer noscript)",
    )

    parser.add_argument(
        "--wait-for",
        type=int,
        default=5000,
        help="Milliseconds to wait for page load before capture (default: 5000)",
    )

    args = parser.parse_args()

    # Execute based on mode
    if args.mode == "text":
        result = text_mode(
            url=args.url,
            wait_for=args.wait_for,
            tags_to_remove=args.tags_to_remove,
        )
    elif args.mode == "screenshot":
        result = screenshot_mode(
            url=args.url,
            output=args.output,
            full_page=args.full_page,
            image_format=args.format,
            quality=args.quality,
            stealth=args.stealth,
            block_ads=args.block_ads,
            wait_for=args.wait_for,
        )
    elif args.mode == "pdf":
        result = pdf_mode(
            url=args.url,
            output=args.output,
            paper_format=args.pdf_format,
            landscape=args.landscape,
            print_background=args.print_background,
            margin_top=args.margin_top,
            margin_bottom=args.margin_bottom,
            margin_left=args.margin_left,
            margin_right=args.margin_right,
            stealth=args.stealth,
            block_ads=args.block_ads,
            wait_for=args.wait_for,
        )
    
    # AI-Friendly JSON Output: print JSON only, single line
    print(json.dumps(result))
    
    # Exit with appropriate code
    sys.exit(0 if result.get("success") else 1)


if __name__ == "__main__":
    main()
