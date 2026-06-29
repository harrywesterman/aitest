"""Auto-generated tests for com.android.deskclock."""
import pytest
from appium.webdriver.common.appiumby import AppiumBy


pytestmark = pytest.mark.appium

@pytest.mark.app("com.android.deskclock", ".DeskClockTabActivity")
class TestCom_Android_Deskclock:
    def test_com_android_deskclock(self, driver):
        # This is the Alarm tab of the Android Desk Clock app, displaying a list of configured alarms with their times, frequency settings, and toggle switches. The bottom navigation bar shows four tabs: Alarm, World Clock (Wereldklok), Stopwatch, and Timer.
        assert driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Alarm")').is_displayed()
        assert driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Wereldklok")').is_displayed()
        assert driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Stopwatch")').is_displayed()
        assert driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Timer")').is_displayed()
        assert driver.find_element(AppiumBy.ID, 'com.android.deskclock:id/end_btn2').is_displayed()
        driver.find_element(AppiumBy.XPATH, '//*[@text="Wereldklok"]').click()

        # Main Clock screen of the DeskClock app showing current time (22:04:20), local date (29 jun), and navigation tabs for Alarm, World Clock, Stopwatch, and Timer. Currently on the Clock tab with no clocks added.
        assert driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Alarm")').is_displayed()
        assert driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Wereldklok")').is_displayed()
        assert driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Stopwatch")').is_displayed()
        assert driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Timer")').is_displayed()
        assert driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Lokale tijd")').is_displayed()
