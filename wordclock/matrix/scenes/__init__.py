"""
Scenes of the mini matrix and the registry of the ones that need no
settings. Scenes that need data or settings (``show``, ``weather``,
``forecast``, ``commits``) are built by :class:`wordclock.matrix.catalog.Catalog`.

Layout: ``text.py`` and ``clocks.py`` for words and time, ``icons.py`` for
the drawings, ``effects/`` for scenes that only draw, ``screens/`` for
scenes that show data or keep state, and ``show.py`` for the show that
plays them all.
"""

from __future__ import annotations

from collections.abc import Callable

from wordclock.matrix.canvas import Color
from wordclock.matrix.scenes.base import Scene
from wordclock.matrix.scenes.clocks import BlocksClock, DialClock, TixClock
from wordclock.matrix.scenes.effects.life import LifeScene
from wordclock.matrix.scenes.effects.rain import RainScene
from wordclock.matrix.scenes.effects.rainbow import RainbowScene
from wordclock.matrix.scenes.effects.sparkle import SparkleScene
from wordclock.matrix.scenes.effects.wiring import WiringScene
from wordclock.matrix.scenes.screens.pomodoro import PomodoroScene
from wordclock.matrix.scenes.text import ClockScene, IpScene, TextScene

# Build a scene from the text and the colour of a request.
SceneFactory = Callable[[str, Color | None], Scene]


def _color(color: Color | None) -> dict[str, Color]:
    return {"color": color} if color is not None else {}


SCENES: dict[str, SceneFactory] = {
    "text": lambda text, color: TextScene(text, **_color(color)),
    "clock": lambda text, color: ClockScene(**_color(color)),
    "blocks": lambda text, color: BlocksClock(),
    "dial": lambda text, color: DialClock(),
    "tix": lambda text, color: TixClock(),
    "ip": lambda text, color: IpScene(**_color(color)),
    "rain": lambda text, color: RainScene(**_color(color)),
    "rainbow": lambda text, color: RainbowScene(),
    "sparkle": lambda text, color: SparkleScene(),
    "life": lambda text, color: LifeScene(),
    "pomodoro": lambda text, color: PomodoroScene(),
    "wiring": lambda text, color: WiringScene(**_color(color)),
}
SCENE_NAMES: tuple[str, ...] = tuple(SCENES)


def create_scene(name: str, text: str = "HOLA", color: Color | None = None) -> Scene:
    """
    Build a scene that needs no settings.

    Args:
        name: One of :data:`SCENE_NAMES`.
        text: Text for the ``text`` scene.
        color: Colour for the scenes that use one; None keeps their default.

    Returns:
        A new scene.

    Raises:
        ValueError: If the name is unknown.
    """
    try:
        factory = SCENES[name]
    except KeyError as exc:
        names = ", ".join(SCENE_NAMES)
        raise ValueError(f"Unknown scene {name!r}, expected one of: {names}") from exc
    return factory(text, color)


__all__ = ["SCENES", "SCENE_NAMES", "Scene", "SceneFactory", "create_scene"]
