import os
import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options


@pytest.fixture
def driver():
    serial = os.getenv("ANDROID_SERIAL", "device")
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.automation_name = "UiAutomator2"
    options.device_name = serial
    options.no_reset = True
    driver = webdriver.Remote(os.getenv("APPIUM_URL", "http://localhost:4723"), options=options)
    try:
        yield driver
    finally:
        try:
            driver.press_keycode(3)
        except Exception:
            pass
        try:
            driver.quit()
        except Exception:
            pass
