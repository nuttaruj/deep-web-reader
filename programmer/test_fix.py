#!/usr/bin/env python3
import os
import json
import urllib.request

def test_fixed_logic():
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
        result = json.loads(response.read().decode("utf-8"))
        
        # OLD LOGIC (broken)
        if "data" in result and result["data"]:
            old_html = result["data"][0].get("html", "")
            print(f"OLD logic html length: {len(old_html)}")
        
        # NEW LOGIC - traverse correctly
        html_content = ""
        if "data" in result and result["data"]:
            first_data = result["data"][0]
            if "results" in first_data and first_data["results"]:
                first_result = first_data["results"][0]
                if "html" in first_result:
                    html_content = first_result["html"]
        
        print(f"NEW logic html length: {len(html_content)}")
        
        # Also check alternative paths
        print("\nChecking all possible paths to HTML...")
        def find_html(obj, path=""):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if k == "html" and isinstance(v, str):
                        print(f"  Found 'html' at {path}.{k}: length {len(v)}")
                    elif isinstance(v, (dict, list)):
                        find_html(v, f"{path}.{k}")
            elif isinstance(obj, list):
                for i, v in enumerate(obj[:3]):
                    if isinstance(v, (dict, list)):
                        find_html(v, f"{path}[{i}]")
        
        find_html(result, "root")
        
        # Test cleaning function
        from html import unescape
        import re
        
        def clean_html_to_text(html_content):
            if not html_content:
                return ""
            content = html_content
            # Remove script tags
            content = re.sub(r'<script\b[^>]*>.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
            # Remove style tags
            content = re.sub(r'<style\b[^>]*>.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)
            # Remove HTML comments
            content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)
            # Replace line breaks and multiple spaces
            content = re.sub(r'\n+', '\n', content)
            content = re.sub(r'\s+', ' ', content)
            # Remove HTML tags but preserve text
            content = re.sub(r'<[^>]+>', ' ', content)
            # Decode HTML entities
            content = unescape(content)
            # Final cleanup
            content = re.sub(r'\s+', ' ', content).strip()
            content = re.sub(r'\n\s*\n', '\n\n', content)
            return content
        
        cleaned = clean_html_to_text(html_content[:5000])  # First 5k chars for testing
        print(f"\nCleaned text sample (first 1000 chars):")
        print("-" * 40)
        print(cleaned[:1000])
        print("-" * 40)
        
        return html_content

if __name__ == "__main__":
    test_fixed_logic()