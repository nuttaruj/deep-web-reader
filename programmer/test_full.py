#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from deep_web_reader import deep_web_read

def test_fixed():
    test_url = "https://www.linkedin.com/jobs/search/?keywords=QA%20Engineer&location=Bangkok%2C%20Thailand"
    
    print("Testing fixed deep_web_read function...")
    print(f"URL: {test_url}")
    
    result = deep_web_read(test_url, clean_html=True, wait_for=8000)
    
    print(f"\nSuccess: {result.get('success')}")
    print(f"Error: {result.get('error', 'None')}")
    print(f"Status: {result.get('status')}")
    print(f"Original HTML length: {result.get('original_html_length', 0):,}")
    print(f"Cleaned text length: {result.get('content_length', 0):,}")
    
    if result.get("success"):
        print("\n✓ SUCCESS! Fixed the 0 characters issue!")
        print(f"   Got {result.get('content_length', 0):,} characters of cleaned text")
        
        # Show sample
        cleaned = result.get("cleaned_text", "")
        if cleaned:
            print(f"\nSample (first 500 chars):")
            print("-" * 40)
            print(cleaned[:500])
            print("-" * 40)
            
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
                print("\nWarning: No keywords found (maybe page structure changed)")
    else:
        print("\n✗ Still failing:", result.get("error"))
        
    return result

if __name__ == "__main__":
    test_fixed()