#!/usr/bin/env python3
import os
import json
import urllib.request

def debug_structure():
    host = os.getenv("BROWSERLESS_HOST")
    token = os.getenv("BROWSERLESS_TOKEN")
    
    test_url = "https://www.linkedin.com/jobs/search/?keywords=QA%20Engineer&location=Bangkok%2C%20Thailand"
    api_url = f"{host.rstrip('/')}/scrape"
    
    payload = {
        "url": test_url,
        "elements": [{
            "selector": "body",
            "timeout": 30000
        }],
        "gotoOptions": {
            "waitUntil": "networkidle2",
            "timeout": 30000
        },
        "waitForTimeout": 5000
    }
    
    headers = {
        "Content-Type": "application/json",
        "Cache-Control": "no-cache",
        "Authorization": f"Bearer {token}"
    }
    
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(api_url, data=data, headers=headers, method="POST")
    
    with urllib.request.urlopen(req, timeout=60) as response:
        raw_response = response.read().decode("utf-8")
        result = json.loads(raw_response)
        
        print("Full response structure (first level):")
        for key, value in result.items():
            print(f"  {key}: {type(value)}")
        
        print("\n'data' field details:")
        data_field = result.get("data", [])
        print(f"  Type: {type(data_field)}")
        print(f"  Length: {len(data_field)}")
        
        if data_field:
            first_item = data_field[0]
            print(f"\nFirst item in 'data' (keys): {list(first_item.keys())}")
            
            # Check what's in 'results'
            if 'results' in first_item:
                results = first_item['results']
                print(f"\n'results' field:")
                print(f"  Type: {type(results)}")
                print(f"  Length: {len(results)}")
                
                if results:
                    # Check first few items in results
                    for i, item in enumerate(results[:3]):
                        print(f"\n  results[{i}] type: {type(item)}")
                        if isinstance(item, dict):
                            print(f"    Keys: {list(item.keys())}")
                            # Look for HTML content
                            for k, v in item.items():
                                if isinstance(v, str) and ('<' in v or 'html' in k.lower()):
                                    print(f"    {k}: string length {len(v)}")
                                    if len(v) > 0:
                                        print(f"      First 100 chars: {v[:100]}")
                        elif isinstance(item, str):
                            print(f"    String length: {len(item)}")
                            if len(item) > 0:
                                print(f"    First 100 chars: {item[:100]}")
            
            # Also check if there's HTML directly somewhere
            print("\nSearching for HTML content in first item...")
            def search_html(obj, path=""):
                if isinstance(obj, dict):
                    for k, v in obj.items():
                        if isinstance(v, str) and '<' in v and ('html' in v or 'body' in v or 'div' in v):
                            print(f"  Found at {path}.{k}: string length {len(v)}")
                            if len(v) > 0:
                                print(f"    Sample: {v[:200]}")
                        elif isinstance(v, (dict, list)):
                            search_html(v, f"{path}.{k}")
                elif isinstance(obj, list):
                    for i, v in enumerate(obj[:5]):  # Limit depth
                        if isinstance(v, (dict, list, str)):
                            search_html(v, f"{path}[{i}]")
            
            search_html(first_item, "data[0]")
        
        # Save full response to file for inspection
        with open('/tmp/browserless_response.json', 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\nFull response saved to /tmp/browserless_response.json")

if __name__ == "__main__":
    debug_structure()