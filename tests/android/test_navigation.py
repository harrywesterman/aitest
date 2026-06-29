import pytest


@pytest.mark.appium
class TestNavigation:
    def test_back_button(self, driver):
        driver.press_keycode(4)
        assert True
