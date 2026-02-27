"""
Appium Chrome automation helper.

Yêu cầu:
  - Appium server đang chạy (mặc định http://127.0.0.1:4723)
  - chromedriver tương thích với Chrome version trên device
    (đặt chromedriver.exe cạnh file này, hoặc truyền chromedriver_path)
  - pip install Appium-Python-Client

Cách dùng:
    from utils.appium_chrome import ChromeSession

    with ChromeSession(serial="XXXX", url="https://example.com") as driver:
        el = driver.find_element(by=AppiumBy.XPATH, value='//button[@id="ok"]')
        el.click()
"""

import os
from appium import webdriver
from appium.options.android import UiAutomator2Options

# Default Appium server URL
APPIUM_SERVER = "http://127.0.0.1:4723"

# Đường dẫn chromedriver mặc định (cạnh file này)
_DEFAULT_CHROMEDRIVER = os.path.join(os.path.dirname(__file__), "..", "chromedriver.exe")


def make_chrome_options(
    serial: str,
    chromedriver_path: str = None,
    appium_server: str = APPIUM_SERVER,
) -> UiAutomator2Options:
    """Tạo UiAutomator2Options để kết nối Chrome trên device."""
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.automation_name = "UiAutomator2"
    options.set_capability("deviceName", serial)
    options.set_capability("udid", serial)
    options.set_capability("browserName", "Chrome")
    options.set_capability("chromedriverExecutable",
        os.path.abspath(chromedriver_path or _DEFAULT_CHROMEDRIVER))
    # Không reset app giữa các session
    options.set_capability("noReset", True)
    options.set_capability("fullReset", False)
    return options


def create_session(
    serial: str,
    url: str = None,
    chromedriver_path: str = None,
    appium_server: str = APPIUM_SERVER,
):
    """
    Tạo Appium WebDriver session gắn vào Chrome đang chạy trên device.

    Args:
        serial: ADB serial của device
        url: (tùy chọn) URL để navigate tới sau khi mở session
        chromedriver_path: đường dẫn chromedriver.exe
        appium_server: URL Appium server

    Returns:
        appium.webdriver.Remote instance
    """
    options = make_chrome_options(serial, chromedriver_path, appium_server)
    driver = webdriver.Remote(appium_server, options=options)
    if url:
        if not url.startswith(("http://", "https://")):
            url = "https://" + url
        driver.get(url)
    return driver


class ChromeSession:
    """
    Context manager để tự động đóng session sau khi xong.

    Ví dụ:
        with ChromeSession(serial="XXXX", url="https://example.com") as driver:
            btn = driver.find_element(AppiumBy.ID, "com.android.chrome:id/url_bar")
            print(btn.text)
    """

    def __init__(
        self,
        serial: str,
        url: str = None,
        chromedriver_path: str = None,
        appium_server: str = APPIUM_SERVER,
    ):
        self.serial = serial
        self.url = url
        self.chromedriver_path = chromedriver_path
        self.appium_server = appium_server
        self.driver = None

    def __enter__(self):
        self.driver = create_session(
            self.serial, self.url,
            self.chromedriver_path, self.appium_server
        )
        return self.driver

    def __exit__(self, *_):
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
        self.driver = None
