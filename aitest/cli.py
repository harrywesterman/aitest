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
