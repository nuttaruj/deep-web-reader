#!/usr/bin/env python3
from html.parser import HTMLParser
from html import unescape
import re

class HTMLTextExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.result = []
        self.ignore_tags = {'script', 'style', 'noscript'}
        self.current_tag = None
    
    def handle_starttag(self, tag, attrs):
        self.current_tag = tag.lower()
        if tag in self.ignore_tags:
            self.ignore_tags.add(tag)
    
    def handle_endtag(self, tag):
        if tag in self.ignore_tags:
            self.ignore_tags.discard(tag)
        self.current_tag = None
    
    def handle_data(self, data):
        if self.current_tag not in self.ignore_tags:
            self.result.append(data)
    
    def get_text(self):
        return ' '.join(self.result)

def clean_html_with_parser(html_content):
    """Clean HTML using HTMLParser (standard library only)"""
    if not html_content:
        return ""
    
    # Decode HTML entities first
    content = unescape(html_content)
    
    # Use parser
    parser = HTMLTextExtractor()
    try:
        parser.feed(content)
        text = parser.get_text()
    except Exception:
        # Fallback to regex if parser fails
        text = re.sub(r'<[^>]+>', ' ', content)
    
    # Clean up whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# Test
if __name__ == "__main__":
    import sys
    sys.path.insert(0, '.')
    from deep_web_reader import fetch_with_browserless
    
    test_url = "https://www.linkedin.com/jobs/search/?keywords=QA%20Engineer&location=Bangkok%2C%20Thailand"
    result = fetch_with_browserless(test_url, wait_for=3000, timeout=10000)
    
    if result['success']:
        html = result['html'][:5000]  # First 5k
        print(f"HTML length: {len(html)}")
        
        cleaned = clean_html_with_parser(html)
        print(f"Cleaned length: {len(cleaned)}")
        print(f"Sample: {cleaned[:500]}")