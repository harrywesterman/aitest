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


def test_action_code_back():
    code = TestGenerator._action_code({"type": "back"})
    assert "driver.back()" in code


def test_action_code_terminate():
    code = TestGenerator._action_code({"type": "terminate"})
    assert code == ""


def test_action_code_click_id():
    code = TestGenerator._action_code({
        "type": "tap", "selector_type": "id", "selector_value": "button1"
    })
    assert 'AppiumBy.ID' in code
    assert 'button1' in code
    assert '.click()' in code


def test_action_code_click_text():
    code = TestGenerator._action_code({
        "type": "tap", "selector_type": "text", "selector_value": "Submit"
    })
    assert 'AppiumBy.XPATH' in code
    assert 'Submit' in code
    assert '.click()' in code


def test_action_code_type():
    code = TestGenerator._action_code({
        "type": "type", "selector_type": "id",
        "selector_value": "input_email", "value": "test@example.com"
    })
    assert 'send_keys' in code
    assert 'input_email' in code
    assert 'test@example.com' in code
    assert '.clear()' in code


def test_action_code_no_selector_falls_back():
    code = TestGenerator._action_code({"type": "tap", "selector_value": ""})
    assert "driver.back()" in code


def test_generate_class_name():
    gen = TestGenerator()
    code = gen.generate_test("com.android.deskclock", [{"description": "screen", "elements": [], "action": {"type": "terminate"}}])
    assert "TestComAndroidDeskclock" in code


def test_generate_normalizes_short_resource_ids():
    gen = TestGenerator()
    code = gen.generate_test(
        "com.example.app",
        [
            {
                "description": "screen",
                "elements": [
                    {"assertion": "assert driver.find_element(AppiumBy.ID, 'submit').is_displayed()"}
                ],
                "action": {"type": "tap", "selector_type": "id", "selector_value": "next"},
            },
            {"description": "next", "elements": [], "action": {"type": "terminate"}},
        ],
    )
    assert "com.example.app:id/submit" in code
    assert "com.example.app:id/next" in code
