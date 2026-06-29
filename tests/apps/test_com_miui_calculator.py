"""Auto-generated tests for com.miui.calculator."""
import pytest
from appium.webdriver.common.appiumby import AppiumBy


pytestmark = pytest.mark.appium

@pytest.mark.app("com.miui.calculator", ".cal.CalculatorActivity")
class TestComMiuiCalculator:
    def test_com_miui_calculator(self, driver):
        # Xiaomi Calculator app showing the standard calculator mode with numeric keypad, operation buttons, and history panel
        assert driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Rekenmachine")').is_displayed()
        assert driver.find_element(AppiumBy.ID, 'com.miui.calculator:id/digit_7').is_displayed()
        assert driver.find_element(AppiumBy.ID, 'com.miui.calculator:id/digit_0').is_displayed()
        assert driver.find_element(AppiumBy.ID, 'com.miui.calculator:id/op_add').is_displayed()
        assert driver.find_element(AppiumBy.ID, 'com.miui.calculator:id/btn_equal_s').is_displayed()
        assert driver.find_element(AppiumBy.ID, 'com.miui.calculator:id/btn_switch').is_displayed()
        assert driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Omzetter")').is_displayed()
        driver.find_element(AppiumBy.ID, "com.miui.calculator:id/digit_7").click()

        # Xiaomi Calculator app showing the basic calculator mode with number pad, operators, history list, and tab navigation between Calculator and Converter modes
        assert driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Rekenmachine")').is_displayed()
        assert driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Omzetter")').is_displayed()
        assert driver.find_element(AppiumBy.ID, 'com.miui.calculator:id/expression').is_displayed()
        assert driver.find_element(AppiumBy.ID, 'com.miui.calculator:id/result').is_displayed()
        assert driver.find_element(AppiumBy.ID, 'com.miui.calculator:id/btn_switch').is_displayed()
        assert driver.find_element(AppiumBy.ID, 'com.miui.calculator:id/digit_0').is_displayed()
        assert driver.find_element(AppiumBy.ID, 'com.miui.calculator:id/digit_9').is_displayed()
        assert driver.find_element(AppiumBy.ID, 'com.miui.calculator:id/btn_equal_s').is_displayed()
        assert driver.find_element(AppiumBy.ID, 'com.miui.calculator:id/op_add').is_displayed()
        assert driver.find_element(AppiumBy.ID, 'com.miui.calculator:id/op_sub').is_displayed()
        assert driver.find_element(AppiumBy.ID, 'com.miui.calculator:id/op_mul').is_displayed()
        assert driver.find_element(AppiumBy.ID, 'com.miui.calculator:id/op_div').is_displayed()
        assert driver.find_element(AppiumBy.ID, 'com.miui.calculator:id/more').is_displayed()
        driver.find_element(AppiumBy.XPATH, '//*[@text="Omzetter"]').click()

        # This is the Converter (Omzetter) screen of the Xiaomi Calculator app, showing a scrollable grid of conversion categories including currency, length, mass, area, time, financial, data, date, discount, volume, number system, speed, and temperature.
        assert driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Rekenmachine")').is_displayed()
        assert driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Omzetter")').is_displayed()
        assert driver.find_element(AppiumBy.ID, 'com.miui.calculator:id/more').is_displayed()
        assert driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Valuta")').is_displayed()
        assert driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Lengte")').is_displayed()
        assert driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Massa")').is_displayed()
        assert driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Financieel")').is_displayed()
        assert driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Temperatuur")').is_displayed()
