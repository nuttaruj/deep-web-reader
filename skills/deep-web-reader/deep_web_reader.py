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

# ===================== HTML TO MARKDOWN CONVERSION =====================

def clean_html_to_markdown(html_content, remove_scripts=True, remove_styles=True, tags_to_remove=None):
    """
    Convert HTML to clean Markdown using HTMLParser (standard library)
    
    Args:
        html_content (str): Raw HTML content
        remove_scripts (bool): Remove <script> tags
        remove_styles (bool): Remove <style> tags
        tags_to_remove (list): List of additional tag names to remove (e.g., ['nav', 'footer', 'noscript'])
    
    Returns:
        str: Cleaned Markdown content
    """
    if not html_content:
        return ""
    
    # Default tags to remove based on parameters
    tags_to_remove = tags_to_remove or []
    if remove_scripts:
        if 'script' not in tags_to_remove:
            tags_to_remove.append('script')
    if remove_styles:
        if 'style' not in tags_to_remove:
            tags_to_remove.append('style')
    
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
                self.list_stack = []  # Track list nesting: ('ul', depth) or ('ol', depth)
                self.list_item_counters = []  # Separate counters for each nested list
                self.in_pre = False
                self.in_code = False
                self.in_anchor = False
                self.current_href = ''
                self.last_char = ''  # Track last character for spacing
                self.pre_language = ''  # Store language for code blocks
            
            def _needs_space_before(self):
                """Return True if we need a space before inline content"""
                if not self.output:
                    return False
                last = self.output[-1]
                if not last:
                    return False
                last_char = last[-1] if last else ''
                # Need space if last character is alphanumeric (word character)
                # but not if it's already a space, newline, or markdown formatting char
                if last_char in (' ', '\n', '[', '(', '*', '`', '#', '-', '.', ',', ';', ':', '?', '!', ')', ']', '}', '>'):
                    return False
                # Also check if last two chars are '**' or '`' (but we only have last char)
                # For simplicity, if last char is markdown formatting, no space
                return last_char.isalnum()
            
            def _add_space_if_needed(self):
                """Add a space if needed before inline content"""
                if self._needs_space_before():
                    self.output.append(' ')
            
            def handle_starttag(self, tag, attrs):
                tag_lower = tag.lower()
                
                # Ignore tags in the removal list
                if tag_lower in self.tags_to_remove:
                    self.ignore = True
                    return
                
                self.tag_stack.append(tag_lower)
                
                if tag_lower in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    level = int(tag_lower[1])
                    self.output.append('\n' + '#' * level + ' ')
                elif tag_lower == 'a':
                    self.in_anchor = True
                    self.current_href = ''
                    for attr, val in attrs:
                        if attr.lower() == 'href':
                            self.current_href = val
                            break
                    self._add_space_if_needed()
                    self.output.append('[')
                elif tag_lower == 'ul':
                    depth = len([l for l in self.list_stack if l[0] == 'ul' or l[0] == 'ol'])
                    self.list_stack.append(('ul', depth))
                    self.list_item_counters.append(0)
                    # Add newline before new list if needed
                    if self.output and not self.output[-1].endswith('\n'):
                        self.output.append('\n')
                elif tag_lower == 'ol':
                    depth = len([l for l in self.list_stack if l[0] == 'ul' or l[0] == 'ol'])
                    self.list_stack.append(('ol', depth))
                    self.list_item_counters.append(0)
                    if self.output and not self.output[-1].endswith('\n'):
                        self.output.append('\n')
                elif tag_lower == 'li':
                    if self.list_stack:
                        list_type, depth = self.list_stack[-1]
                        counter_index = len(self.list_stack) - 1
                        self.list_item_counters[counter_index] += 1
                        counter = self.list_item_counters[counter_index]
                        
                        # Determine indentation
                        indent = '  ' * depth
                        if list_type == 'ul':
                            self.output.append(f'\n{indent}- ')
                        else:  # 'ol'
                            self.output.append(f'\n{indent}{counter}. ')
                    else:
                        self.output.append('\n- ')
                elif tag_lower == 'pre':
                    self.in_pre = True
                    # Ensure we're on a new line
                    if self.output and not self.output[-1].endswith('\n'):
                        self.output.append('\n')
                    self.output.append('```\n')
                elif tag_lower == 'code':
                    if not self.in_pre:
                        self.in_code = True
                        self._add_space_if_needed()
                        self.output.append('`')
                elif tag_lower in ['strong', 'b']:
                    self._add_space_if_needed()
                    self.output.append('**')
                elif tag_lower in ['em', 'i']:
                    self._add_space_if_needed()
                    self.output.append('*')
                elif tag_lower == 'p':
                    # Add newline before paragraph if needed
                    if self.output and not self.output[-1].endswith('\n\n'):
                        if not self.output[-1].endswith('\n'):
                            self.output.append('\n')
                        self.output.append('\n')
                elif tag_lower == 'br':
                    self.output.append('\n')
                elif tag_lower == 'hr':
                    self.output.append('\n---\n')
                elif tag_lower == 'div':
                    # Add newline for block-level div
                    if self.output and not self.output[-1].endswith('\n'):
                        self.output.append('\n')
            
            def handle_endtag(self, tag):
                tag_lower = tag.lower()
                
                if self.ignore:
                    if tag_lower in self.tags_to_remove:
                        self.ignore = False
                    return
                
                if self.tag_stack and self.tag_stack[-1] == tag_lower:
                    self.tag_stack.pop()
                
                if tag_lower in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                    self.output.append('\n')
                elif tag_lower == 'a':
                    if self.in_anchor:
                        self.in_anchor = False
                        href = self.current_href if self.current_href else '#'
                        self.output.append(f']({href})')
                elif tag_lower == 'ul':
                    if self.list_stack and self.list_stack[-1][0] == 'ul':
                        self.list_stack.pop()
                        self.list_item_counters.pop()
                    self.output.append('\n')
                elif tag_lower == 'ol':
                    if self.list_stack and self.list_stack[-1][0] == 'ol':
                        self.list_stack.pop()
                        self.list_item_counters.pop()
                    self.output.append('\n')
                elif tag_lower == 'li':
                    # Nothing special needed
                    pass
                elif tag_lower == 'pre':
                    self.in_pre = False
                    self.output.append('\n```\n')
                elif tag_lower == 'code':
                    if not self.in_pre and self.in_code:
                        self.in_code = False
                        self.output.append('`')
                elif tag_lower in ['strong', 'b']:
                    self.output.append('**')
                elif tag_lower in ['em', 'i']:
                    self.output.append('*')
                elif tag_lower == 'p':
                    self.output.append('\n')
                elif tag_lower == 'div':
                    self.output.append('\n')
            
            def handle_data(self, data):
                if self.ignore:
                    return
                
                # Preserve whitespace in pre/code blocks
                if self.in_pre or self.in_code:
                    self.output.append(data)
                    return
                
                # Normalize whitespace outside code blocks
                if not data.strip():
                    # If it's just whitespace, add a single space if needed
                    if self.output and self.output[-1] and self.output[-1][-1] not in (' ', '\n'):
                        self.output.append(' ')
                    return
                
                # Clean up multiple spaces within text
                cleaned = ' '.join(data.split())
                
                # Add space before if original data has leading space
                if self.output and self.output[-1] and self.output[-1][-1] not in (' ', '\n'):
                    if data[0].isspace() or self._needs_space_before():
                        self.output.append(' ')
                
                self.output.append(cleaned)
                
                # Add trailing space if original data has trailing space
                if data[-1].isspace():
                    self.output.append(' ')
            
            def get_markdown(self):
                # Join all parts
                result = ''.join(self.output)
                
                # Clean up multiple blank lines (more than 2 consecutive newlines)
                import re
                result = re.sub(r'\n\s*\n\s*\n+', '\n\n', result)
                
                # Fix any double spaces
                result = re.sub(r'[ \t]+', ' ', result)
                
                # Remove leading/trailing whitespace on each line
                lines = result.split('\n')
                lines = [line.rstrip() for line in lines]  # Only strip trailing spaces
                result = '\n'.join(lines)
                
                # Remove multiple empty lines again
                result = re.sub(r'\n\s*\n\s*\n+', '\n\n', result)
                
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
            pattern = rf'<{tag}\b[^>]*>.*?</{tag}>'
            content = re.sub(pattern, '', content, flags=re.DOTALL | re.IGNORECASE)
        
        content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
        content = re.sub(r'<[^>]+>', ' ', content)
        content = unescape(content)
        content = re.sub(r'\s+', ' ', content).strip()
        
        return content

# ===================== MAIN FUNCTION =====================




def deep_web_read(url, clean_html=True, wait_for=5000, tags_to_remove=None):
    """
    Main function to fetch and optionally clean web content
    
    Args:
        url (str): Target URL
        clean_html (bool): Whether to clean HTML to text
        wait_for (int): Milliseconds to wait for page load
        tags_to_remove (list): List of HTML tags to remove during cleaning.
            Default: ['script', 'style', 'nav', 'footer', 'noscript']
    
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
        # Default tags to remove
        if tags_to_remove is None:
            tags_to_remove = ['script', 'style', 'nav', 'footer', 'noscript']
        markdown = clean_html_to_markdown(result["html"], tags_to_remove=tags_to_remove)
        result["markdown_text"] = markdown
        result["content_length"] = len(markdown)
        
        # Also keep original HTML for reference
        result["original_html_length"] = len(result["html"])
    else:
        result["markdown_text"] = ""
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
        print(f"Markdown size: {result.get('content_length', 0):,} characters")
        print("="*60)
        print("\nMarkdown content:\n")
        print(result.get('markdown_text', ''))
    else:
        print(f"\nERROR: {result.get('error')}")
        sys.exit(1)