#!/usr/bin/env python3
"""
Test script for Deep Web Reader
Test WalnutZtudio website extraction as required
"""

import os
import sys
import json
import unittest
from deep_web_reader import deep_web_read, fetch_with_browserless, clean_html_to_text, get_browserless_config

def test_walnutztudio():
    """
    Test function for WalnutZtudio website
    This replicates the test block from the original deep_web_reader.py
    """
    print("=" * 60)
    print("Deep Web Reader - Test Script")
    print("Testing WalnutZtudio website")
    print("=" * 60)
    
    # Test URL - WalnutZtudio homepage (non-aggressive anti-bot)
    test_url = "https://walnutztudio.com"
    
    # Check environment variables
    print("\n[1] Checking environment variables...")
    host = os.getenv("BROWSERLESS_HOST")
    token = os.getenv("BROWSERLESS_TOKEN")
    
    if not host:
        print("WARNING: BROWSERLESS_HOST not set in environment")
        print("Please set with: export BROWSERLESS_HOST='https://chrome.browserless.io'")
    
    if not token:
        print("WARNING: BROWSERLESS_TOKEN not set in environment")
        print("Please set with: export BROWSERLESS_TOKEN='your-api-token'")
    
    if not host or not token:
        print("\n[SKIP] Cannot run test without Browserless credentials")
        print("To test with mock data, uncomment the mock test section in code")
        return {
            "success": False,
            "error": "Missing Browserless credentials",
            "status": "skipped"
        }
    
    print(f"✓ BROWSERLESS_HOST: {host[:50]}..." if len(host) > 50 else f"✓ BROWSERLESS_HOST: {host}")
    print(f"✓ BROWSERLESS_TOKEN: {'*' * len(token)}")
    
    # Run actual fetch
    print(f"\n[2] Fetching from WalnutZtudio: {test_url}")
    
    try:
        result = deep_web_read(test_url, clean_html=True, wait_for=8000)
        
        if result.get("success"):
            print(f"\n[3] SUCCESS! Content fetched and cleaned")
            print(f"    Original HTML size: {result.get('original_html_length', 0):,} characters")
            print(f"    Cleaned text size: {result.get('content_length', 0):,} characters")
            
            # Show sample of cleaned text
            cleaned_text = result.get("cleaned_text", "")
            if cleaned_text:
                print(f"\n[4] Sample of cleaned text (first 500 chars):")
                print("-" * 40)
                sample = cleaned_text[:500]
                print(sample)
                if len(cleaned_text) > 500:
                    print("... [truncated]")
                print("-" * 40)
            
            # Check if we got actual content (per new simplified requirements)
            content_length = result.get("content_length", 0)
            if content_length > 0:
                print(f"\n[5] SUCCESS: Successfully extracted {content_length:,} characters of clean text")
                print(f"    Content validation: ✓ Text extraction successful")
            else:
                print(f"\n[5] WARNING: Clean text extraction resulted in empty content")
                print(f"    Content validation: ⚠️  No text extracted (possible anti-bot or empty page)")
            
            print("\n[6] Test completed successfully!")
            print("    Ready for QA testing with WalnutZtudio website by น้องเทส")
            
        else:
            print(f"\n[ERROR] Fetch failed: {result.get('error', 'Unknown error')}")
            print("Status:", result.get("status", "unknown"))
            return result
            
    except KeyboardInterrupt:
        print("\n[INTERRUPT] Test interrupted by user")
        return {
            "success": False,
            "error": "Interrupted by user",
            "status": "interrupted"
        }
    except Exception as e:
        print(f"\n[EXCEPTION] Unexpected error during test: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e),
            "status": "exception"
        }
    
    print("\n" + "=" * 60)
    print("Test block completed")
    print("=" * 60)
    
    return result


