import json
from unittest.mock import patch, MagicMock
from aitest.explorer import ExplorerAgent


def test_explorer_init():
    explorer = ExplorerAgent(llm_url="http://localhost:11434/v1")
    assert explorer.llm_client is not None
    assert explorer.max_screens == 10


SAMPLE_XML = """<?xml version="1.0"?>
<android.widget.FrameLayout>
  <android.widget.LinearLayout resource-id="com.app:id/header" text="Welcome" clickable="true" content-desc="" checkable="false" scrollable="false">
    <android.widget.Button resource-id="com.app:id/submit" text="Submit" clickable="true" content-desc="Submit button" checkable="false" scrollable="false"/>
  </android.widget.LinearLayout>
  <android.widget.TextView text="Hello" clickable="false"/>
</android.widget.FrameLayout>"""


def test_compress_xml():
    result = ExplorerAgent._compress_xml(SAMPLE_XML)
    assert "LinearLayout" in result
    assert "id=\"com.app:id/header\"" in result
    assert "text=\"Welcome\"" in result
    assert "id=\"com.app:id/submit\"" in result
    assert "text=\"Submit\"" in result
    assert "clickable" in result
    assert "desc=\"Submit button\"" in result
    assert "TextView" in result
    assert "Hello" in result


def test_compress_xml_empty():
    result = ExplorerAgent._compress_xml("<node></node>")
    assert result == ""


def test_strip_markdown_no_fences():
    result = ExplorerAgent._strip_markdown('{"key": "value"}')
    assert result == '{"key": "value"}'


def test_strip_markdown_with_fences():
    result = ExplorerAgent._strip_markdown('```json\n{"key": "value"}\n```')
    assert json.loads(result) == {"key": "value"}


def test_strip_markdown_without_lang():
    result = ExplorerAgent._strip_markdown('```\n{"key": "value"}\n```')
    assert json.loads(result) == {"key": "value"}


@patch("aitest.explorer.LLMClient")
def test_analyze_screen_parses_json(mock_llm_cls):
    mock_client = MagicMock()
    mock_client.chat.return_value = '{"description": "test", "elements": [], "action": {"type": "back"}, "is_end_state": false}'
    mock_llm_cls.return_value = mock_client

    explorer = ExplorerAgent(llm_url="http://localhost:11434/v1")
    result = explorer.analyze_screen("<xml/>", "com.test.app")

    assert result["description"] == "test"
    assert result["action"]["type"] == "back"


@patch("aitest.explorer.LLMClient")
def test_analyze_screen_bad_json_uses_back(mock_llm_cls):
    mock_client = MagicMock()
    mock_client.chat.return_value = "not json"
    mock_llm_cls.return_value = mock_client

    explorer = ExplorerAgent(llm_url="http://localhost:11434/v1")
    result = explorer.analyze_screen("<xml/>", "com.test.app")

    assert result["action"]["type"] == "back"
    assert result["is_end_state"] is False


@patch("aitest.explorer.LLMClient")
def test_analyze_screen_llm_error_ends(mock_llm_cls):
    mock_client = MagicMock()
    mock_client.chat.side_effect = RuntimeError("LLM server down")
    mock_llm_cls.return_value = mock_client

    explorer = ExplorerAgent(llm_url="http://localhost:11434/v1")
    result = explorer.analyze_screen("<xml/>", "com.test.app")

    assert result["action"]["type"] == "back"
    assert result["is_end_state"] is True
