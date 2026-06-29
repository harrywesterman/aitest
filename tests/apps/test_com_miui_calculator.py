"""Auto-generated tests for com.miui.calculator."""
import pytest
from appium.webdriver.common.appiumby import AppiumBy


pytestmark = pytest.mark.appium

@pytest.mark.app("com.miui.calculator", ".cal.CalculatorActivity")
class TestComMiuiCalculator:
    def test_com_miui_calculator(self, driver):
        # Xiaomi Calculator app showing the calculator/converter switcher and converter category grid.
        assert driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Rekenmachine")').is_displayed()
        assert driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Omzetter")').is_displayed()
        assert driver.find_element(AppiumBy.ID, 'com.miui.calculator:id/more').is_displayed()
        assert driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().description("Valuta")').is_displayed()
        assert driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().description("Lengte")').is_displayed()
        assert driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().description("Massa")').is_displayed()
        assert driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().description("Temperatuur")').is_displayed()
