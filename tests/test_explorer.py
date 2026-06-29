import pytest
from aitest.explorer import ExplorerAgent


def test_explorer_init():
    explorer = ExplorerAgent(llm_url="http://localhost:11434/v1")
    assert explorer.llm_client is not None
