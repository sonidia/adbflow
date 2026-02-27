#!/usr/bin/env python3
"""
Test script cho ads automation với text-based "Learn more" click

Chạy script này để test với URL ads thật:
    python test_ads.py "https://your-ads-url-here"
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from main import run_ads_automation

def test_ads_automation(url: str, serial: str = "223824861c027ece"):
    """Test ads automation với URL cụ thể."""
    print(f"🚀 Testing ads automation on {serial}")
    print(f"📱 URL: {url}")
    print("🎯 Will try to click element with text 'Learn more'")
    print()

    try:
        title = run_ads_automation(serial, url)
        print(f"✅ SUCCESS: Page title = '{title}'")
        print("🎯 Automation completed (Learn more clicked if found)")

    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_ads.py <ads_url>")
        print("Example: python test_ads.py https://example.com/ads")
        print()
        print("The script will:")
        print("1. Open Chrome on device")
        print("2. Navigate to the URL")
        print("3. Look for element with text 'Learn more'")
        print("4. Click it if found")
        sys.exit(1)

    url = sys.argv[1]
    test_ads_automation(url)