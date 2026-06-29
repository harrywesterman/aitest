"""Auto-generated tests for com.android.deskclock."""
import pytest
from appium.webdriver.common.appiumby import AppiumBy


pytestmark = pytest.mark.appium

@pytest.mark.app("com.android.deskclock", ".DeskClockTabActivity")
class TestCom_Android_Deskclock:
    def test_com_android_deskclock(self, driver):
        # The current DeskClock tab screen shows the four main tabs and the world clock title.
        assert driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().description("Alarm")').is_displayed()
        assert driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Wereldklok")').is_displayed()
        assert driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().description("Stopwatch")').is_displayed()
        assert driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().description("Timer")').is_displayed()
        assert driver.find_element(AppiumBy.ID, 'com.android.deskclock:id/action_bar_title_expand').is_displayed()
