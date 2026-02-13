import os
from typing import Any
from dotenv import load_dotenv
from Helpers import JsonObject

load_dotenv()


def get_config() -> JsonObject:
    def get_env(key: str, default: Any = None, cast_type: Any = str) -> Any:
        value = os.getenv(key, default)
        try:
            return cast_type(value) if value is not None else default
        except (ValueError, TypeError):
            return default

    config_data: dict[str, Any] = {
        "app_name": get_env("NAME", "Lumi"),
        "app_id": get_env("APP_ID", None, int),
        "app_hash": get_env("APP_HASH", None),
        "app_token": get_env("APP_TOKEN", None),
        "owner_user_id": get_env("OWNER_USER_ID", None, int),
        "owner_user_name": get_env("OWNER_USER_NAME", None),
        "prefix": get_env("PREFIX", "/"),
        "url": get_env(
            "URL",
            "mongodb+srv://stumnmake:abhinavvijay@cluster0.kbpomy2.mongodb.net/Alice?retryWrites=true&w=majority",
        ),
        "imgbb_key": get_env("IMGBB_KEY", None),
    }

    return JsonObject(config_data)


