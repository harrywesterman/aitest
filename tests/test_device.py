import pytest
from unittest.mock import patch, MagicMock
from aitest.device import DeviceManager
from aitest.config import DeviceConfig


def test_discover_returns_list():
    dm = DeviceManager()
    devices = dm.discover()
    assert isinstance(devices, list)


@patch("aitest.device.subprocess.run")
def test_discover_parses_output(mock_run):
    mock_run.return_value = MagicMock(
        returncode=0,
        stdout="List of devices attached\nemulator-5554\tdevice\n1234567\tdevice\n",
    )
    dm = DeviceManager()
    devices = dm.discover()
    assert len(devices) == 2
    assert devices[0].serial == "emulator-5554"
    assert isinstance(devices[0], DeviceConfig)


@patch("aitest.device.subprocess.run")
def test_discover_skips_offline(mock_run):
    mock_run.return_value = MagicMock(
        returncode=0,
        stdout="List of devices attached\nemulator-5554\tdevice\nbad\tOffline\n",
    )
    dm = DeviceManager()
    devices = dm.discover()
    assert len(devices) == 1
    assert devices[0].serial == "emulator-5554"


@patch("aitest.device.subprocess.run")
def test_discover_handles_adb_error(mock_run):
    mock_run.return_value = MagicMock(returncode=1, stdout="")
    dm = DeviceManager()
    devices = dm.discover()
    assert devices == []


def test_start_appium_requires_serial():
    dm = DeviceManager()
    with pytest.raises(ValueError, match="serial"):
        dm.start_appium("")


@patch("aitest.device.subprocess.Popen")
@patch("aitest.device.DeviceManager._appium_ready")
@patch("aitest.device.DeviceManager._port_in_use")
def test_start_appium_reuses_running_server(mock_port_in_use, mock_ready, mock_popen):
    mock_port_in_use.return_value = True
    mock_ready.return_value = True

    dm = DeviceManager()
    port = dm.start_appium("abc", 4723)

    assert port == 4723
    mock_popen.assert_not_called()


def test_port_in_use():
    dm = DeviceManager()
    # unlikely to be in use on a random high port
    assert dm._port_in_use(0) is False


def test_find_free_port():
    dm = DeviceManager()
    port = dm._find_free_port(60000)
    assert port >= 60000
    assert port < 65535
