import subprocess
import typer
from pathlib import Path
from .config import Config, ConfigError
from .device import DeviceManager
from .explorer import ExplorerAgent
from .generator import TestGenerator
from .runner import TestRunner
from .healer import Healer
from .notifier import Notifier

app = typer.Typer(pretty_exceptions_short=True, pretty_exceptions_show_locals=False)


def _load_config(config_file: str) -> Config:
    try:
        return Config.load(config_file)
    except ConfigError as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def explore(
    app_package: str = typer.Option("", "--app", "-a", help="App package to explore"),
    all_apps: bool = typer.Option(False, "--all", help="Explore all apps"),
    config_file: str = typer.Option("aitest.yaml", "--config", "-c"),
):
    """Explore an Android device and generate test scripts"""
    cfg = _load_config(config_file)
    dm = DeviceManager(cfg.devices)
    configured = [d for d in cfg.devices if d.serial]
    devices = (
        dm.discover()
        if not configured
        else configured
    )
    if not devices:
        typer.echo("No devices found", err=True)
        raise typer.Exit(1)
    serial = devices[0].serial
    port = dm.start_appium(serial, devices[0].port)

    if not app_package and not all_apps:
        typer.echo("No app specified (use --app or --all)")
        raise typer.Exit(1)

    if all_apps:
        result = subprocess.run(
            ["adb", "-s", serial, "shell", "pm", "list", "packages", "-3"],
            capture_output=True, text=True,
        )
        candidates = [
            line.split(":", 1)[1].strip()
            for line in result.stdout.strip().split("\n")
            if ":" in line
        ]
        typer.echo(f"Checking {len(candidates)} third-party package(s) for launchable activities...")
        packages = []
        for pkg in candidates:
            check = subprocess.run(
                ["adb", "-s", serial, "shell", "pm", "resolve-activity", "--brief", pkg],
                capture_output=True, text=True,
            )
            if check.returncode == 0 and check.stdout.strip():
                packages.append(pkg)
        if not packages:
            typer.echo("No apps with launchable activities found", err=True)
            raise typer.Exit(1)
        typer.echo(f"Found {len(packages)} app(s) with launchable activities")
        for i, pkg in enumerate(packages[:10], 1):
            typer.echo(f"\n[{i}/{min(len(packages), 10)}] Exploring {pkg}...")
            try:
                _explore_app(cfg, serial, port, pkg)
            except Exception as e:
                typer.echo(f"  Skipping {pkg}: {e}", err=True)
        if len(packages) > 10:
            typer.echo(f"\n{len(packages) - 10} remaining app(s) skipped. Use --app for specific apps.")
        return

    _explore_app(cfg, serial, port, app_package)


@app.command()
def run(
    device: str = typer.Option("", "--device", "-d", help="Device serial"),
    config_file: str = typer.Option("aitest.yaml", "--config", "-c"),
):
    """Run the test suite on connected devices"""
    cfg = _load_config(config_file)
    dm = DeviceManager(cfg.devices)
    configured = [d for d in cfg.devices if d.serial]
    devices = (
        dm.discover()
        if not configured
        else configured
    )
    if device:
        devices = [d for d in devices if d.serial == device]
    if not devices:
        typer.echo("No devices found", err=True)
        raise typer.Exit(1)
    serial = devices[0].serial
    port = dm.start_appium(serial, devices[0].port)
    runner = TestRunner(devices, appium_url=f"http://localhost:{port}")
    results = runner.run_all()
    notifier = Notifier(cfg.notify.webhook)
    failed = notifier.summary(results)
    if failed:
        raise typer.Exit(1)


