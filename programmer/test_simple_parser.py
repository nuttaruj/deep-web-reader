#!/usr/bin/env python3
from html.parser import HTMLParser
import re

class SimpleHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text_parts = []
    
    def handle_data(self, data):
        self.text_parts.append(data)
    
    def get_text(self):
        return ' '.join(self.text_parts)

def extract_text_from_html(html):
    parser = SimpleHTMLParser()
    parser.feed(html)
    return parser.get_text()

# Test with a small sample
sample_html = """<div>Hello <b>World</b>!</div>
<script>alert('test');</script>
<style>body { color: red; }</style>
<p>More text</p>"""

print("Test 1:")
print(extract_text_from_html(sample_html))

# Test with LinkedIn sample
import sys
sys.path.insert(0, '.')
from deep_web_reader import fetch_with_browserless

test_url = "https://www.linkedin.com/jobs/search/?keywords=QA%20Engineer&location=Bangkok%2C%20Thailand"
result = fetch_with_browserless(test_url, wait_for=3000, timeout=10000)

if result['success']:
    html = result['html'][:10000]
    print(f"\nHTML length: {len(html)}")
    
    text = extract_text_from_html(html)
    print(f"Extracted text length: {len(text)}")
    print(f"First 500 chars: {text[:500]}")