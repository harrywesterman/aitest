class TestGenerator:
    @staticmethod
    def _action_code(action: dict, indent: str = "        ") -> str:
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
                return f"""{indent}el = driver.find_element(AppiumBy.XPATH, '//*[@text="{sel_val}"]'){indent}el.clear(){indent}el.send_keys("{type_val}")"""
            if sel_type == "id":
                return f"""{indent}el = driver.find_element(AppiumBy.ID, "{sel_val}"){indent}el.clear(){indent}el.send_keys("{type_val}")"""
            return f"""{indent}el = driver.find_element(AppiumBy.XPATH, "{sel_val}"){indent}el.clear(){indent}el.send_keys("{type_val}")"""

        if sel_type == "text":
            return f"""{indent}driver.find_element(AppiumBy.XPATH, '//*[@text="{sel_val}"]').click()"""

        if sel_type == "id":
            return f"""{indent}driver.find_element(AppiumBy.ID, "{sel_val}").click()"""

        return f"""{indent}driver.find_element(AppiumBy.XPATH, "{sel_val}").click()"""

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
                    lines.append(f"        {assertion}")

            action = screen.get("action", {})
            if i < len(screens) - 1 and action:
                nav = cls._action_code(action)
                if nav:
                    lines.append(nav)
            lines.append("")

        if lines and not lines[-1]:
            lines.pop()
        return "\n".join(lines) + "\n"
