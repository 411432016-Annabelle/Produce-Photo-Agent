"""Start the agent with: uv run python -m agent"""

import sys

import discord

from .bot import ProduceBot
from .config import ConfigError, load_config
from .log import log


def main() -> None:
    try:
        config = load_config()
    except ConfigError as error:
        log(f"❌ {error}. See .env.example.")
        sys.exit(1)

    config.photos_dir.mkdir(parents=True, exist_ok=True)
    bot = ProduceBot(config)
    try:
        # log_handler=None keeps discord.py's own logging quiet; reconnecting is automatic.
        bot.run(config.discord_token, log_handler=None)
    except discord.LoginFailure:
        log("❌ Discord rejected DISCORD_TOKEN. Reset the token in the Developer Portal and update .env.")
        sys.exit(1)
    except discord.PrivilegedIntentsRequired:
        log("❌ Message Content Intent is off. Turn it on in the Developer Portal (Bot page) and restart.")
        sys.exit(1)
    except KeyboardInterrupt:
        pass
    log("Agent stopped.")


if __name__ == "__main__":
    main()
