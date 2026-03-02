#!/usr/bin/env python3
"""
Test script for ads automation with modal detection.
"""

import sys
import os
import csv
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import run_ads_automation

def test_ads():
    # Đọc URL từ data.csv
    ads_url = None
    device_serial = None

    try:
        with open('data.csv', 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 3:
                    device_serial = row[1]  # Serial number
                    ads_url = row[2]        # Ads link
                    break
    except FileNotFoundError:
        print("data.csv not found")
        return

    if not ads_url or not device_serial:
        print("No ads URL or device serial found in data.csv")
        return

    try:
        print(f"Testing ads automation on device {device_serial}")
        print(f"Ads URL: {ads_url}")
        result = run_ads_automation(device_serial, ads_url)
        print(f"Test completed. Page title: {result}")
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == "__main__":
    test_ads()
