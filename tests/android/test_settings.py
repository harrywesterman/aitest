import pytest


@pytest.mark.appium
class TestSettings:
    def test_settings_opens(self, settings_driver):
        assert settings_driver.find_element(
            "xpath", "//*[contains(@text,'Instellingen')]"
        )

    def test_wifi_toggle(self, settings_driver):
        wifi = settings_driver.find_element(
            "xpath",
            "//*[contains(@text,'Wifi')]",
        )
        assert wifi.is_displayed()

    def test_bluetooth_toggle(self, settings_driver):
        bt = settings_driver.find_element(
            "xpath", "//*[contains(@text,'Bluetooth')]"
        )
        assert bt.is_displayed()
