from .llm_client import LLMClient

HEALER_PROMPT = """A test failed because a UI element could not be found.
Old selector: {old_selector}

Here is the current page source.
Find the correct new selector for the same element.
Return ONLY the new selector value."""


class Healer:
    def __init__(self, llm_url: str, llm_key: str = "", model: str = "qwen2.5:7b"):
        self.llm_client = LLMClient(url=llm_url, key=llm_key, model=model)

    def heal_selector(self, old_selector: str, page_source: str, screenshot_base64: str | None = None) -> str:
        system_msg = {"role": "system", "content": HEALER_PROMPT.format(old_selector=old_selector)}
        if screenshot_base64:
            user_msg = {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"Page source:\n{page_source[:4000]}"},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{screenshot_base64}"}},
                ],
            }
        else:
            user_msg = {"role": "user", "content": f"Page source:\n{page_source[:4000]}"}
        return self.llm_client.chat([system_msg, user_msg]).strip()
