from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass, field
from logging import getLogger
from pathlib import Path

from wordclock.matrix.dimmer import BrightnessLevels

logger = getLogger(__name__)


@dataclass(frozen=True)
class Personal:
    """Personal texts and accounts, kept out of the public repository."""

    messages: tuple[str, ...] = ()
    # Texts for one day of every year, keyed by "MM-DD".
    dates: dict[str, tuple[str, ...]] = field(default_factory=dict)
    # City for the weather screen
    city: str | None = None
    # GitHub login and token for the commits screen
    github_user: str | None = None
    github_token: str | None = field(default=None, repr=False)
    # Strip brightness for the day, the evening and the night
    brightness: BrightnessLevels = field(default_factory=BrightnessLevels)


def _optional_text(table: object, key: str) -> str | None:
    if not isinstance(table, dict):
        raise ValueError(f"Expected a table, got {table!r}")
    value = table.get(key)
    if value is not None and not isinstance(value, str):
        raise ValueError(f"Expected text for {key!r}, got {value!r}")
    return value


def _texts(value: object) -> tuple[str, ...]:
    if isinstance(value, str):
        return (value,)
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return tuple(value)
    raise ValueError(f"Expected a text or a list of texts, got {value!r}")


def _brightness(table: object) -> BrightnessLevels:
    if not isinstance(table, dict):
        raise ValueError(f"Expected a table, got {table!r}")
    unknown = set(table) - {"day", "evening", "night"}
    if unknown:
        raise ValueError(f"Unknown brightness keys: {', '.join(sorted(unknown))}")
    return BrightnessLevels(**table)


def load_personal(path: Path) -> Personal:
    """
    Read the personal texts from a TOML file.

    The file has a ``messages`` list, a ``[dates]`` table that maps
    ``"MM-DD"`` to a text or a list of texts, a ``[weather]`` table with a
    ``city``, a ``[github]`` table with a ``user`` and a ``token``, and a
    ``[brightness]`` table with a ``day``, ``evening`` and ``night`` level. A
    missing or broken file gives no personal settings, so the show still
    runs. Without a token in the file, ``GITHUB_TOKEN`` is used.

    Args:
        path: The TOML file.

    Returns:
        The personal texts.
    """
    if not path.is_file():
        logger.info("No personal texts at %s", path)
        return Personal(github_token=os.environ.get("GITHUB_TOKEN"))
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        messages = _texts(data.get("messages", []))
        dates = {str(day): _texts(texts) for day, texts in data.get("dates", {}).items()}
        city = _optional_text(data.get("weather", {}), "city")
        github_user = _optional_text(data.get("github", {}), "user")
        github_token = _optional_text(data.get("github", {}), "token")
        brightness = _brightness(data.get("brightness", {}))
    except (tomllib.TOMLDecodeError, ValueError, AttributeError) as exc:
        logger.warning("Ignoring personal texts in %s: %s", path, exc)
        return Personal(github_token=os.environ.get("GITHUB_TOKEN"))
    logger.info("Loaded %d messages and %d dates from %s", len(messages), len(dates), path)
    return Personal(
        messages,
        dates,
        city=city,
        github_user=github_user,
        github_token=github_token or os.environ.get("GITHUB_TOKEN"),
        brightness=brightness,
    )
