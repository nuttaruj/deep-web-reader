#!/usr/bin/env python3
import os
import sys
import json
import urllib.request
import urllib.error

def debug_browserless():
    """Debug Browserless API connection and response"""
    host = os.getenv("BROWSERLESS_HOST")
    token = os.getenv("BROWSERLESS_TOKEN")
    
    print(f"Host: {host}")
    print(f"Token length: {len(token) if token else 0}")
    
    # Test URL - LinkedIn
    test_url = "https://www.linkedin.com/jobs/search/?keywords=QA%20Engineer&location=Bangkok%2C%20Thailand"
    
    api_url = f"{host.rstrip('/')}/scrape"
    print(f"API URL: {api_url}")
    
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
        "Cache-Control": "no-cache"
    }
    
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    print("\nHeaders:", json.dumps(headers, indent=2))
    print("\nPayload:", json.dumps(payload, indent=2))
    
    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(api_url, data=data, headers=headers, method="POST")
        
        print("\nSending request...")
        with urllib.request.urlopen(req, timeout=60) as response:
            print(f"Response status: {response.status} {response.reason}")
            raw_response = response.read().decode("utf-8")
            print(f"Response length: {len(raw_response)} chars")
            
            # Try to parse JSON
            try:
                result = json.loads(raw_response)
                print("\nParsed JSON keys:", list(result.keys()))
                if "data" in result:
                    print("Data type:", type(result["data"]))
                    if result["data"]:
                        print("First data item keys:", list(result["data"][0].keys()))
                        html_content = result["data"][0].get("html", "")
                        print(f"HTML content length: {len(html_content)}")
                        if html_content:
                            print("First 200 chars of HTML:", html_content[:200])
                        else:
                            print("HTML is empty!")
                    else:
                        print("Data list is empty!")
                else:
                    print("No 'data' key in response")
            except json.JSONDecodeError:
                print("Response is not valid JSON")
                print("First 500 chars of response:", raw_response[:500])
                
    except urllib.error.HTTPError as e:
        print(f"HTTP Error: {e.code} {e.reason}")
        print(e.read().decode()[:500])
    except Exception as e:
        print(f"Error: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_browserless()