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


def _wait_for_focus(serial: str, package_name: str, timeout: float = 10) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        result = _adb(serial, "shell", "dumpsys", "window")
        focus_lines = [
            line
            for line in result.stdout.splitlines()
            if "mCurrentFocus" in line or "mFocusedApp" in line
        ]
        if any(package_name in line for line in focus_lines):
            return True
        time.sleep(0.5)
    return False


@pytest.fixture
def driver(request):
    serial = os.getenv("ANDROID_SERIAL", "device")
    _wake_and_unlock(serial)
    marker = request.node.get_closest_marker("app")
    app_package = None
    if marker:
        app_package = marker.args[0]
        activity = marker.args[1] if len(marker.args) > 1 and marker.args[1] else ""
        launch_cmd = (
            ["adb", "-s", serial, "shell", "am", "start", "-n", f"{app_package}/{activity}"]
            if activity
            else ["adb", "-s", serial, "shell", "monkey", "-p", app_package, "-c", "android.intent.category.LAUNCHER", "1"]
        )
        subprocess.run(launch_cmd, capture_output=True)
        _wait_for_focus(serial, app_package, timeout=3)
    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.automation_name = "UiAutomator2"
    options.device_name = serial
    if marker:
        options.app_package = marker.args[0]
        if len(marker.args) > 1 and marker.args[1]:
            options.app_activity = marker.args[1]
    options.no_reset = True
    driver = webdriver.Remote(os.getenv("APPIUM_URL", "http://localhost:4723"), options=options)
    try:
        if app_package:
            driver.activate_app(app_package)
            _wait_for_focus(serial, app_package)
        yield driver
    finally:
        subprocess.run(["adb", "-s", serial, "shell", "input", "keyevent", "KEYCODE_HOME"], capture_output=True)
        try:
            driver.quit()
        except Exception:
            pass
