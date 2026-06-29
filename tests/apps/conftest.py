import os
import subprocess
import time
import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options


@pytest.fixture
def driver(request):
    serial = os.getenv("ANDROID_SERIAL", "device")
    subprocess.run(["adb", "-s", serial, "shell", "svc", "power", "stayon", "true"], capture_output=True)
    subprocess.run(["adb", "-s", serial, "shell", "settings", "put", "system", "screen_off_timeout", "1800000"], capture_output=True)
    subprocess.run(["adb", "-s", serial, "shell", "input", "keyevent", "KEYCODE_WAKEUP"], capture_output=True)
    subprocess.run(["adb", "-s", serial, "shell", "input", "keyevent", "KEYCODE_HOME"], capture_output=True)
    subprocess.run(["adb", "-s", serial, "shell", "wm", "dismiss-keyguard"], capture_output=True)
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
        for _ in range(30):
            subprocess.run(launch_cmd, capture_output=True)
            r = subprocess.run(
                ["adb", "-s", serial, "shell", "dumpsys", "window"],
                capture_output=True, text=True,
            )
            for line in r.stdout.split("\n"):
                if "mCurrentFocus" in line and app_package in line:
                    break
            else:
                time.sleep(0.5)
                continue
            break
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
        yield driver
    finally:
        subprocess.run(["adb", "-s", serial, "shell", "input", "keyevent", "KEYCODE_HOME"], capture_output=True)
        try:
            driver.quit()
        except Exception:
            pass
