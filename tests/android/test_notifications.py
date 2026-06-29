import pytest


@pytest.mark.appium
class TestNotifications:
    def test_notification_bar(self, driver):
        driver.open_notifications()
        assert driver.find_element(
            "xpath", "//*[contains(@text,'USB debugging')]"
        )
