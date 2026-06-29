import json
import re


class TestGenerator:
    @staticmethod
    def _uiautomator_selector(kind: str, value: str) -> str:
        return f'new UiSelector().{kind}({json.dumps(value)})'

    @staticmethod
    def _normalize_id(selector_value: str, app_package: str = "") -> str:
        if not app_package or "/" in selector_value or ":" in selector_value:
            return selector_value
        return f"{app_package}:id/{selector_value}"

    @classmethod
    def _normalize_assertion_ids(cls, assertion: str, app_package: str) -> str:
        def replace(match: re.Match) -> str:
            prefix, quote, selector_value = match.groups()
            return f"{prefix}{quote}{cls._normalize_id(selector_value, app_package)}{quote}"

        return re.sub(r"(AppiumBy\.ID,\s*)(['\"])([^'\"]+)\2", replace, assertion)

    @staticmethod
    def _action_code(action: dict, indent: str = "        ", app_package: str = "") -> str:
        t = action.get("type", "back")
        if t == "back":
            return f"{indent}driver.back()"
        if t == "terminate":
            return ""

        sel_type = action.get("selector_type", "xpath")
        sel_val = action.get("selector_value", "")

        if not sel_val:
            return f"{indent}driver.back()"

        if t == "type":
            type_val = action.get("value", "")
            if sel_type == "text":
                selector = TestGenerator._uiautomator_selector("text", sel_val)
                return f"""{indent}el = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, '{selector}'){indent}el.clear(){indent}el.send_keys({json.dumps(type_val)})"""
            if sel_type == "id":
                sel_val = TestGenerator._normalize_id(sel_val, app_package)
                return f"""{indent}el = driver.find_element(AppiumBy.ID, "{sel_val}"){indent}el.clear(){indent}el.send_keys({json.dumps(type_val)})"""
            if sel_type in {"description", "content-desc", "accessibility_id"}:
                return f"""{indent}el = driver.find_element(AppiumBy.ACCESSIBILITY_ID, {json.dumps(sel_val)}){indent}el.clear(){indent}el.send_keys({json.dumps(type_val)})"""
            return f"""{indent}el = driver.find_element(AppiumBy.XPATH, {json.dumps(sel_val)}){indent}el.clear(){indent}el.send_keys({json.dumps(type_val)})"""

        if sel_type == "text":
            selector = TestGenerator._uiautomator_selector("text", sel_val)
            return f"""{indent}driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, '{selector}').click()"""

        if sel_type == "id":
            sel_val = TestGenerator._normalize_id(sel_val, app_package)
            return f"""{indent}driver.find_element(AppiumBy.ID, "{sel_val}").click()"""

        if sel_type in {"description", "content-desc", "accessibility_id"}:
            return f"""{indent}driver.find_element(AppiumBy.ACCESSIBILITY_ID, {json.dumps(sel_val)}).click()"""

        return f"""{indent}driver.find_element(AppiumBy.XPATH, {json.dumps(sel_val)}).click()"""

    @classmethod
    def generate_test(cls, app_name: str, screens: list[dict]) -> str:
        safe = app_name.replace(".", "_")
        lines = [
            f'"""Auto-generated tests for {app_name}."""',
            "import pytest",
            "from appium.webdriver.common.appiumby import AppiumBy",
            "",
            "",
            "pytestmark = pytest.mark.appium",
            "",
            f"class Test{''.join(p.capitalize() for p in safe.split('_'))}:",
            f"    def test_{safe}(self, driver):",
        ]

        for i, screen in enumerate(screens):
            desc = screen.get("description", "screen")
            lines.append(f"        # {desc}")
            for elem in screen.get("elements", []):
                assertion = elem.get("assertion", "")
                if assertion:
                    lines.append(f"        {cls._normalize_assertion_ids(assertion, app_name)}")

            action = screen.get("action", {})
            if i < len(screens) - 1 and action:
                nav = cls._action_code(action, app_package=app_name)
                if nav:
                    lines.append(nav)
            lines.append("")

        if lines and not lines[-1]:
            lines.pop()
        return "\n".join(lines) + "\n"
