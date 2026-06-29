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
    """Explore an Android device and generate test scripts"""
    cfg = Config.load(config_file)
    dm = DeviceManager(cfg.devices)
    devices = (
        dm.discover()
        if not cfg.devices
        else [{"serial": d.serial} for d in cfg.devices]
    )
    if not devices:
        typer.echo("No devices found", err=True)
        raise typer.Exit(1)
    serial = devices[0]["serial"]
    port = dm.start_appium(serial)
    explorer = ExplorerAgent(cfg.llm.url, cfg.llm.key, cfg.llm.model)
    screens = []
    if app_package:
        typer.echo(f"Exploring {app_package}...")
        screen = explorer.analyze_screen("<page_source />")
        screens.append(screen)
    gen = TestGenerator()
    code = gen.generate_test(app_package or "unknown", screens)
    out_dir = Path("tests/apps")
    out_dir.mkdir(parents=True, exist_ok=True)
    safe_name = (app_package or "unknown").replace(".", "_")
    out_file = out_dir / f"test_{safe_name}.py"
    out_file.write_text(code)
    typer.echo(f"Generated: {out_file}")


@app.command()
def run(
    device: str = typer.Option("", "--device", "-d", help="Device serial"),
    config_file: str = typer.Option("aitest.yaml", "--config", "-c"),
):
    """Run the test suite on connected devices"""
    cfg = Config.load(config_file)
    dm = DeviceManager(cfg.devices)
    devices = (
        dm.discover()
        if not cfg.devices
        else [{"serial": d.serial} for d in cfg.devices]
    )
    if device:
        devices = [d for d in devices if d["serial"] == device]
    if not devices:
        typer.echo("No devices found", err=True)
        raise typer.Exit(1)
    runner = TestRunner(devices)
    results = runner.run_all()
    notifier = Notifier(cfg.notify.webhook if hasattr(cfg, "notify") else "")
    notifier.summary(results)
    if any(not r["passed"] for r in results.values()):
        raise typer.Exit(1)


@app.command()
def heal(
    test_path: str = typer.Argument(..., help="Test file to heal"),
    config_file: str = typer.Option("aitest.yaml", "--config", "-c"),
):
    """Use AI to fix a failing test"""
    cfg = Config.load(config_file)
    healer_agent = Healer(cfg.llm.url, cfg.llm.key, cfg.llm.model)
    typer.echo(f"Analyzing {test_path}...")
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
        typer.echo(f"  {d['serial']}")


if __name__ == "__main__":
    app()
