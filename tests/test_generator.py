from aitest.generator import TestGenerator


def test_generate_test_basic():
    gen = TestGenerator()
    screens = [
        {
            "description": "login screen",
            "elements": [
                {"selector": "//input[@id='email']", "assertion": "driver.find_element(By.XPATH, '//input[@id=\"email\"]')"}
            ],
        }
    ]
    code = gen.generate_test("com.example.app", screens)
    assert "test_com_example_app" in code
    assert "driver" in code
