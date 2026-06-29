import httpx
import sys


class Notifier:
    def __init__(self, webhook_url: str = ""):
        self.webhook_url = webhook_url

    def notify_failure(self, device: str, test: str, error: str):
        msg = f"[FAIL] {device} - {test}: {error}"
        print(msg, file=sys.stderr)
        if self.webhook_url:
            httpx.post(
                self.webhook_url,
                json={"device": device, "test": test, "error": error},
            )

    def summary(self, results: dict) -> int:
        failed = sum(1 for r in results.values() if not r["passed"])
        total = len(results)
        print(f"\nResults: {total - failed}/{total} passed")
        if failed:
            print(f"FAILURES: {failed} device(s) have failing tests", file=sys.stderr)
        return failed