@app.command()
def heal(
    test_path: str = typer.Argument(..., help="Test file to heal"),
    config_file: str = typer.Option("aitest.yaml", "--config", "-c"),
):
    """Use AI to fix a failing test"""
    test_path = Path(test_path)
    if not test_path.exists():
        typer.echo(f"Test file not found: {test_path}", err=True)
        raise typer.Exit(1)

    cfg = _load_config(config_file)
    healer_agent = Healer(cfg.llm.url, cfg.llm.key, cfg.llm.model)
    typer.echo(f"Analyzing {test_path}...")

    test_code = test_path.read_text()
    import re
    selectors = re.findall(r'["\']([^"\']{5,})["\']\s*\)', test_code)

    if not selectors:
        typer.echo("No selectors found to heal")
        return

    dm = DeviceManager(cfg.devices)
    configured = [d for d in cfg.devices if d.serial]
    devices = (
        dm.discover()
        if not configured
        else configured
    )
    if not devices:
        typer.echo("No devices found", err=True)
        raise typer.Exit(1)
    serial = devices[0].serial
    port = dm.start_appium(serial, devices[0].port)
    typer.echo(f"Connecting to {serial}...")

    from appium import webdriver
    from appium.options.android import UiAutomator2Options

    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.automation_name = "UiAutomator2"
    options.device_name = serial
    options.no_reset = True

    driver = webdriver.Remote(f"http://localhost:{port}", options=options)
    page_source = driver.page_source

    if not selectors:
        typer.echo("No selectors found to heal")
        driver.quit()
        return

    typer.echo(f"Found {len(selectors)} selector(s). Healing...")
    for sel in selectors:
        new_sel = healer_agent.heal_selector(sel, page_source)
        if new_sel and new_sel != sel:
            typer.echo(f"  {sel} -> {new_sel}")
            test_code = test_code.replace(sel, new_sel)

    Path(test_path).write_text(test_code)
    driver.quit()
    typer.echo("Healing complete")


@app.command()
def devices():
    """List connected Android devices"""
    dm = DeviceManager()
    found = dm.discover()
    if not found:
        typer.echo("No devices connected")
        return
    for d in found:
        typer.echo(f"  {d.serial}")


