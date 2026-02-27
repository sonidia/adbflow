#!/usr/bin/env python3
"""
Demo script: Chrome CDP automation examples

Chạy script này để test các tính năng CDP:
    python demo_cdp.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from utils.cdp_chrome import ChromeCDP

def demo_basic_navigation():
    """Demo cơ bản: navigate và lấy title."""
    print("=== Demo 1: Basic Navigation ===")

    with ChromeCDP(serial="223824861c027ece") as cdp:
        cdp.navigate("https://google.com")
        title = cdp.get_page_title()
        print(f"Page title: {title}")

def demo_form_interaction():
    """Demo form: click button và input text."""
    print("\n=== Demo 2: Form Interaction ===")

    with ChromeCDP(serial="223824861c027ece") as cdp:
        # Mở trang demo form
        cdp.navigate("https://httpbin.org/forms/post")

        # Click vào input field và nhập text
        try:
            cdp.click("#custname")  # Focus vào input
            cdp.input_text("#custname", "Test User")
            print("✅ Input text thành công")
        except Exception as e:
            print(f"⚠️  Không tìm thấy element: {e}")

def demo_javascript_execution():
    """Demo JavaScript execution."""
    print("\n=== Demo 3: JavaScript Execution ===")

    with ChromeCDP(serial="223824861c027ece") as cdp:
        cdp.navigate("https://google.com")

        # Execute JavaScript
        result = cdp.execute_js("return document.title + ' - Modified by CDP'")
        print(f"JS result: {result}")

        # Thay đổi background color
        cdp.execute_js("document.body.style.backgroundColor = 'lightblue'")
        print("✅ Thay đổi background thành light blue")

def demo_text_based_click():
    """Demo click element dựa trên text content."""
    print("\n=== Demo 4: Text-based Element Click ===")

    with ChromeCDP(serial="223824861c027ece") as cdp:
        cdp.navigate("https://github.com")

        # Tìm và click element có text chứa "Learn more"
        js_click = """
        const elements = Array.from(document.querySelectorAll('*')).filter(el =>
            el.textContent && el.textContent.trim().toLowerCase().includes('learn more')
        );
        if (elements.length > 0) {
            elements[0].click();
            'clicked';
        } else {
            'not_found';
        }
        """
        result = cdp.execute_js(js_click)
        if result == 'clicked':
            print("✅ Clicked element with text 'Learn more'")
        else:
            print("⚠️  No element with text 'Learn more' found")

if __name__ == "__main__":
    print("🚀 Chrome CDP Demo")
    print("Đảm bảo device đã connect và Chrome đã được cài đặt")
    print()

    try:
        demo_basic_navigation()
        demo_form_interaction()
        demo_javascript_execution()
        demo_text_based_click()

        print("\n🎉 All demos completed successfully!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()