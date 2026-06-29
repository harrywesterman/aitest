import yaml
from pathlib import Path
from dataclasses import dataclass, field

@dataclass
class LLMConfig:
    url: str = "http://localhost:11434/v1"
    key: str = ""
    model: str = "qwen2.5:7b"

@dataclass
class DeviceConfig:
    serial: str = ""
    model: str = ""
    port: int = 4723

@dataclass
class Config:
    llm: LLMConfig = field(default_factory=LLMConfig)
    devices: list[DeviceConfig] = field(default_factory=list)

    @classmethod
    def load(cls, path: str | None = None) -> "Config":
        path = path or "aitest.yaml"
        cfg_file = Path(path)
        if not cfg_file.exists():
            return cls()
        with open(cfg_file) as f:
            data = yaml.safe_load(f) or {}
        llm_data = data.get("llm", {})
        devices_data = data.get("devices", [])
        return cls(
            llm=LLMConfig(**llm_data),
            devices=[DeviceConfig(**d) for d in devices_data],
        )
