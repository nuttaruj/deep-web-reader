#!/usr/bin/env python3
import sys
import os
import re
from html import unescape
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from deep_web_reader import fetch_with_browserless

def debug_cleaning():
    test_url = "https://www.linkedin.com/jobs/search/?keywords=QA%20Engineer&location=Bangkok%2C%20Thailand"
    
    print("Fetching...")
    result = fetch_with_browserless(test_url, wait_for=3000, timeout=10000)
    
    if not result['success']:
        print("Failed")
        return
    
    html = result['html']
    print(f"Original HTML length: {len(html)}")
    
    # Take first 2000 chars to debug
    sample = html[:2000]
    print(f"\nFirst 2000 chars of HTML:")
    print("-" * 60)
    print(sample)
    print("-" * 60)
    
    # Apply cleaning steps one by one
    content = sample
    
    # 1. Remove scripts
    before = content
    content = re.sub(r'<script\b[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
    print(f"\nAfter script removal: {len(before)} -> {len(content)} chars")
    if before != content:
        print("  Scripts were removed")
    
    # 2. Remove styles
    before = content
    content = re.sub(r'<style\b[^>]*>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)
    print(f"After style removal: {len(before)} -> {len(content)} chars")
    
    # 3. Remove HTML comments
    before = content
    content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
    print(f"After comment removal: {len(before)} -> {len(content)} chars")
    
    # 4. Replace line breaks and spaces
    before = content
    content = re.sub(r'\n+', '\n', content)
    content = re.sub(r'\s+', ' ', content)
    print(f"After whitespace normalization: {len(before)} -> {len(content)} chars")
    
    # 5. Remove HTML tags
    before = content
    content = re.sub(r'<[^>]+>', ' ', content)
    print(f"After tag removal: {len(before)} -> {len(content)} chars")
    
    # 6. Decode entities
    before = content
    content = unescape(content)
    print(f"After entity decode: {len(before)} -> {len(content)} chars")
    
    # 7. Final cleanup
    before = content
    content = re.sub(r'\s+', ' ', content).strip()
    content = re.sub(r'\n\s*\n', '\n\n', content)
    print(f"After final cleanup: {len(before)} -> {len(content)} chars")
    
    print(f"\nFinal cleaned text ({len(content)} chars):")
    print("-" * 60)
    print(content)
    print("-" * 60)
    
    # Try a simpler approach: just remove tags and decode
    print("\n\n=== Trying simpler cleaning ===")
    simple = sample
    # Remove all tags
    simple = re.sub(r'<[^>]+>', ' ', simple)
    simple = unescape(simple)
    simple = re.sub(r'\s+', ' ', simple).strip()
    
    print(f"Simple cleaned ({len(simple)} chars):")
    print(simple[:500])

if __name__ == "__main__":
    debug_cleaning()