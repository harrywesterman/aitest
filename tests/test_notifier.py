from unittest.mock import patch
from aitest.notifier import Notifier


def test_notifier_init():
    n = Notifier()
    assert n.webhook_url == ""


def test_notifier_init_with_webhook():
    n = Notifier("https://hooks.example.com")
    assert n.webhook_url == "https://hooks.example.com"


def test_notify_failure_no_webhook(capsys):
    n = Notifier()
    n.notify_failure("dev1", "test_login", "timeout")
    captured = capsys.readouterr()
    assert "[FAIL] dev1 - test_login: timeout" in captured.err


@patch("aitest.notifier.httpx.post")
def test_notify_failure_with_webhook(mock_post):
    n = Notifier("https://hooks.example.com")
    n.notify_failure("dev1", "test_a", "error")
    mock_post.assert_called_once_with(
        "https://hooks.example.com",
        json={"device": "dev1", "test": "test_a", "error": "error"},
    )


def test_summary_all_pass(capsys):
    n = Notifier()
    result = n.summary({"dev1": {"passed": True}, "dev2": {"passed": True}})
    assert result == 0
    captured = capsys.readouterr()
    assert "2/2 passed" in captured.out


def test_summary_some_fail(capsys):
    n = Notifier()
    result = n.summary({"dev1": {"passed": True}, "dev2": {"passed": False}})
    assert result == 1
    captured = capsys.readouterr()
    assert "1/2 passed" in captured.out
    assert "FAILURES" in captured.err
