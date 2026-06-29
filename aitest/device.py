import os
import subprocess
import socket
import time
import urllib.error
import urllib.request
from .config import DeviceConfig


class DeviceManager:
    def __init__(self, devices: list[DeviceConfig] | None = None):
        self.devices = devices or []

    def discover(self) -> list[DeviceConfig]:
        result = subprocess.run(
            ["adb", "devices"], capture_output=True, text=True
        )
        if result.returncode != 0:
            return []
        lines = result.stdout.strip().split("\n")[1:]
        found = []
        for line in lines:
            if line.strip() and "device" in line and "offline" not in line:
                serial = line.split("\t")[0]
                found.append(DeviceConfig(serial=serial))
        return found

    def start_appium(self, serial: str, port: int = 4723) -> int:
        if not serial:
            raise ValueError("serial is required")

        if self._port_in_use(port):
            if self._appium_ready(port):
                return port
            port = self._find_free_port(port + 1)

        env = {**os.environ, "ANDROID_HOME": os.environ.get("ANDROID_HOME", "/opt/homebrew/share/android-commandlinetools")}
        subprocess.Popen(
            ["appium", "-p", str(port), "--relaxed-security"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            env=env,
        )

        if not self._wait_for_appium(port):
            raise RuntimeError(f"Appium failed to start on port {port}")

        return port

    @staticmethod
    def _port_in_use(port: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(("127.0.0.1", port)) == 0

    @staticmethod
    def _find_free_port(start: int) -> int:
        port = start
        while port < 65535:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                if s.connect_ex(("127.0.0.1", port)) != 0:
                    return port
            port += 1
        raise RuntimeError("no free ports available")

    @staticmethod
    def _wait_for_appium(port: int, timeout: int = 15) -> bool:
        start = time.time()
        while time.time() - start < timeout:
            if DeviceManager._appium_ready(port):
                return True
            time.sleep(0.5)
        return False

    @staticmethod
    def _appium_ready(port: int) -> bool:
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/status", timeout=1) as response:
                return response.status == 200
        except (OSError, urllib.error.URLError):
            return False
