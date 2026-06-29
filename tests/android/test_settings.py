import pytest


@pytest.mark.appium
class TestSettings:
    def test_settings_opens(self, driver):
        assert driver.find_element(
            "xpath", "//*[contains(@text,'Settings')]"
        )

    def test_wifi_toggle(self, driver):
        wifi = driver.find_element(
            "xpath",
            "//*[contains(@text,'Wi-Fi') or contains(@text,'WiFi')]",
        )
        assert wifi.is_displayed()

    def test_bluetooth_toggle(self, driver):
        bt = driver.find_element(
            "xpath", "//*[contains(@text,'Bluetooth')]"
        )
        assert bt.is_displayed()
