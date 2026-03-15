#!/usr/bin/env python3
"""
Deep Web Reader - A zero-dependency web scraping tool using Browserless API
Created by: WalnutZtudio
Description: Fetch and clean web content with standard library only
"""

import os
import sys
import json
import urllib.request
import urllib.error
import urllib.parse
import re
from html import unescape

# ===================== CONFIGURATION =====================

def get_browserless_config():
    """Read Browserless configuration from environment variables"""
    host = os.getenv("BROWSERLESS_HOST")
    token = os.getenv("BROWSERLESS_TOKEN")
    
    if not host:
        raise ValueError("BROWSERLESS_HOST environment variable not set")
    if not token:
        raise ValueError("BROWSERLESS_TOKEN environment variable not set")
    
    # Ensure host has proper scheme
    if not host.startswith("http"):
        host = f"https://{host}"
    
    return {
        "host": host.rstrip("/"),
        "token": token
    }

# ===================== BROWSERLESS API =====================

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
        "elements": [{
            "selector": "body",
            "timeout": timeout
        }],
        "gotoOptions": {
            "waitUntil": "networkidle2",
            "timeout": timeout
        },
        "waitForTimeout": wait_for
    }
    
    # Create HTTP request
    headers = {
        "Content-Type": "application/json",
        "Cache-Control": "no-cache"
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
            # Response structure can vary, so we try multiple paths
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
                    "status": "fetched"
                }
            else:
                return {
                    "success": False,
                    "html": "",
                    "url": url,
                    "error": "No HTML content found in Browserless API response",
                    "status": "empty_response"
                }
                
    except urllib.error.HTTPError as e:
        return {
            "success": False,
            "html": "",
            "url": url,
            "error": f"HTTP Error {e.code}: {e.reason}",
            "status": "http_error"
        }
    except urllib.error.URLError as e:
        return {
            "success": False,
            "html": "",
            "url": url,
            "error": f"URL Error: {e.reason}",
            "status": "url_error"
        }
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "html": "",
            "url": url,
            "error": f"JSON Decode Error: {str(e)}",
            "status": "json_error"
        }
    except Exception as e:
        return {
            "success": False,
            "html": "",
            "url": url,
            "error": f"Unexpected error: {str(e)}",
            "status": "unknown_error"
        }

# ===================== HTML CLEANING =====================

def clean_html_to_text(html_content, remove_scripts=True, remove_styles=True):
    """
    Convert HTML to clean text using HTMLParser (standard library)
    
    Args:
        html_content (str): Raw HTML content
        remove_scripts (bool): Remove <script> tags
        remove_styles (bool): Remove <style> tags
    
    Returns:
        str: Cleaned text content
    """
    if not html_content:
        return ""
    
    try:
        # Use HTMLParser for more robust parsing
        from html.parser import HTMLParser
        from html import unescape
        
        class TextExtractor(HTMLParser):
            def __init__(self, remove_scripts, remove_styles):
                super().__init__()
                self.text_parts = []
                self.ignore = False
                self.remove_scripts = remove_scripts
                self.remove_styles = remove_styles
            
            def handle_starttag(self, tag, attrs):
                tag_lower = tag.lower()
                if (self.remove_scripts and tag_lower == 'script') or \
                   (self.remove_styles and tag_lower == 'style'):
                    self.ignore = True
            
            def handle_endtag(self, tag):
                tag_lower = tag.lower()
                if (self.remove_scripts and tag_lower == 'script') or \
                   (self.remove_styles and tag_lower == 'style'):
                    self.ignore = False
            
            def handle_data(self, data):
                if not self.ignore:
                    self.text_parts.append(data)
            
            def get_text(self):
                return ' '.join(self.text_parts)
        
        # Decode HTML entities first
        content = unescape(html_content)
        parser = TextExtractor(remove_scripts, remove_styles)
        parser.feed(content)
        text = parser.get_text()
        
        # Clean up whitespace
        import re
        text = re.sub(r'\s+', ' ', text).strip()
        return text
        
    except Exception:
        # Fallback to regex method if parser fails
        import re
        from html import unescape
        
        content = html_content
        
        if remove_scripts:
            content = re.sub(r'<script\b[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
        
        if remove_styles:
            content = re.sub(r'<style\b[^>]*>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)
        
        content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
        content = re.sub(r'<[^>]+>', ' ', content)
        content = unescape(content)
        content = re.sub(r'\s+', ' ', content).strip()
        
        return content

# ===================== MAIN FUNCTION =====================

def deep_web_read(url, clean_html=True, wait_for=5000):
    """
    Main function to fetch and optionally clean web content
    
    Args:
        url (str): Target URL
        clean_html (bool): Whether to clean HTML to text
        wait_for (int): Milliseconds to wait for page load
    
    Returns:
        dict: Result containing success status, content, and metadata
    """
    print(f"[Deep Web Reader] Fetching: {url}")
    
    # Fetch content via Browserless
    result = fetch_with_browserless(url, wait_for=wait_for)
    
    if not result.get("success"):
        print(f"[ERROR] Failed to fetch {url}: {result.get('error', 'Unknown error')}")
        return result
    
    # Clean HTML if requested
    if clean_html and result.get("html"):
        cleaned_text = clean_html_to_text(result["html"])
        result["cleaned_text"] = cleaned_text
        result["content_length"] = len(cleaned_text)
        
        # Also keep original HTML for reference
        result["original_html_length"] = len(result["html"])
    else:
        result["cleaned_text"] = ""
        result["content_length"] = 0
        result["original_html_length"] = len(result.get("html", ""))
    
    print(f"[SUCCESS] Fetched {result.get('original_html_length', 0)} chars, "
          f"cleaned to {result.get('content_length', 0)} chars")
    
    return result

# ===================== END OF MAIN CODE =====================

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 deep_web_reader.py <URL>")
        print("\nOptions:")
        print("  <URL>    Target website URL")
        sys.exit(1)
    
    url = sys.argv[1]
    result = deep_web_read(url)
    
    if result.get('success'):
        print("\n" + "="*60)
        print(f"Successfully fetched: {url}")
        print(f"Original HTML size: {result.get('original_html_length', 0):,} characters")
        print(f"Cleaned text size: {result.get('content_length', 0):,} characters")
        print("="*60)
        print("\nCleaned text preview (first 1000 chars):\n")
        print(result.get('cleaned_text', '')[:1000])
        if result.get('content_length', 0) > 1000:
            print(f"\n[... and {result.get('content_length', 0) - 1000:,} more characters]")
    else:
        print(f"\nERROR: {result.get('error')}")
        sys.exit(1)