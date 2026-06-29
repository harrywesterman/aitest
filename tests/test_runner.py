from unittest.mock import patch, MagicMock
from aitest.runner import TestRunner
from aitest.config import DeviceConfig


def test_runner_init():
    runner = TestRunner([DeviceConfig(serial="test123")])
    assert len(runner.devices) == 1
    assert runner.devices[0].serial == "test123"


@patch("aitest.runner.subprocess.run")
def test_run_all(mock_run):
    mock_run.return_value = MagicMock(returncode=0)

    runner = TestRunner([DeviceConfig(serial="abc"), DeviceConfig(serial="def")])
    results = runner.run_all()

    assert "abc" in results
    assert "def" in results
    assert results["abc"]["passed"] is True
    assert results["def"]["passed"] is True
    assert mock_run.call_count == 2


@patch("aitest.runner.subprocess.run")
def test_run_all_failure(mock_run):
    mock_run.return_value = MagicMock(returncode=1)

    runner = TestRunner([DeviceConfig(serial="abc")])
    results = runner.run_all()

    assert results["abc"]["passed"] is False
    assert results["abc"]["returncode"] == 1


@patch("aitest.runner.subprocess.run")
def test_run_all_sets_env(mock_run):
    mock_run.return_value = MagicMock(returncode=0)

    runner = TestRunner([DeviceConfig(serial="xyz")])
    runner.run_all()

    env = mock_run.call_args[1]["env"]
    assert env["ANDROID_SERIAL"] == "xyz"
