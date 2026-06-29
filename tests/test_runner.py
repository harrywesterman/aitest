from unittest.mock import patch, MagicMock
from aitest.runner import TestRunner
from aitest.config import DeviceConfig


def _fake_run(pytest_returncode=0):
    def run(args, **kwargs):
        if "pytest" in args:
            return MagicMock(returncode=pytest_returncode, stdout="pytest out", stderr="")
        if args[-3:] == ["get", "system", "screen_off_timeout"]:
            return MagicMock(returncode=0, stdout="600000", stderr="")
        return MagicMock(returncode=0, stdout="", stderr="")

    return run


def _pytest_calls(mock_run):
    return [
        call
        for call in mock_run.call_args_list
        if "pytest" in call.args[0]
    ]


def test_runner_init():
    runner = TestRunner([DeviceConfig(serial="test123")])
    assert len(runner.devices) == 1
    assert runner.devices[0].serial == "test123"


@patch("aitest.runner.subprocess.run")
def test_run_all(mock_run):
    mock_run.side_effect = _fake_run(pytest_returncode=0)

    runner = TestRunner([DeviceConfig(serial="abc"), DeviceConfig(serial="def")])
    results = runner.run_all()

    assert "abc" in results
    assert "def" in results
    assert results["abc"]["passed"] is True
    assert results["def"]["passed"] is True
    assert len(_pytest_calls(mock_run)) == 2


@patch("aitest.runner.subprocess.run")
def test_run_all_failure(mock_run):
    mock_run.side_effect = _fake_run(pytest_returncode=1)

    runner = TestRunner([DeviceConfig(serial="abc")])
    results = runner.run_all()

    assert results["abc"]["passed"] is False
    assert results["abc"]["returncode"] == 1


@patch("aitest.runner.subprocess.run")
def test_run_all_sets_env(mock_run):
    mock_run.side_effect = _fake_run(pytest_returncode=0)

    runner = TestRunner([DeviceConfig(serial="xyz")], appium_url="http://localhost:4724")
    runner.run_all()

    pytest_call = _pytest_calls(mock_run)[0]
    env = pytest_call.kwargs["env"]
    assert env["ANDROID_SERIAL"] == "xyz"
    assert env["APPIUM_URL"] == "http://localhost:4724"
    assert "-m" in pytest_call.args[0]
    assert "appium" in pytest_call.args[0]
