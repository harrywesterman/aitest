import httpx
from typing import Any


class LLMClient:
    def __init__(self, url: str, key: str = "", model: str = "qwen2.5:7b"):
        if not url:
            raise ValueError("url is required")
        self.url = url.rstrip("/") + "/chat/completions"
        self.key = key
        self.model = model
        self._client = httpx.Client(timeout=120)

    def chat(self, messages: list[dict[str, str]], **kwargs: Any) -> str:
        if not messages:
            raise ValueError("messages cannot be empty")
        headers = {"Content-Type": "application/json"}
        if self.key:
            headers["Authorization"] = f"Bearer {self.key}"
        payload = {"model": self.model, "messages": messages, **kwargs}
        resp = self._client.post(self.url, json=payload, headers=headers)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]

    def close(self):
        self._client.close()
