from aitest.healer import Healer


def test_healer_init():
    healer = Healer(llm_url="http://localhost:11434/v1")
    assert healer.llm_client is not None
