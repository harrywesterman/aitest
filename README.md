# aitest

AI-powered Android Appium test generator. Runs fully locally with your own LLM.

**The problem:** You manage a fleet of 10,000+ Android devices with pre-installed apps. When Android updates, apps update, or new phone models arrive, you need to know if everything still works. Writing and maintaining Appium tests by hand doesn't scale.

**The solution:** aitest uses a local LLM (via Ollama or any OpenAI-compatible API) to autonomously explore Android devices, generate a comprehensive pytest + Appium test suite, and self-heal when UI changes break tests.

## Features

- **Autonomous exploration** — AI explores your device and apps, discovers UI elements, and generates test scripts
- **Batch explore** — `aitest explore --all` discovers all third-party apps with launchable activities and generates tests for each
- **LLM-agnostic** — works with Ollama, LM Studio, vLLM, OpenAI, or any OpenAI-compatible API
- **Sequential execution** — runs tests across multiple USB-connected devices one at a time with JUnit XML output
- **Self-healing** — when a test fails due to a UI change, AI finds the new selector automatically
- **Android OS tests** — built-in tests for Android system functions (Settings, notifications, navigation)
- **Trigger-ready** — designed to run on Android update, app update, or new device model
- **Fully local** — no cloud dependencies, everything runs on your network

## Architecture

```
┌─────────────────────────────────────────────────┐
│                     CLI                          │
│  aitest explore   aitest run   aitest heal      │
└────────┬───────────────────────────┬────────────┘
         ▼                           ▼
┌─────────────────┐    ┌──────────────────────────┐
│  LLM Client      │    │  Device Manager           │
│  (OpenAI compat) │    │  ─ ADB discovery          │
│  ─ url + api_key │    │  ─ Appium lifecycle       │
│  ─ model keuze   │    │  ─ adaptive port polling  │
└────────┬─────────┘    └───────────┬──────────────┘
         │                          │
         ▼                          ▼
┌─────────────────┐    ┌──────────────────────────┐
│  Explorer Agent  │    │  Test Runner              │
│  ─ explores phone│    │  ─ pytest sequential      │
│  ─ builds screens│    │  ─ JUnit XML output       │
│  ─ generates .py │    │  ─ per-device env         │
└─────────────────┘    └───────────┬──────────────┘
                                   │
                                   ▼
                         ┌──────────────────────────┐
                         │  Notifier                 │
                         │  ─ CLI exit code          │
                         │  ─ webhook                │
                         └──────────────────────────┘
```

## Quick Start

### 1. Prerequisites

Install all required tools via Homebrew:

```bash
# Appium server (mobile device automation)
brew install appium

# Android SDK command-line tools (includes ANDROID_HOME)
brew install --cask android-commandlinetools

# Android platform tools (includes adb, fastboot)
brew install --cask android-platform-tools
```

Set the `ANDROID_HOME` environment variable. Add this to your `~/.zshrc` or `~/.bashrc`:

```bash
export ANDROID_HOME=/opt/homebrew/share/android-commandlinetools
```

Then start Appium and install the Android UiAutomator2 driver:

```bash
# Start the Appium server (runs on port 4723 by default)
brew services start appium

# Install the Android UiAutomator2 driver (needed for Android automation)
appium driver install uiautomator2
```

> **Enable USB debugging** on your Android device:
> 1. Open *Settings → About phone* and tap *Build number* 7 times to enable Developer options
> 2. Go to *Settings → System → Developer options*
> 3. Enable **USB debugging**
> 4. Connect your phone via USB and accept the debugging authorization prompt
> 5. Verify with: `adb devices` — your device serial should appear

### 2. Install

```bash
git clone https://github.com/harrywesterman/aitest.git
cd aitest
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 3. Configure

```bash
cp aitest.yaml.example aitest.yaml
```

Edit `aitest.yaml`:

```yaml
llm:
  # Your LLM server (Ollama, vLLM, LM Studio, OpenAI, etc.)
  # For Ollama: http://ollama-server.lan:11434/v1
  # For OpenAI: https://api.openai.com/v1
  url: "http://localhost:11434/v1"
  key: ""                          # leave empty for Ollama
  model: "qwen2.5:7b"             # or "gpt-4", "llama3:8b", etc.

devices:
  # Leave empty to auto-discover via ADB
  - serial: "R58N910xxx1"
    model: "Samsung Galaxy S24"
    port: 4723
  - serial: "R58N910xxx2"
    model: "Pixel 8"
    port: 4724

notify:
  webhook: "https://hooks.example.com/fail"   # optional
```

### 4. List connected devices

```bash
aitest devices
```

Example output:
```
  4a0aeefb
