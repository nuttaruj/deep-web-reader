#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from deep_web_reader import clean_html_to_text, fetch_with_browserless

def test():
    test_url = "https://www.linkedin.com/jobs/search/?keywords=QA%20Engineer&location=Bangkok%2C%20Thailand"
    result = fetch_with_browserless(test_url, wait_for=3000, timeout=10000)
    
    if result['success']:
        html = result['html'][:15000]  # First 15k chars
        print(f"HTML length: {len(html)}")
        
        cleaned = clean_html_to_text(html)
        print(f"Cleaned length: {len(cleaned)}")
        print(f"\nSample (first 1000 chars):")
        print("-" * 60)
        print(cleaned[:1000])
        print("-" * 60)
        
        # Check for keywords
        keywords = ["job", "jobs", "QA", "quality", "engineer", "Bangkok", "ตำแหน่ง", "งาน"]
        found = []
        text_lower = cleaned.lower()
        for kw in keywords:
            if kw.lower() in text_lower:
                found.append(kw)
        
        if found:
            print(f"\nFound keywords: {', '.join(found)}")
        else:
            print("\nNo keywords found (maybe page structure different)")
        
        # Test with full HTML
        print("\n\n=== Testing with full HTML ===")
        full_cleaned = clean_html_to_text(result['html'])
        print(f"Full cleaned length: {len(full_cleaned):,}")
        if len(full_cleaned) > 1000:
            print("✓ Success! Got substantial cleaned text.")
        else:
            print("⚠️  Warning: cleaned text seems short")
    else:
        print("Fetch failed")

if __name__ == "__main__":
    test()