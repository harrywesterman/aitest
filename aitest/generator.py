class TestGenerator:
    @staticmethod
    def generate_test(app_name: str, screens: list[dict]) -> str:
        lines = [
            f"def test_{app_name.replace('.', '_')}(driver):",
        ]
        for i, screen in enumerate(screens):
            for elem in screen.get("elements", []):
                lines.append(f"    # {screen.get('description', 'screen')}")
                if elem.get("assertion"):
                    lines.append(f"    {elem['assertion']}")
        return "\n".join(lines)