def _explore_app(cfg, serial, port, app_package):
    typer.echo(f"Launching {app_package} on {serial}...")

    activity_result = subprocess.run(
        ["adb", "-s", serial, "shell", "pm", "resolve-activity", "--brief", app_package],
        capture_output=True, text=True,
    )
    app_activity = None
    for line in activity_result.stdout.strip().split("\n"):
        if line.startswith("com.") or line.startswith("android."):
            parts = line.split("/", 1)
            if len(parts) == 2:
                app_activity = parts[1] if parts[1].startswith(".") else "." + parts[1]
            break

    if app_activity:
        subprocess.run(
            ["adb", "-s", serial, "shell", "am", "start", "-n", f"{app_package}/{app_activity.lstrip('.')}"],
            capture_output=True,
        )
    else:
        subprocess.run(
            ["adb", "-s", serial, "shell", "monkey", "-p", app_package, "-c", "android.intent.category.LAUNCHER", "1"],
            capture_output=True,
        )

    from appium import webdriver
    from appium.options.android import UiAutomator2Options

    options = UiAutomator2Options()
    options.platform_name = "Android"
    options.automation_name = "UiAutomator2"
    options.device_name = serial
    options.app_package = app_package
    if app_activity:
        options.app_activity = app_activity
    options.no_reset = True
    options.set_capability("uiautomator2ServerInstallTimeout", 60000)

    driver = webdriver.Remote(f"http://localhost:{port}", options=options)

    explorer = ExplorerAgent(cfg.llm.url, cfg.llm.key, cfg.llm.model)
    typer.echo(f"Exploring {app_package} (max {explorer.max_screens} screens)...")
    screens = explorer.explore_app(driver, app_package)

    driver.quit()
    typer.echo(f"Explored {len(screens)} screens")

    gen = TestGenerator()
    code = gen.generate_test(app_package, screens)
    out_dir = Path("tests/apps")
    out_dir.mkdir(parents=True, exist_ok=True)
    conftest = out_dir / "conftest.py"
    if not conftest.exists():
        conftest.write_text(
            'import os\n'
            'import subprocess\n'
            'import pytest\n'
            'import time\n'
            'from appium import webdriver\n'
            'from appium.options.android import UiAutomator2Options\n'
            '\n'
            '\n'
            'def _adb(serial: str, *args: str) -> subprocess.CompletedProcess:\n'
            '    return subprocess.run(["adb", "-s", serial, *args], capture_output=True, text=True)\n'
            '\n'
            '\n'
            'def _wake_and_unlock(serial: str) -> None:\n'
            '    _adb(serial, "shell", "svc", "power", "stayon", "true")\n'
            '    _adb(serial, "shell", "settings", "put", "system", "screen_off_timeout", "1800000")\n'
            '    _adb(serial, "shell", "input", "keyevent", "KEYCODE_WAKEUP")\n'
            '    _adb(serial, "shell", "input", "keyevent", "KEYCODE_HOME")\n'
            '    _adb(serial, "shell", "wm", "dismiss-keyguard")\n'
            '\n'
            '\n'
            'def _wait_for_focus(serial: str, package_name: str, timeout: float = 10) -> bool:\n'
            '    deadline = time.time() + timeout\n'
            '    while time.time() < deadline:\n'
            '        result = _adb(serial, "shell", "dumpsys", "window")\n'
            '        focus_lines = [\n'
            '            line\n'
            '            for line in result.stdout.splitlines()\n'
            '            if "mCurrentFocus" in line or "mFocusedApp" in line\n'
            '        ]\n'
            '        if any(package_name in line for line in focus_lines):\n'
            '            return True\n'
            '        time.sleep(0.5)\n'
            '    return False\n'
            '\n'
            '\n'
            '@pytest.fixture\n'
            'def driver(request):\n'
            '    serial = os.getenv("ANDROID_SERIAL", "device")\n'
            '    _wake_and_unlock(serial)\n'
            '    marker = request.node.get_closest_marker("app")\n'
            '    app_package = None\n'
            '    if marker:\n'
            '        app_package = marker.args[0]\n'
            '        activity = marker.args[1] if len(marker.args) > 1 and marker.args[1] else ""\n'
            '        launch_cmd = (\n'
            '            ["adb", "-s", serial, "shell", "am", "start", "-n", f"{app_package}/{activity}"]\n'
            '            if activity\n'
            '            else ["adb", "-s", serial, "shell", "monkey", "-p", app_package, "-c", "android.intent.category.LAUNCHER", "1"]\n'
            '        )\n'
            '        subprocess.run(launch_cmd, capture_output=True)\n'
            '        _wait_for_focus(serial, app_package, timeout=3)\n'
            '    options = UiAutomator2Options()\n'
            '    options.platform_name = "Android"\n'
            '    options.automation_name = "UiAutomator2"\n'
            '    options.device_name = serial\n'
            '    if marker:\n'
            '        options.app_package = marker.args[0]\n'
            '        if len(marker.args) > 1 and marker.args[1]:\n'
            '            options.app_activity = marker.args[1]\n'
            '    options.no_reset = True\n'
            '    driver = webdriver.Remote(os.getenv("APPIUM_URL", "http://localhost:4723"), options=options)\n'
            '    try:\n'
            '        if app_package:\n'
            '            driver.activate_app(app_package)\n'
            '            _wait_for_focus(serial, app_package)\n'
            '        yield driver\n'
            '    finally:\n'
            '        subprocess.run(["adb", "-s", serial, "shell", "input", "keyevent", "KEYCODE_HOME"], capture_output=True)\n'
            '        try:\n'
            '            driver.quit()\n'
            '        except Exception:\n'
            '            pass\n'
        )
        typer.echo(f"Created: {conftest}")
    safe_name = app_package.replace(".", "_")
    out_file = out_dir / f"test_{safe_name}.py"
    lines = code.split("\n")
    marker_line = f'@pytest.mark.app("{app_package}"'
    if app_activity:
        marker_line += f', "{app_activity}"'
    marker_line += ")"
    for i, line in enumerate(lines):
        if line.startswith("class Test") and lines[i - 1] != marker_line:
            lines.insert(i, marker_line)
            break
    code = "\n".join(lines)
    out_file.write_text(code)
    typer.echo(f"Generated: {out_file}")


if __name__ == "__main__":
    app()
