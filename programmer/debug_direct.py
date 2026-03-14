#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from deep_web_reader import fetch_with_browserless

def debug():
    test_url = "https://www.linkedin.com/jobs/search/?keywords=QA%20Engineer&location=Bangkok%2C%20Thailand"
    
    print("Testing fetch_with_browserless directly...")
    result = fetch_with_browserless(test_url, wait_for=3000, timeout=10000)
    
    print(f"Success: {result.get('success')}")
    print(f"Error: {result.get('error', 'None')}")
    print(f"Status: {result.get('status')}")
    print(f"HTML length: {len(result.get('html', ''))}")
    
    if result.get('html'):
        print(f"\nFirst 200 chars of HTML:")
        print("-" * 40)
        print(result['html'][:200])
        print("-" * 40)
    
    return result

if __name__ == "__main__":
    debug()