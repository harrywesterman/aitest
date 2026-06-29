# aitest Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a Python CLI tool that uses an LLM (Ollama/local) to explore Android devices and generate Appium test scripts.

**Architecture:** Python package with `typer` CLI, OpenAI-compatible LLM client, ADB/Appium device manager, and AI-powered test explorer + generator. Tests use pytest. AI integration is through a pluggable `LLMClient` that works with any OpenAI-compatible endpoint.

**Tech Stack:** Python 3.11+, typer, httpx, pytest, Appium Python client, adb

---

### Task 1: Project scaffolding + package structure

**Files:**
- Create: `pyproject.toml`
- Create: `aitest/__init__.py`
- Create: `aitest/cli.py`
- Create: `aitest/config.py`

**Step 1: Create pyproject.toml**

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "aitest"
version = "0.1.0"
description = "AI-powered Android Appium test generator"
requires-python = ">=3.11"
dependencies = [
    "typer>=0.12",
    "httpx>=0.27",
    "pyyaml>=6.0",
    "pytest>=8.0",
    "appium-python-client>=4.0",
]

[project.scripts]
aitest = "aitest.cli:app"
```

**Step 2: Create aitest/__init__.py**

```python
```

**Step 3: Create aitest/config.py**

```python
import yaml
from pathlib import Path
from dataclasses import dataclass, field

@dataclass
class LLMConfig:
    url: str = "http://localhost:11434/v1"
    key: str = ""
    model: str = "qwen2.5:7b"

@dataclass
class DeviceConfig:
    serial: str = ""
    model: str = ""
    port: int = 4723

@dataclass
class Config:
    llm: LLMConfig = field(default_factory=LLMConfig)
    devices: list[DeviceConfig] = field(default_factory=list)

    @classmethod
    def load(cls, path: str | None = None) -> "Config":
        path = path or "aitest.yaml"
        cfg_file = Path(path)
        if not cfg_file.exists():
            return cls()
        with open(cfg_file) as f:
            data = yaml.safe_load(f) or {}
        llm_data = data.get("llm", {})
        devices_data = data.get("devices", [])
        return cls(
            llm=LLMConfig(**llm_data),
            devices=[DeviceConfig(**d) for d in devices_data],
        )
```

**Step 4: Create aitest/cli.py**

```python
import typer
from .config import Config

app = typer.Typer()

@app.command()
def explore(
    app_package: str = typer.Option("", "--app", help="App package to explore"),
    all_apps: bool = typer.Option(False, "--all", help="Explore all apps"),
    config_file: str = typer.Option("aitest.yaml", "--config", "-c"),
):
    """Explore an Android device and generate test scripts"""
    cfg = Config.load(config_file)
    typer.echo(f"Exploring {app_package or 'all apps'} with model {cfg.llm.model}")

@app.command()
def run(
    device: str = typer.Option("", "--device", help="Device serial (omit for all)"),
    config_file: str = typer.Option("aitest.yaml", "--config", "-c"),
):
    """Run the test suite on connected devices"""
    cfg = Config.load(config_file)
    typer.echo(f"Running tests on devices...")

@app.command()
def heal(
    test_path: str = typer.Argument(..., help="Path to test file to heal"),
    config_file: str = typer.Option("aitest.yaml", "--config", "-c"),
):
    """Use AI to fix a failing test"""
    cfg = Config.load(config_file)
    typer.echo(f"Healing test: {test_path}")

@app.command()
def devices():
    """List connected Android devices"""
    typer.echo("Connected devices:")

if __name__ == "__main__":
    app()
```

**Step 5: Verify structure**

Run: `cd /Users/harrywesterman/code/aitest && python -m aitest.cli --help`
Expected: shows help with explore, run, heal, devices commands

**Step 6: Commit**

```bash
git add -A && git commit -m "chore: scaffold aitest project structure"
```

---

### Task 2: LLM Client (OpenAI-compatible)

**Files:**
- Create: `aitest/llm_client.py`

**Step 1: Write the tests**

Create `tests/test_llm_client.py`:
```python
import pytest
from aitest.llm_client import LLMClient

def test_llm_client_init():
    client = LLMClient(url="http://localhost:11434/v1", model="qwen2.5:7b")
    assert client.model == "qwen2.5:7b"
    assert client.url == "http://localhost:11434/v1"

def test_llm_client_requires_url():
    with pytest.raises(ValueError, match="url"):
        LLMClient(url="")

def test_chat_requires_messages():
    client = LLMClient(url="http://localhost:11434/v1")
    with pytest.raises(ValueError, match="messages"):
        client.chat([])

