import subprocess
import socket
import time
from .config import DeviceConfig


class DeviceManager:
    def __init__(self, devices: list[DeviceConfig] | None = None):
        self.devices = devices or []

    def discover(self) -> list[dict]:
        result = subprocess.run(
            ["adb", "devices"], capture_output=True, text=True
        )
        lines = result.stdout.strip().split("\n")[1:]
        found = []
        for line in lines:
            if line.strip() and "device" in line and "offline" not in line:
                serial = line.split("\t")[0]
                found.append({"serial": serial})
        return found

    def start_appium(self, serial: str, port: int = 4723) -> int:
        if not serial:
            raise ValueError("serial is required")
        appium_port = self._find_free_port(port)
        subprocess.Popen(
            ["appium", "-p", str(appium_port), "--relaxed-security"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        time.sleep(3)
        return appium_port

    @staticmethod
    def _find_free_port(start: int) -> int:
        port = start
        while True:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                if s.connect_ex(("127.0.0.1", port)) != 0:
                    return port
            port += 1