```

### 5. Explore an app

```bash
aitest explore --app com.android.settings
```

The AI connects to the device, opens the app, analyzes each screen, and generates test scripts in `tests/apps/`.

### 6. Run all tests

```bash
aitest run
```

Runs the full test suite on all connected devices sequentially. Output:

```
Results: 23/24 passed
FAILURES: 1 device(s) have failing tests
```

## CLI Commands

### `aitest explore`

Explore an Android device and generate test scripts.

```
aitest explore --app com.example.app          # explore one app
aitest explore --all                           # explore all installed apps (max 10)
aitest explore --app com.example.app -c prod.yaml  # use custom config
```

Use `--all` to auto-discover every third-party app with a launchable activity and generate tests for each. Non-launchable packages are skipped gracefully.

### `aitest run`

Run the test suite on connected devices.

```
aitest run                                     # all devices
aitest run --device R58N910xxx1                # single device
aitest run --device R58N910xxx1 -c prod.yaml   # custom config
```

Returns exit code 0 if all tests pass, 1 if any fail.

### `aitest heal`

Use AI to fix a failing test by finding the new UI selector. Connects to the device, captures the current page source, and replaces outdated selectors in the test file.

```
aitest heal tests/apps/test_com_example_app.py
```

### `aitest devices`

List connected Android devices via ADB.

```
aitest devices
```

## Test Suite Structure

```
tests/
├── conftest.py            # Shared Appium driver fixture (uses ANDROID_SERIAL)
├── android/               # Hand-crafted Android OS tests
│   ├── conftest.py        # Settings-specific driver override
│   ├── test_settings.py   # WiFi, Bluetooth, display, sound
│   ├── test_notifications.py
│   └── test_navigation.py
│
├── apps/                  # AI-generated app tests
│   ├── conftest.py        # Generated driver fixture (auto-created by explore)
│   ├── test_com_android_deskclock.py
│   ├── test_com_miui_calculator.py
│   └── ...
│
├── test_device.py         # Device discovery, Appium lifecycle tests
├── test_explorer.py       # XML compression, LLM analysis, markdown parsing
├── test_generator.py      # Action code generation, class naming
├── test_healer.py         # Selector healing with/without screenshot
├── test_llm_client.py     # LLM API client init, validation
├── test_notifier.py       # Failure reporting, summary output
└── test_runner.py         # Multi-device test execution, env handling
```

### Android OS Tests

These test core Android functions and work across all devices:

- **Settings** — opens, WiFi toggle, Bluetooth toggle
- **Notifications** — notification bar opens and displays
- **Navigation** — back button, home, recent apps

Add your own by creating files in `tests/android/`.

### AI-Generated App Tests

The Explorer Agent generates these by:

1. Opening the app on the device
2. Capturing the page source (XML hierarchy)
3. Compressing the XML to relevant attributes (resource-id, text, content-desc, clickable)
4. Sending the compressed XML to the LLM for analysis
5. Generating pytest assertions for stable UI elements only (ignoring dynamic values like times, dates, counters)
6. Choosing the next action (tap, type, back) based on LLM recommendations
7. Repeating until the app is fully explored or duplicate screens are detected

Test plans for each explored app are documented in `docs/plans/`.

## AI Exploration Flow

```
1. App openen via ADB (am start / monkey)
   ↓
2. Page source (XML) ophalen via Appium
   ↓
3. XML comprimeren: alleen relevante attributen
   ↓
4. LLM analyseert:
   - "Dit is een login scherm"
   - Elementen: email field, password field, login button
   ↓
5. Genereert pytest code voor dit scherm:
   - Asserties: elk stabiel element is zichtbaar
   - Gebruik ANDROID_UIAUTOMATOR voor text, ID voor resource-id
   ↓
6. LLM kiest actie: "tik op login → kijk wat er gebeurt"
   ↓
7. Nieuw scherm → herhaal stap 2-6
   ↓
8. Einde (max 10 screens, duplicate detectie, of terminate)
   → tests/apps/app_naam.py
```

## Self-Healing Flow

When a test fails after an app update:

```
1. Test faalt (resource-id van login knop is veranderd)
   ↓
2. AI leest testbestand, extraheert alle selectors
   ↓
3. Maakt verbinding met device, captureert page source (+ optioneel screenshot)
   ↓
4. LLM: "vind een nieuwe selector voor hetzelfde element"
   ↓
5. AI stelt nieuwe selector voor per falend element
   ↓
6. Test code wordt geüpdatet met nieuwe selectors
```

## Use Cases

### Android OS Update

```bash
# After OTA update lands on test devices:
aitest run
# If something broke, heal it:
aitest heal tests/android/test_settings.py
```

### App Update

```bash
# After app v2.1 is installed on devices:
aitest explore --app com.example.app   # re-explore
aitest run                              # verify everything works
```

### New Phone Model

```bash
# Connect the new phone via USB
aitest devices
# Add its serial to aitest.yaml
aitest run                              # run the full suite
```

## Development

```bash
git clone https://github.com/harrywesterman/aitest.git
cd aitest
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

# Run unit tests (skip integration and Appium tests)
python -m pytest tests/ -v -m "not integration and not appium"

# Run all tests (requires LLM server + Appium)
python -m pytest tests/ -v
```

## Project Structure

```
aitest/
├── aitest/                  # Python package
│   ├── cli.py              # typer CLI (explore, run, heal, devices)
│   ├── config.py           # YAML config loader + ConfigError
│   ├── llm_client.py       # OpenAI-compatible API client
│   ├── device.py           # ADB discovery + Appium lifecycle (adaptive polling)
│   ├── explorer.py         # AI agent that explores phone/apps
│   ├── generator.py        # screen data → pytest code generator
│   ├── runner.py           # Sequential test executor (per device)
│   ├── healer.py           # AI self-healing for selectors (with screenshot support)
│   └── notifier.py         # Webhook + CLI exit code reporting
├── tests/                  # Test suite (40+ unit tests, ~70% module coverage)
│   ├── conftest.py         # Shared Appium driver fixture
│   ├── android/            # Hand-crafted Android OS tests
│   └── apps/               # AI-generated app tests
├── docs/plans/             # Design docs and app test plans
├── pyproject.toml
├── aitest.yaml.example
└── README.md
```

## Configuration Reference

### `aitest.yaml`

| Key | Description | Default |
|-----|-------------|---------|
| `llm.url` | OpenAI-compatible API endpoint | `http://localhost:11434/v1` |
| `llm.key` | API key (empty for Ollama) | `""` |
| `llm.model` | Model name | `qwen2.5:7b` |
| `devices[].serial` | Android device serial (from ADB) | `""` |
| `devices[].model` | Human-readable device model | `""` |
| `devices[].port` | Appium server port | `4723` |
| `notify.webhook` | URL for failure notifications | `""` |
