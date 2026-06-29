import subprocess
import sys


class TestRunner:
    __test__ = False
    def __init__(self, devices: list[dict]):
        self.devices = devices

    def run_all(self, test_path: str = "tests") -> dict:
        results = {}
        for device in self.devices:
            serial = device["serial"]
            env = {**os.environ, "ANDROID_SERIAL": serial}
            result = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    test_path,
                    "-v",
                    "--junit-xml",
                    f"reports/junit-{serial}.xml",
                ],
                env=env,
                capture_output=True,
                text=True,
            )
            results[serial] = {
                "returncode": result.returncode,
                "passed": result.returncode == 0,
            }
        return results