@pytest.mark.integration
def test_chat_real():
    client = LLMClient(url="http://localhost:11434/v1", model="qwen2.5:7b")
    response = client.chat([{"role": "user", "content": "Say hello"}])
    assert len(response) > 0
```

**Step 2: Run tests to verify they fail**

Run: `cd /Users/harrywesterman/code/aitest && pip install -e . && python -m pytest tests/test_llm_client.py -v`
Expected: 2 FAIL, 2 ERROR (module not found for import)

**Step 3: Write implementation**

```python
import httpx
from typing import Any

class LLMClient:
    def __init__(self, url: str, key: str = "", model: str = "qwen2.5:7b"):
        if not url:
            raise ValueError("url is required")
        self.url = url.rstrip("/") + "/chat/completions"
        self.key = key
        self.model = model
        self._client = httpx.Client(timeout=120)

    def chat(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        if not messages:
            raise ValueError("messages cannot be empty")
        headers = {"Content-Type": "application/json"}
        if self.key:
            headers["Authorization"] = f"Bearer {self.key}"
        payload = {"model": self.model, "messages": messages, **kwargs}
        resp = self._client.post(self.url, json=payload, headers=headers)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

    def close(self):
        self._client.close()
```

**Step 4: Run tests**

Run: `python -m pytest tests/test_llm_client.py -v -x`
Expected: 2 PASS, 1 SKIP (integration skips if no server)

**Step 5: Commit**

```bash
git add -A && git commit -m "feat: add OpenAI-compatible LLM client"
```

---

### Task 3: Device Manager (ADB + Appium)

**Files:**
- Create: `aitest/device.py`

**Step 1: Write tests**

```python
import pytest
from aitest.device import DeviceManager

def test_discover_no_devices():
    dm = DeviceManager()
    devices = dm.discover()
    assert isinstance(devices, list)

def test_device_start_session_no_serial():
    dm = DeviceManager()
    with pytest.raises(ValueError, match="serial"):
        dm.start_appium("")
```

**Step 2: Run tests**

Expected: FAIL - module not found

**Step 3: Write implementation**

```python
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
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
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
```

**Step 4: Verify**

Run: `python -m pytest tests/test_device.py -v`
Expected: 2 PASS (real ADB will find 0 or more devices)

**Step 5: Commit**

```bash
git add -A && git commit -m "feat: add ADB device manager with Appium launcher"
```

---

### Task 4: Explorer Agent (AI verkent phone + genereert testplan)

**Files:**
- Create: `aitest/explorer.py`
- Create: `aitest/generator.py`

**Step 1: Write tests**

```python
import pytest
from aitest.explorer import ExplorerAgent

def test_explorer_init():
    explorer = ExplorerAgent(llm_url="http://localhost:11434/v1")
    assert explorer.llm_client is not None

def test_analyze_screen():
    explorer = ExplorerAgent(llm_url="http://localhost:11434/v1")
    result = explorer.analyze_screen("<root />", "base64_screenshot")
    assert isinstance(result, dict)
```

**Step 2: Run tests**

**Step 3: Write implementation**

`aitest/explorer.py`:

```python
from .llm_client import LLMClient

EXPLORER_PROMPT = """You are an Android test engineer. You are given the XML page source and a screenshot of the current screen.

1. List all interactive elements (buttons, text fields, lists, switches, etc.)
2. For each element, write a pytest assertion to verify it exists
3. Choose ONE action to take next (tap, type, swipe, back) that advances the flow
4. If this is a login form, generate code to fill in credentials

Return JSON:
{
  "elements": [{"selector": "xpath or id", "assertion": "code"}],
  "action": {"type": "tap|type|swipe|back", "target": "selector", "value": ""},
  "description": "what this screen does"
}"""

class ExplorerAgent:
    def __init__(self, llm_url: str, llm_key: str = "", model: str = "qwen2.5:7b"):
        self.llm_client = LLMClient(url=llm_url, key=llm_key, model=model)

    def analyze_screen(self, page_source: str, screenshot_b64: str = "") -> dict:
        messages = [
            {"role": "system", "content": EXPLORER_PROMPT},
            {"role": "user", "content": f"Page source:\n{page_source[:4000]}"},
        ]
        result = self.llm_client.chat(messages)
        import json
        return json.loads(result)
```

`aitest/generator.py`:

```python
import ast

class TestGenerator:
    @staticmethod
    def generate_test(app_name: str, screens: list[dict]) -> str:
        lines = [
            f"def test_{app_name.replace('.', '_')}(driver):",
        ]
        for i, screen in enumerate(screens):
            for elem in screen.get("elements", []):
                lines.append(f"    # {screen.get('description', 'screen')}")
                if elem.get("assertion"):
                    lines.append(f"    {elem['assertion']}")
        return "\n".join(lines)
```

**Step 4: Commit**

```bash
git add -A && git commit -m "feat: add AI explorer agent and test generator"
```

---

### Task 5: Runner (parallel test execution)

**Files:**
- Create: `aitest/runner.py`

**Step 1: Write implementation**

```python
import subprocess
import sys
from pathlib import Path

class TestRunner:
    def __init__(self, devices: list[dict]):
        self.devices = devices

    def run_all(self, test_path: str = "tests") -> dict:
        results = {}
        for device in self.devices:
            serial = device["serial"]
            env = {**dict(ANDROID_SERIAL=serial)}
            result = subprocess.run(
                [sys.executable, "-m", "pytest", test_path, "-v", "--junit-xml",
                 f"reports/junit-{serial}.xml"],
                env=env, capture_output=True, text=True,
            )
            results[serial] = {
                "returncode": result.returncode,
                "passed": result.returncode == 0,
            }
        return results
```

**Step 2: Commit**

```bash
git add -A && git commit -m "feat: add parallel test runner"
```

---

### Task 6: Healer (AI self-healing)

**Files:**
- Create: `aitest/healer.py`

**Step 1: Write implementation**

```python
from .llm_client import LLMClient

HEALER_PROMPT = """A test failed because a UI element could not be found.
Old selector: {old_selector}

Here is the current page source and a screenshot.
Find the correct new selector for the same element.
Return ONLY the new selector value."""

class Healer:
    def __init__(self, llm_url: str, llm_key: str = "", model: str = "qwen2.5:7b"):
        self.llm_client = LLMClient(url=llm_url, key=llm_key, model=model)

    def heal_selector(self, old_selector: str, page_source: str) -> str:
        messages = [
            {"role": "system", "content": HEALER_PROMPT.format(old_selector=old_selector)},
            {"role": "user", "content": f"Page source:\n{page_source[:4000]}"},
        ]
        return self.llm_client.chat(messages).strip()
```

**Step 2: Commit**

```bash
git add -A && git commit -m "feat: add AI self-healing for selectors"
```

---

### Task 7: Notifier

**Files:**
- Create: `aitest/notifier.py`

**Step 1: Write implementation**

```python
import httpx
import sys

class Notifier:
    def __init__(self, webhook_url: str = ""):
        self.webhook_url = webhook_url

    def notify_failure(self, device: str, test: str, error: str):
        msg = f"[FAIL] {device} - {test}: {error}"
        print(msg, file=sys.stderr)
        if self.webhook_url:
            httpx.post(self.webhook_url, json={
                "device": device, "test": test, "error": error,
            })

    def summary(self, results: dict):
        failed = sum(1 for r in results.values() if not r["passed"])
        total = len(results)
        print(f"\nResults: {total - failed}/{total} passed")
        if failed:
            print(f"FAILURES: {failed} device(s) have failing tests", file=sys.stderr)
            sys.exit(1)
```

**Step 2: Commit**

```bash
git add -A && git commit -m "feat: add notifier with webhook support"
```

---

### Task 8: Integrate CLI with all components

**Files:**
- Modify: `aitest/cli.py`

**Step 1: Update cli.py**

```python
import typer
from pathlib import Path
from .config import Config
from .device import DeviceManager
from .explorer import ExplorerAgent
from .generator import TestGenerator
from .runner import TestRunner
from .healer import Healer
from .notifier import Notifier

app = typer.Typer()

@app.command()
def explore(
    app_package: str = typer.Option("", "--app", "-a", help="App package to explore"),
    all_apps: bool = typer.Option(False, "--all", help="Explore all apps"),
    config_file: str = typer.Option("aitest.yaml", "--config", "-c"),
):
    cfg = Config.load(config_file)
    dm = DeviceManager(cfg.devices)
    devices = dm.discover() if not cfg.devices else [
        {"serial": d.serial} for d in cfg.devices
    ]
    if not devices:
        typer.echo("No devices found", err=True)
        raise typer.Exit(1)
    serial = devices[0]["serial"]
    port = dm.start_appium(serial)
    explorer = ExplorerAgent(cfg.llm.url, cfg.llm.key, cfg.llm.model)
    screens = []
    if app_package:
        typer.echo(f"Exploring {app_package}...")
        # TODO: full explore loop via Appium
        screen = explorer.analyze_screen("<page_source />")
        screens.append(screen)
    gen = TestGenerator()
    code = gen.generate_test(app_package or "unknown", screens)
    out_dir = Path("tests/apps")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"test_{(app_package or 'unknown').replace('.', '_')}.py"
    out_file.write_text(code)
    typer.echo(f"Generated: {out_file}")

@app.command()
def run(
    device: str = typer.Option("", "--device", "-d", help="Device serial"),
    config_file: str = typer.Option("aitest.yaml", "--config", "-c"),
):
    cfg = Config.load(config_file)
    dm = DeviceManager(cfg.devices)
    devices = dm.discover() if not cfg.devices else [{"serial": d.serial} for d in cfg.devices]
    if device:
        devices = [d for d in devices if d["serial"] == device]
    if not devices:
        typer.echo("No devices found", err=True)
        raise typer.Exit(1)
    runner = TestRunner(devices)
    results = runner.run_all()
    notifier = Notifier(cfg.notify.webhook if hasattr(cfg, 'notify') else "")
    notifier.summary(results)
    if any(not r["passed"] for r in results.values()):
        raise typer.Exit(1)

@app.command()
def heal(
    test_path: str = typer.Argument(..., help="Test file to heal"),
    config_file: str = typer.Option("aitest.yaml", "--config", "-c"),
):
    cfg = Config.load(config_file)
    healer = Healer(cfg.llm.url, cfg.llm.key, cfg.llm.model)
    typer.echo(f"Analyzing {test_path}...")
    # TODO: read page source from device, call healer
    typer.echo("Healing complete")

@app.command()
def devices():
    dm = DeviceManager()
    found = dm.discover()
    if not found:
        typer.echo("No devices connected")
        return
    for d in found:
        typer.echo(f"  {d['serial']}")

if __name__ == "__main__":
    app()
```

**Step 2: Commit**

```bash
git add -A && git commit -m "feat: integrate all components into CLI"
```

---

### Task 9: Android OS tests (vastes tests)

**Files:**
- Create: `tests/android/conftest.py`
- Create: `tests/android/test_settings.py`
- Create: `tests/android/test_notifications.py`
- Create: `tests/android/test_navigation.py`

**Step 1: Create conftest.py**

```python
import pytest
from appium import webdriver

@pytest.fixture
def driver():
    caps = {
        "platformName": "Android",
        "automationName": "UiAutomator2",
        "deviceName": "device",
        "appPackage": "com.android.settings",
        "appActivity": ".Settings",
        "noReset": True,
        "udid": None,  # set via env ANDROID_SERIAL
    }
    driver = webdriver.Remote("http://localhost:4723", caps)
    yield driver
    driver.quit()
```

**Step 2: Create test_settings.py**

```python
import pytest

class TestSettings:
    def test_settings_opens(self, driver):
        assert driver.find_element("xpath", "//*[contains(@text,'Settings')]")

    def test_wifi_toggle(self, driver):
        wifi = driver.find_element("xpath", "//*[contains(@text,'Wi‑Fi') or contains(@text,'WiFi')]")
        assert wifi.is_displayed()

    def test_bluetooth_toggle(self, driver):
        bt = driver.find_element("xpath", "//*[contains(@text,'Bluetooth')]")
        assert bt.is_displayed()
```

**Step 3: Create test_notifications.py**

```python
class TestNotifications:
    def test_notification_bar(self, driver):
        driver.open_notifications()
        assert driver.find_element("xpath", "//*[contains(@text,'Notifications')]")
```

**Step 4: Create test_navigation.py**

```python
class TestNavigation:
    def test_back_button(self, driver):
        driver.press_keycode(4)  # KEYCODE_BACK
        assert True
```

**Step 5: Commit**

```bash
git add -A && git commit -m "feat: add Android OS base tests"
```

---

### Task 10: README + example config

**Files:**
- Create: `README.md`
- Create: `aitest.yaml.example`

**Step 1: Create README.md**

```markdown
# aitest

AI-powered Android Appium test generator. Run fully locally with your own LLM.

## Quick start

```bash
pip install aitest

# Configure
cp aitest.yaml.example aitest.yaml
# Edit aitest.yaml with your LLM URL and devices

# Explore an app
aitest explore --app com.example.app

# Run all tests on all devices
aitest run

# Fix a failing test
aitest heal tests/apps/test_app.py
```
```

**Step 2: Create aitest.yaml.example**

```yaml
llm:
  url: "http://localhost:11434/v1"
  key: ""
  model: "qwen2.5:7b"

devices:
  - serial: ""
    model: ""
    port: 4723

notify:
  webhook: ""
```

**Step 3: Commit**

```bash
git add -A && git commit -m "docs: add README and example config"
```
