"""Loads the four settings from .env. Values are never printed."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import dotenv_values

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SETTING_NAMES = ("DISCORD_TOKEN", "CHANNEL_ID", "CLAUDE_MODEL", "DATA_DIR")


class ConfigError(Exception):
    pass


@dataclass(frozen=True)
class Config:
    discord_token: str
    channel_id: int
    claude_model: str
    data_dir: Path

    @property
    def photos_dir(self) -> Path:
        return self.data_dir / "photos"


def load_config(env_path: Path = PROJECT_ROOT / ".env") -> Config:
    # dotenv_values reads the file without copying the token into os.environ,
    # so the claude -p subprocess never inherits it.
    file_values = dotenv_values(env_path) if env_path.exists() else {}
    values = {}
    for name in SETTING_NAMES:
        value = (file_values.get(name) or os.environ.get(name) or "").strip()
        if not value:
            raise ConfigError(f"Setting {name} is missing or empty in .env")
        values[name] = value

    if not values["CHANNEL_ID"].isdigit():
        raise ConfigError("Setting CHANNEL_ID must contain only digits")

    data_dir = Path(values["DATA_DIR"]).expanduser()
    if not data_dir.is_absolute():
        data_dir = PROJECT_ROOT / data_dir

    return Config(
        discord_token=values["DISCORD_TOKEN"],
        channel_id=int(values["CHANNEL_ID"]),
        claude_model=values["CLAUDE_MODEL"],
        data_dir=data_dir.resolve(),
    )
