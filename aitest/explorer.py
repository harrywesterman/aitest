import json
from .llm_client import LLMClient

EXPLORER_PROMPT = """You are an Android test engineer. You are given the XML page source and a screenshot of the current screen.

1. List all interactive elements (buttons, text fields, lists, switches, etc.)
2. For each element, write a pytest assertion to verify it exists
3. Choose ONE action to take next (tap, type, swipe, back) that advances the flow
4. If this is a login form, generate code to fill in credentials

Return JSON:
{
  "elements": [{"selector": "xpath or id", "assertion": "code"}],
  "action": {"type": "tap|type|swipe|back", "target": "selector", "value": ""},
  "description": "what this screen does"
}"""


class ExplorerAgent:
    def __init__(self, llm_url: str, llm_key: str = "", model: str = "qwen2.5:7b"):
        self.llm_client = LLMClient(url=llm_url, key=llm_key, model=model)

    def analyze_screen(self, page_source: str, screenshot_b64: str = "") -> dict:
        messages = [
            {"role": "system", "content": EXPLORER_PROMPT},
            {"role": "user", "content": f"Page source:\n{page_source[:4000]}"},
        ]
        result = self.llm_client.chat(messages)
        return json.loads(result)
