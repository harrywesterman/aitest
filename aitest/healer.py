from .llm_client import LLMClient

HEALER_PROMPT = """A test failed because a UI element could not be found.
Old selector: {old_selector}

Here is the current page source and a screenshot.
Find the correct new selector for the same element.
Return ONLY the new selector value."""


class Healer:
    def __init__(self, llm_url: str, llm_key: str = "", model: str = "qwen2.5:7b"):
        self.llm_client = LLMClient(url=llm_url, key=llm_key, model=model)

    def heal_selector(self, old_selector: str, page_source: str) -> str:
        messages = [
            {
                "role": "system",
                "content": HEALER_PROMPT.format(old_selector=old_selector),
            },
            {"role": "user", "content": f"Page source:\n{page_source[:4000]}"},
        ]
        return self.llm_client.chat(messages).strip()
