import pytest
from aitest.llm_client import LLMClient


def test_llm_client_init():
    client = LLMClient(url="http://localhost:11434/v1", model="qwen2.5:7b")
    assert client.model == "qwen2.5:7b"
    assert client.url == "http://localhost:11434/v1/chat/completions"


def test_llm_client_requires_url():
    with pytest.raises(ValueError, match="url"):
        LLMClient(url="")


def test_chat_requires_messages():
    client = LLMClient(url="http://localhost:11434/v1")
    with pytest.raises(ValueError, match="messages"):
        client.chat([])


@pytest.mark.integration
def test_chat_real():
    from aitest.config import Config
    cfg = Config.load()
    client = LLMClient(url=cfg.llm.url, key=cfg.llm.key, model=cfg.llm.model)
    response = client.chat([{"role": "user", "content": "Say hello"}])
    assert len(response) > 0
