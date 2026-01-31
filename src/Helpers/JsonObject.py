from typing import Any, Dict, Optional


class JsonObject:
    def __init__(self, config: Dict[str, Any]) -> None:
        self.__dict__["_config"] = config
        for key, value in config.items():
            if isinstance(value, dict):
                value = JsonObject(value)
            setattr(self, key, value)

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        return getattr(self, key, default)