def run_mock_test():
    """
    Run a mock test without Browserless credentials
    Useful for CI/CD or when credentials aren't available
    """
    print("=" * 60)
    print("Deep Web Reader - Mock Test")
    print("=" * 60)
    
    # Test the HTML cleaning function
    print("\n[1] Testing HTML cleaning function...")
    test_html = """
    <html>
        <head><title>Test Page</title></head>
        <body>
            <h1>Hello World</h1>
            <p>This is a test paragraph.</p>
            <script>alert('test');</script>
            <style>body { color: red; }</style>
            <div>More text here.</div>
        </body>
    </html>
    """
    
    cleaned = clean_html_to_text(test_html, remove_scripts=True, remove_styles=True)
    print(f"Original HTML: {len(test_html)} chars")
    print(f"Cleaned text: {len(cleaned)} chars")
    print(f"Cleaned content: {cleaned[:100]}...")
    
    if len(cleaned) > 0 and "Hello World" in cleaned:
        print("✓ HTML cleaning function works correctly")
    else:
        print("✗ HTML cleaning function failed")
        return False
    
    # Test configuration function
    print("\n[2] Testing configuration function...")
    try:
        # Temporarily set environment variables for test
        os.environ["BROWSERLESS_HOST"] = "https://test.example.com"
        os.environ["BROWSERLESS_TOKEN"] = "test-token"
        
        config = get_browserless_config()
        print(f"Config host: {config['host']}")
        print(f"Config token: {config['token']}")
        
        if config["host"] == "https://test.example.com" and config["token"] == "test-token":
            print("✓ Configuration function works correctly")
        else:
            print("✗ Configuration function failed")
            return False
            
        # Clean up
        del os.environ["BROWSERLESS_HOST"]
        del os.environ["BROWSERLESS_TOKEN"]
        
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False
    
    print("\n[3] Mock test completed successfully!")
    return True


class TestDeepWebReader(unittest.TestCase):
    """Unit tests for Deep Web Reader"""
    
    def test_html_cleaning(self):
        """Test HTML cleaning function"""
        html = "<h1>Test</h1><p>Content</p>"
        cleaned = clean_html_to_text(html)
        self.assertIsInstance(cleaned, str)
        self.assertGreater(len(cleaned), 0)
    
    def test_html_cleaning_with_scripts(self):
        """Test HTML cleaning with script removal"""
        html = "<script>alert('test');</script><p>Visible text</p>"
        cleaned = clean_html_to_text(html, remove_scripts=True)
        self.assertNotIn("alert", cleaned)
        self.assertIn("Visible text", cleaned)
    
    def test_config_function(self):
        """Test configuration retrieval"""
        # Save original env vars
        original_host = os.getenv("BROWSERLESS_HOST")
        original_token = os.getenv("BROWSERLESS_TOKEN")
        
        # Set test values
        os.environ["BROWSERLESS_HOST"] = "https://test.example.com"
        os.environ["BROWSERLESS_TOKEN"] = "test-token-123"
        
        try:
            config = get_browserless_config()
            self.assertEqual(config["host"], "https://test.example.com")
            self.assertEqual(config["token"], "test-token-123")
        finally:
            # Restore original values
            if original_host:
                os.environ["BROWSERLESS_HOST"] = original_host
            else:
                del os.environ["BROWSERLESS_HOST"]
                
            if original_token:
                os.environ["BROWSERLESS_TOKEN"] = original_token
            else:
                del os.environ["BROWSERLESS_TOKEN"]


if __name__ == "__main__":
    """
    Main test execution
    """
    print("Deep Web Reader Test Suite")
    print("=" * 50)
    
    # Check for command line arguments
    if len(sys.argv) > 1 and sys.argv[1] == "unit":
        # Run unit tests
        print("Running unit tests...")
        unittest.main(argv=[sys.argv[0]])
    elif len(sys.argv) > 1 and sys.argv[1] == "mock":
        # Run mock test
        print("Running mock test...")
        success = run_mock_test()
        sys.exit(0 if success else 1)
    else:
        # Run the main WalnutZtudio test
        print("Running WalnutZtudio website test...")
        result = test_walnutztudio()
        
        if result and result.get("success"):
            print("\n✅ Test PASSED")
            sys.exit(0)
        else:
            print("\n❌ Test FAILED")
            sys.exit(1)