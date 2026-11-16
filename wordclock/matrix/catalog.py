from __future__ import annotations

from logging import getLogger

from wordclock.matrix.canvas import Color
from wordclock.matrix.feeds import Feed, Weather, contributions_fetcher, weather_fetcher
from wordclock.matrix.scenes import SCENE_NAMES, Scene, create_scene
from wordclock.matrix.screens import CommitsScene, LifeScene, PomodoroScene, WeatherScene
from wordclock.matrix.show import Personal, ShowScene

logger = getLogger(__name__)

# Scenes that need the personal settings or keep state, on top of the
# plain ones of :data:`SCENE_NAMES`.
EXTRA_SCENES: tuple[str, ...] = ("pomodoro", "life", "weather", "commits")
ALL_SCENES: tuple[str, ...] = SCENE_NAMES + EXTRA_SCENES

WEATHER_REFRESH_SECONDS = 15 * 60
COMMITS_REFRESH_SECONDS = 30 * 60


class Catalog:
    """
    Build any scene by name, with the personal settings and the network
    feeds they need. The feeds are made once and shared, so switching
    scenes does not fetch again.
    """

    def __init__(self, personal: Personal, days: int = 60) -> None:
        self.personal = personal
        self.weather: Feed[Weather] | None = None
        self.commits: Feed[list[int]] | None = None
        if personal.city:
            self.weather = Feed(weather_fetcher(personal.city), WEATHER_REFRESH_SECONDS, "weather")
        if personal.github_user and personal.github_token:
            fetch = contributions_fetcher(personal.github_user, personal.github_token, days)
            self.commits = Feed(fetch, COMMITS_REFRESH_SECONDS, "commits")

    def available(self) -> tuple[str, ...]:
        """
        List the scenes that can play with these settings.

        Returns:
            Scene names; ``weather`` needs a city, ``commits`` a GitHub
            account.
        """
        missing = {"weather"} if self.weather is None else set()
        if self.commits is None:
            missing.add("commits")
        return tuple(name for name in ALL_SCENES if name not in missing)

    def build(self, name: str, text: str = "HOLA", color: Color | None = None) -> Scene:
        """
        Build a scene.

        Args:
            name: One of :meth:`available`.
            text: Text for the ``text`` scene.
            color: Colour for the scenes that use one.

        Returns:
            A new scene.

        Raises:
            ValueError: If the scene is unknown or not set up.
        """
        if name == "show":
            return ShowScene(self.personal, weather=self.weather, commits=self.commits)
        if name == "pomodoro":
            return PomodoroScene()
        if name == "life":
            return LifeScene()
        if name == "weather":
            if self.weather is None:
                raise ValueError("The weather needs a city: [weather] city in matrix.toml")
            return WeatherScene(self.weather)
        if name == "commits":
            if self.commits is None:
                raise ValueError("The commits need [github] user and token in matrix.toml")
            return CommitsScene(self.commits)
        return create_scene(name, text=text, color=color)
