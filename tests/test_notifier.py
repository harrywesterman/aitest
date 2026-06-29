from aitest.notifier import Notifier


def test_notifier_init():
    n = Notifier()
    assert n.webhook_url == ""


def test_notifier_init_with_webhook():
    n = Notifier("https://hooks.example.com")
    assert n.webhook_url == "https://hooks.example.com"
