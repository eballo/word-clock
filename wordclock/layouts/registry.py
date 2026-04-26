"""Layout registry — maps language names to their layout modules."""

from __future__ import annotations

import importlib

from wordclock.layouts.base import LayoutModule

SUPPORTED_LANGUAGES: tuple[str, ...] = ("english", "catalan", "spanish")


def get_layout(lang: str) -> LayoutModule:
    """
    Return the layout module for *lang*.

    Args:
        lang: Language name, must be one of :data:`SUPPORTED_LANGUAGES`.

    Returns:
        The layout module satisfying the :class:`~wordclock.layouts.base.LayoutModule` protocol.

    Raises:
        ValueError: If *lang* is not a supported language.
    """
    if lang not in SUPPORTED_LANGUAGES:
        raise ValueError(f"Unknown language: {lang!r}")
    return importlib.import_module(f"wordclock.layouts.{lang}")  # type: ignore[return-value]
