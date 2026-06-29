from unittest.mock import patch, MagicMock
from aitest.healer import Healer


def test_healer_init():
    healer = Healer(llm_url="http://localhost:11434/v1")
    assert healer.llm_client is not None


@patch("aitest.healer.LLMClient")
def test_heal_selector_calls_llm(mock_llm_cls):
    mock_client = MagicMock()
    mock_client.chat.return_value = 'new_selector_value'
    mock_llm_cls.return_value = mock_client

    healer = Healer(llm_url="http://localhost:11434/v1")
    result = healer.heal_selector("old_sel", "<page>source</page>")

    assert result == "new_selector_value"
    mock_client.chat.assert_called_once()
    messages = mock_client.chat.call_args[0][0]
    assert len(messages) == 2
    assert "old_sel" in messages[0]["content"]
    assert "source" in messages[1]["content"]


@patch("aitest.healer.LLMClient")
def test_heal_selector_with_screenshot(mock_llm_cls):
    mock_client = MagicMock()
    mock_client.chat.return_value = 'new_sel'
    mock_llm_cls.return_value = mock_client

    healer = Healer(llm_url="http://localhost:11434/v1")
    result = healer.heal_selector("old", "page", screenshot_base64="abc123")

    assert result == "new_sel"
    messages = mock_client.chat.call_args[0][0]
    user_content = messages[1]["content"]
    assert isinstance(user_content, list)
    assert user_content[0]["type"] == "text"
    assert user_content[1]["type"] == "image_url"
    assert "abc123" in user_content[1]["image_url"]["url"]
