import pytest
from aitest.device import DeviceManager


def test_discover_returns_list():
    dm = DeviceManager()
    devices = dm.discover()
    assert isinstance(devices, list)


def test_start_appium_requires_serial():
    dm = DeviceManager()
    with pytest.raises(ValueError, match="serial"):
        dm.start_appium("")
