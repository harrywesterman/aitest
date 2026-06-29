import yaml
from pathlib import Path
from dataclasses import dataclass, field


class ConfigError(Exception):
    pass

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
class NotifyConfig:
    webhook: str = ""

@dataclass
class Config:
    llm: LLMConfig = field(default_factory=LLMConfig)
    devices: list[DeviceConfig] = field(default_factory=list)
    notify: NotifyConfig = field(default_factory=NotifyConfig)

    @classmethod
    def load(cls, path: str | None = None) -> "Config":
        path = path or "aitest.yaml"
        cfg_file = Path(path)
        if not cfg_file.exists():
            if path != "aitest.yaml":
                raise ConfigError(f"config file not found: {path}")
            return cls()
        with open(cfg_file) as f:
            try:
                data = yaml.safe_load(f) or {}
            except yaml.YAMLError as e:
                raise ConfigError(f"invalid YAML in {path}: {e}") from e
        llm_data = data.get("llm", {})
        devices_data = data.get("devices", [])
        notify_data = data.get("notify", {})
        return cls(
            llm=LLMConfig(**llm_data),
            devices=[DeviceConfig(**d) for d in devices_data],
            notify=NotifyConfig(**notify_data),
        )
