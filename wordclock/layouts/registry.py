from __future__ import annotations

import importlib
from enum import StrEnum

from wordclock.layouts.base import LayoutModule


class Language(StrEnum):
    english = "english"
    catalan = "catalan"
    spanish = "spanish"


SUPPORTED_LANGUAGES: tuple[str, ...] = tuple(lang.value for lang in Language)


def get_layout(lang: str | Language) -> LayoutModule:
    """
    Return the layout module for *lang*.

    Args:
        lang: Language name or :class:`Language` enum value.

    Returns:
        The layout module satisfying the :class:`~wordclock.layouts.base.LayoutModule` protocol.

    Raises:
        ValueError: If *lang* is not a supported language.
    """
    key = lang.value if isinstance(lang, Language) else lang
    if key not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Unknown language: {lang!r}")
    return importlib.import_module(f"wordclock.layouts.{key}")  # type: ignore[return-value]
