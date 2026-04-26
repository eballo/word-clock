from __future__ import annotations

import json
from logging import getLogger
from pathlib import Path

from wordclock.layouts.utils.grid import create_layout

logger = getLogger(__name__)

_DATA_DIR = Path(__file__).parent.parent / "data"


class Layout:
    """Represents a single language layout backed by a JSON data file."""

    def __init__(self, name: str) -> None:
        """
        Args:
            name: Layout name matching a file in ``data/`` (e.g. ``"english"``).
        """
        key = name.value if hasattr(name, "value") else name
        self.name = key
        self._path: Path = _DATA_DIR / f"{key}.json"
        self._data: dict = json.loads(self._path.read_text(encoding="utf-8"))

    @classmethod
    def available(cls) -> list[str]:
        """Return all layout names found in the data directory."""
        return sorted(p.stem for p in _DATA_DIR.glob("*.json"))

    @property
    def raw(self) -> list[str]:
        """Raw grid rows with lowercase 'x' as filler positions."""
        return self._data["raw"]

    @property
    def static(self) -> list[str] | None:
        """Pre-generated display matrix, or ``None`` if not yet generated."""
        return self._data.get("static") or None

    def grid(self, seed: int | None = None) -> list[str]:
        """
        Return the display matrix.

        Uses the stored static version if available; otherwise computes one
        from the raw grid via :func:`~wordclock.layouts.utils.grid.create_layout`.

        Args:
            seed: Forwarded to :func:`~wordclock.layouts.utils.grid.create_layout`
                  when no static matrix exists.

        Returns:
            Final grid with all 'x' fillers replaced by uppercase letters.
        """
        if self.static:
            return self.static
        return create_layout(self.raw, seed=seed)

    def generate_static(self, seed: int | None = None) -> list[str]:
        """
        Generate a static display matrix and persist it to the JSON file.

        Args:
            seed: Optional seed for :func:`~wordclock.layouts.utils.grid.create_layout`.

        Returns:
            The generated static grid now stored in the file.
        """
        static = create_layout(self.raw, seed=seed)
        self._data["static"] = static
        self._path.write_text(
            json.dumps(self._data, ensure_ascii=False, indent=4) + "\n",
            encoding="utf-8",
        )
        logger.info("Saved static layout for '%s' (%d rows)", self.name, len(static))
        return static


def load_grid(name: str, seed: int | None = None) -> list[str]:
    """Return the display matrix for *name* (static if available, else computed)."""
    return Layout(name).grid(seed=seed)


def generate_static(name: str, seed: int | None = None) -> list[str]:
    """Generate and persist the static matrix for *name*."""
    return Layout(name).generate_static(seed=seed)
