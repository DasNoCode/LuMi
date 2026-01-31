import sys
from typing import List
from Config import get_config
from Libs import SuperClient

REQUIRED_ENV_VARS: List[str] = ["app_token", "owner_user_id", "owner_user_name"]


def main() -> None:
    config = get_config()

    bot: SuperClient = SuperClient(config)

    missing_vars: List[str] = [
        var for var in REQUIRED_ENV_VARS if not getattr(config, var, None)
    ]

    if missing_vars:
        bot.log.error(
            f"[ERROR] [Main] Missing required environment variables: {', '.join(missing_vars)}"
        )
        sys.exit(1)

    bot.run_polling()


if __name__ == "__main__":
    main()
