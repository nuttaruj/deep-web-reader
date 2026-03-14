#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from deep_web_reader import fetch_with_browserless, clean_html_to_text

def test_clean():
    test_url = "https://www.linkedin.com/jobs/search/?keywords=QA%20Engineer&location=Bangkok%2C%20Thailand"
    
    print("Fetching...")
    result = fetch_with_browserless(test_url, wait_for=3000, timeout=10000)
    
    if result['success']:
        html = result['html']
        print(f"HTML length: {len(html)}")
        
        cleaned = clean_html_to_text(html[:5000])  # First 5k chars
        print(f"Cleaned length (from 5k): {len(cleaned)}")
        
        print(f"\nCleaned sample:")
        print("-" * 40)
        print(cleaned[:1000])
        print("-" * 40)
        
        # Check if we get reasonable text
        if len(cleaned) > 100:
            print("✓ Cleaning works!")
        else:
            print("⚠️  Cleaning may not be working properly")
    else:
        print("Fetch failed:", result['error'])

if __name__ == "__main__":
    test_clean()