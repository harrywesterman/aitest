import os
import subprocess
import sys
from .config import DeviceConfig


class TestRunner:
    __test__ = False
    SCREEN_TIMEOUT_MS = "1800000"

    def __init__(self, devices: list[DeviceConfig], appium_url: str = "http://localhost:4723"):
        self.devices = devices
        self.appium_url = appium_url

    def run_all(self, test_path: str | list[str] = "tests", marker: str = "appium") -> dict:
        results = {}
        test_paths = [test_path] if isinstance(test_path, str) else list(test_path)
        for device in self.devices:
            serial = device.serial
            original_screen_timeout = self._screen_timeout(serial)
            self._keep_awake(serial)
            env = {
                **os.environ,
                "ANDROID_SERIAL": serial,
                "APPIUM_URL": self.appium_url,
            }
            cmd = [
                sys.executable,
                "-m",
                "pytest",
                *test_paths,
                "-v",
            ]
            if marker:
                cmd.extend(["-m", marker])
            cmd.extend([
                "--junit-xml",
                f"reports/junit-{serial}.xml",
            ])
            try:
                result = subprocess.run(
                    cmd,
                    env=env,
                    capture_output=True,
                    text=True,
                )
            finally:
                self._adb(serial, "shell", "input", "keyevent", "KEYCODE_HOME")
                if original_screen_timeout:
                    self._set_screen_timeout(serial, original_screen_timeout)
            results[serial] = {
                "returncode": result.returncode,
                "passed": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
            }
        return results

    @staticmethod
    def _adb(serial: str, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["adb", "-s", serial, *args],
            capture_output=True,
            text=True,
        )

    @classmethod
    def _screen_timeout(cls, serial: str) -> str:
        result = cls._adb(serial, "shell", "settings", "get", "system", "screen_off_timeout")
        value = result.stdout.strip()
        return value if value.isdigit() else ""

    @classmethod
    def _set_screen_timeout(cls, serial: str, value: str) -> None:
        cls._adb(serial, "shell", "settings", "put", "system", "screen_off_timeout", value)

    @classmethod
    def _keep_awake(cls, serial: str) -> None:
        cls._adb(serial, "shell", "svc", "power", "stayon", "true")
        cls._set_screen_timeout(serial, cls.SCREEN_TIMEOUT_MS)
        cls._adb(serial, "shell", "input", "keyevent", "KEYCODE_WAKEUP")
        cls._adb(serial, "shell", "wm", "dismiss-keyguard")
