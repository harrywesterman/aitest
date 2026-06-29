"""Auto-generated tests for com.nl.politie.digipass."""
import time

import pytest
from appium.webdriver.common.appiumby import AppiumBy


pytestmark = pytest.mark.appium

@pytest.mark.app("com.nl.politie.digipass", ".com.vasco.digipass.mobile.android.views.activities.DigipassActivity")
class TestComNlPolitieDigipass:
    def test_com_nl_politie_digipass(self, driver):
        # The current DIGIPASS screen shows the main action list with a title bar and settings/notification icons.
        driver.activate_app("com.nl.politie.digipass")
        time.sleep(2)
        assert driver.find_element(AppiumBy.ID, 'com.nl.politie.digipass:id/header_title').is_displayed()
        assert driver.find_element(AppiumBy.ID, 'com.nl.politie.digipass:id/header_notification').is_displayed()
        assert driver.find_element(AppiumBy.ID, 'com.nl.politie.digipass:id/header_settings').is_displayed()
        assert driver.find_element(AppiumBy.ID, 'com.nl.politie.digipass:id/command_action_1').is_displayed()
        assert driver.find_element(AppiumBy.ID, 'com.nl.politie.digipass:id/command_action_3').is_displayed()
        assert driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Kies")').is_displayed()
        assert driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Genereer toegangscode")').is_displayed()
        assert driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Bezoek POLITIE")').is_displayed()
