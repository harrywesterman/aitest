import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options


@pytest.fixture
def driver():
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.automation_name = "UiAutomator2"
    options.device_name = "device"
    options.app_package = "com.android.settings"
    options.app_activity = ".Settings"
    options.no_reset = True
    driver = webdriver.Remote("http://localhost:4723", options=options)
    yield driver
    driver.quit()
