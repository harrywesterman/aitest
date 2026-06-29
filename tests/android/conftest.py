import os
import subprocess
import time
import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options


def _adb(serial: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["adb", "-s", serial, *args],
        capture_output=True,
        text=True,
    )


def _wake_and_unlock(serial: str) -> None:
    _adb(serial, "shell", "svc", "power", "stayon", "true")
    _adb(serial, "shell", "settings", "put", "system", "screen_off_timeout", "1800000")
    _adb(serial, "shell", "input", "keyevent", "KEYCODE_WAKEUP")
    _adb(serial, "shell", "input", "keyevent", "KEYCODE_HOME")
    _adb(serial, "shell", "wm", "dismiss-keyguard")


def _wait_for_focus(serial: str, package_name: str, timeout: float = 10) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        result = _adb(serial, "shell", "dumpsys", "window")
        focus_lines = [
            line
            for line in result.stdout.splitlines()
            if "mCurrentFocus" in line or "mFocusedApp" in line
        ]
        if any(package_name in line for line in focus_lines):
            return
        time.sleep(0.5)


@pytest.fixture
def driver():
    serial = os.getenv("ANDROID_SERIAL", "device")
    _wake_and_unlock(serial)
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.automation_name = "UiAutomator2"
    options.device_name = serial
    options.no_reset = True
    driver = webdriver.Remote(os.getenv("APPIUM_URL", "http://localhost:4723"), options=options)
    try:
        yield driver
    finally:
        _adb(serial, "shell", "input", "keyevent", "KEYCODE_HOME")
        try:
            driver.quit()
        except Exception:
            pass


@pytest.fixture
def settings_driver(driver):
    serial = os.getenv("ANDROID_SERIAL", "device")
    _adb(serial, "shell", "am", "start", "-a", "android.settings.SETTINGS")
    _wait_for_focus(serial, "com.android.settings")
    return driver
