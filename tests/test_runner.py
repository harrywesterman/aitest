from aitest.runner import TestRunner


def test_runner_init():
    runner = TestRunner([{"serial": "test123"}])
    assert len(runner.devices) == 1
    assert runner.devices[0]["serial"] == "test123"
