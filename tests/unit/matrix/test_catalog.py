from __future__ import annotations

import pytest

from wordclock.matrix.canvas import Canvas
from wordclock.matrix.catalog import ALL_SCENES, Catalog
from wordclock.matrix.personal import Personal
from wordclock.matrix.scenes import SCENE_NAMES
from wordclock.matrix.scenes.screens.commits import CommitsScene
from wordclock.matrix.scenes.screens.weather import ForecastScene, WeatherScene

SET_UP = Personal(city="Barcelona", github_user="eballo", github_token="secret")


class TestCatalog:
    def test_without_settings_hides_weather_and_commits(self) -> None:
        # Given / When
        available = Catalog(Personal()).available()
        # Then
        assert "weather" not in available and "commits" not in available
        assert "forecast" not in available
        assert "pomodoro" in available and "life" in available

    def test_with_settings_offers_every_scene(self) -> None:
        # Given / When / Then
        assert Catalog(SET_UP).available() == ALL_SCENES

    @pytest.mark.parametrize("name", Catalog(Personal()).available())
    def test_builds_every_available_scene(self, name: str) -> None:
        # Given
        canvas = Canvas(10, 6)
        # When
        scene = Catalog(Personal()).build(name)
        scene.render(canvas, 0)
        # Then
        assert scene.fps > 0

    def test_builds_the_network_scenes_without_fetching(self) -> None:
        # Given: building must not touch the network
        catalog = Catalog(SET_UP)
        # When / Then
        assert isinstance(catalog.build("weather"), WeatherScene)
        assert isinstance(catalog.build("forecast"), ForecastScene)
        assert isinstance(catalog.build("commits"), CommitsScene)

    def test_forecast_needs_a_city(self) -> None:
        # Given / When / Then
        with pytest.raises(ValueError, match="city"):
            Catalog(Personal()).build("forecast")

    @pytest.mark.parametrize(
        "name",
        ["counter", "spin", "fire", "layers", "bounce", "worms", "snake", "maze", "stack"],
    )
    def test_new_scenes_are_registered(self, name: str) -> None:
        # Given / When / Then
        assert name in SCENE_NAMES
        assert name in Catalog(Personal()).available()

    @pytest.mark.parametrize("name", ["weather", "commits", "tetris"])
    def test_rejects_what_cannot_play(self, name: str) -> None:
        # Given / When / Then
        with pytest.raises(ValueError):
            Catalog(Personal()).build(name)

    def test_show_gets_the_feeds(self) -> None:
        # Given
        catalog = Catalog(SET_UP)
        # When
        show = catalog.build("show")
        # Then
        assert show.weather is catalog.weather and show.commits is catalog.commits
