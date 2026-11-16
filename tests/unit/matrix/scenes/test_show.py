from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import pytest

from wordclock.matrix.canvas import Canvas
from wordclock.matrix.dimmer import BrightnessLevels
from wordclock.matrix.font import GLYPHS, fold_char
from wordclock.matrix.languages import MatrixLanguage
from wordclock.matrix.personal import Personal, load_personal
from wordclock.matrix.scenes.clocks import BlocksClock, CounterScene, DialClock, TixClock
from wordclock.matrix.scenes.effects.maze import MazeScene
from wordclock.matrix.scenes.effects.rainbow import RainbowScene
from wordclock.matrix.scenes.icons import ICONS, IconScene
from wordclock.matrix.scenes.show import (
    COUNTER_EXTRA_SECONDS,
    EFFECT_SECONDS,
    EFFECTS,
    ShowItem,
    ShowScene,
)
from wordclock.matrix.scenes.text import ClockScene, IpScene, TextScene
from wordclock.matrix.texts import TEXTS, Locale, date_text, day_texts, greeting

# Every kind of clock the show plays.
CLOCKS = (ClockScene, CounterScene, BlocksClock, DialClock, TixClock)

# 24 October 2026 is a Saturday.
SATURDAY = datetime(2026, 10, 24, 10, 0)
# Two minutes past ten: no clock due.
TWO_PAST_TEN = datetime(2026, 10, 24, 10, 2)


def every_day_text(language: MatrixLanguage = MatrixLanguage.catalan) -> list[str]:
    texts: set[str] = set()
    for day in range(19, 26):
        for hour in range(24):
            texts.update(day_texts(datetime(2026, 10, day, hour), TEXTS[language]))
    return sorted(texts)


def every_text() -> list[str]:
    texts: list[str] = []
    for language, words in TEXTS.items():
        texts += every_day_text(language) + list(words.weekdays + words.months)
        texts += list(words.weather.values())
    return texts


class TestDayTexts:
    @pytest.mark.parametrize(
        ("hour", "text"),
        [(0, "BONA NIT"), (6, "BON DIA"), (12, "BON DIA"), (13, "BONA TARDA"), (20, "BONA NIT")],
    )
    def test_greets_for_the_time_of_day(self, hour: int, text: str) -> None:
        # Given / When / Then
        assert greeting(hour) == text

    def test_date_uses_the_short_catalan_month(self) -> None:
        # Given / When / Then
        assert date_text(SATURDAY) == "24 OCT"

    @pytest.mark.parametrize(
        ("now", "text"),
        [
            (datetime(2026, 10, 19, 10), "FALTEN 4 DIES PER DIVENDRES"),
            (datetime(2026, 10, 22, 10), "DEMÀ ÉS DIVENDRES!"),
            (datetime(2026, 10, 23, 16), "BON CAP DE SETMANA!"),
            (SATURDAY, "BON DISSABTE"),
            (datetime(2026, 10, 25, 10), "BON DIUMENGE"),
            (datetime(2026, 10, 21, 14), "HORA DE DINAR"),
            (datetime(2026, 10, 21, 21), "HORA DE SOPAR"),
            (datetime(2026, 10, 21, 23, 30), "A DORMIR!"),
        ],
    )
    def test_adds_texts_for_the_week_and_meals(self, now: datetime, text: str) -> None:
        # Given / When
        texts = day_texts(now)
        # Then
        assert text in texts

    def test_friday_morning_has_no_weekend_text(self) -> None:
        # Given
        now = datetime(2026, 10, 23, 10)
        # When
        texts = day_texts(now)
        # Then
        assert "BON CAP DE SETMANA!" not in texts

    @pytest.mark.parametrize("text", every_text())
    def test_every_text_has_glyphs(self, text: str) -> None:
        # Given / When
        missing = [char for char in text if fold_char(char) not in GLYPHS]
        # Then
        assert missing == []


class TestLoadPersonal:
    @pytest.fixture(autouse=True)
    def no_token_in_the_environment(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv("GITHUB_TOKEN", raising=False)

    def test_reads_the_weather_city_and_the_github_account(self, tmp_path: Path) -> None:
        # Given
        path = tmp_path / "matrix.toml"
        path.write_text(
            '[weather]\ncity = "Girona"\n[github]\nuser = "eballo"\ntoken = "secret"\n',
            encoding="utf-8",
        )
        # When
        personal = load_personal(path)
        # Then
        assert personal.city == "Girona"
        assert (personal.github_user, personal.github_token) == ("eballo", "secret")
        assert "secret" not in repr(personal)

    def test_token_from_the_environment(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        # Given
        monkeypatch.setenv("GITHUB_TOKEN", "from-env")
        path = tmp_path / "matrix.toml"
        path.write_text('[github]\nuser = "eballo"\n', encoding="utf-8")
        # When / Then
        assert load_personal(path).github_token == "from-env"

    def test_reads_messages_and_dates(self, tmp_path: Path) -> None:
        # Given
        path = tmp_path / "matrix.toml"
        path.write_text(
            'messages = ["HOLA ENRIC"]\n'
            '[dates]\n"03-14" = "FELICITATS!"\n"12-25" = ["BON NADAL!", "♥"]\n',
            encoding="utf-8",
        )
        # When
        personal = load_personal(path)
        # Then
        assert personal.messages == ("HOLA ENRIC",)
        assert personal.dates == {"03-14": ("FELICITATS!",), "12-25": ("BON NADAL!", "♥")}

    def test_missing_file_gives_no_texts(self, tmp_path: Path) -> None:
        # Given / When
        personal = load_personal(tmp_path / "missing.toml")
        # Then
        assert personal == Personal()

    def test_reads_the_brightness_levels(self, tmp_path: Path) -> None:
        # Given
        path = tmp_path / "matrix.toml"
        path.write_text("[brightness]\nday = 120\nnight = 4\n", encoding="utf-8")
        # When
        personal = load_personal(path)
        # Then
        assert personal.brightness == BrightnessLevels(day=120, night=4)

    def test_default_brightness_levels(self, tmp_path: Path) -> None:
        # Given / When
        personal = load_personal(tmp_path / "missing.toml")
        # Then
        assert personal.brightness == BrightnessLevels()

    @pytest.mark.parametrize(
        "content",
        [
            "messages = [",
            "messages = [1, 2]",
            "dates = 3",
            "[brightness]\nday = 300",
            "[brightness]\nnoon = 50",
            "brightness = 50",
        ],
    )
    def test_broken_file_gives_no_texts(self, tmp_path: Path, content: str) -> None:
        # Given
        path = tmp_path / "matrix.toml"
        path.write_text(content, encoding="utf-8")
        # When
        personal = load_personal(path)
        # Then
        assert personal == Personal()


class TestIconScene:
    @pytest.mark.parametrize("name", ICONS)
    def test_icons_fill_the_matrix_exactly(self, name: str) -> None:
        # Given
        pixels = ICONS[name]
        # When / Then
        assert len(pixels) == 6
        assert all(len(row) == 10 for row in pixels)

    def test_draws_the_lit_cells(self) -> None:
        # Given
        canvas = Canvas(10, 6)
        # When
        IconScene(ICONS["heart"], (255, 0, 0)).render(canvas, 0)
        # Then
        lit = sum(1 for row in canvas.rows() for color in row if any(color))
        assert lit == sum(row.count("X") for row in ICONS["heart"])


class TestShowScene:
    def play(self, scene: ShowScene, seconds: float) -> list[type]:
        canvas = Canvas(10, 6)
        seen: list[type] = []
        for frame in range(int(seconds * scene.fps)):
            scene.render(canvas, frame)
            assert scene._item is not None
            if not seen or seen[-1] is not type(scene._item.scene):
                seen.append(type(scene._item.scene))
        return seen

    def test_plays_mostly_effects(self) -> None:
        # Given: two minutes past ten, no counter due
        scene = ShowScene(seed=1, clock=lambda: TWO_PAST_TEN)
        kinds = []
        # When: one round, item by item
        for _ in range(7):
            kinds.append(type(next(scene._items)().scene))
        # Then: IP, then effect, effect, text, effect, effect, drawing
        plain = (TextScene, IconScene, IpScene, *CLOCKS)
        assert kinds[0] is IpScene
        assert kinds[3] is TextScene and kinds[6] is IconScene
        assert all(kind not in plain for kind in (kinds[1], kinds[2], kinds[4], kinds[5]))

    def test_never_the_same_effect_twice_in_a_row(self) -> None:
        # Given
        scene = ShowScene(seed=1, clock=lambda: TWO_PAST_TEN)
        # When
        kinds = [type(scene._effect().scene) for _ in range(300)]
        # Then
        assert all(a is not b for a, b in zip(kinds, kinds[1:], strict=False))

    def test_every_effect_can_play(self) -> None:
        # Given
        scene = ShowScene(seed=1, clock=lambda: TWO_PAST_TEN)
        # When
        kinds = {type(scene._effect().scene).__name__ for _ in range(400)}
        # Then
        assert len(kinds) == len(EFFECTS)

    def test_clock_every_five_minutes(self) -> None:
        # Given: 10:05:00
        moment = [datetime(2026, 10, 24, 10, 4, 58)]
        scene = ShowScene(seed=1, clock=lambda: moment[0])
        canvas = Canvas(10, 6)
        scene.render(canvas, 0)
        # When
        moment[0] = datetime(2026, 10, 24, 10, 5, 0)
        scene.render(canvas, 1)
        # Then
        assert scene._item is not None
        assert isinstance(scene._item.scene, CounterScene)
        assert scene._item.seconds == 60 + COUNTER_EXTRA_SECONDS

    def test_no_clock_between_the_slots(self) -> None:
        # Given: 10:06
        scene = ShowScene(seed=1, clock=lambda: datetime(2026, 10, 24, 10, 6, 0))
        # When
        seen = self.play(scene, 60)
        # Then
        assert not set(seen) & set(CLOCKS)

    def test_counter_fills_the_rest_of_the_minute(self) -> None:
        # Given
        scene = ShowScene(seed=1)
        # When
        items = scene.clock_items(datetime(2026, 10, 24, 10, 5, 20))
        # Then: 40 s left, plus a little to see the first square
        assert len(items) == 1
        assert isinstance(items[0].scene, CounterScene)
        assert items[0].seconds == 40 + COUNTER_EXTRA_SECONDS
        assert items[0].clock

    def test_clock_plays_once_per_slot(self) -> None:
        # Given: the whole 10:05 minute
        moment = [datetime(2026, 10, 24, 10, 5, 0)]
        scene = ShowScene(seed=1, clock=lambda: moment[0])
        canvas = Canvas(10, 6)
        counters = 0
        # When
        for frame in range(int(70 * scene.fps)):
            moment[0] = datetime(2026, 10, 24, 10, 5, 0) + timedelta(seconds=frame / scene.fps)
            before = scene._item
            scene.render(canvas, frame)
            if scene._item is not before and isinstance(scene._item.scene, CounterScene):
                counters += 1
        # Then
        assert counters == 1

    def test_shows_the_zzz_at_night(self) -> None:
        # Given
        scene = ShowScene(seed=1, clock=lambda: datetime(2026, 10, 24, 2, 1))
        # When
        icon = scene._icon().scene
        # Then
        assert isinstance(icon, IconScene)
        assert icon.pixels == ICONS["zzz"]

    def test_mixes_personal_messages_with_day_texts(self) -> None:
        # Given
        personal = Personal(messages=("HOLA ENRIC",))
        scene = ShowScene(personal, seed=1, clock=lambda: SATURDAY)
        # When
        texts = {scene._text() for _ in range(200)}
        # Then
        assert "HOLA ENRIC" in texts
        assert "BON DISSABTE" in texts

    def test_writes_in_the_language_of_the_locale(self) -> None:
        # Given
        locale = Locale(MatrixLanguage.english)
        scene = ShowScene(seed=1, clock=lambda: SATURDAY, locale=locale)
        # When
        english = {scene._text() for _ in range(100)}
        locale.set(MatrixLanguage.spanish)
        spanish = {scene._text() for _ in range(100)}
        # Then
        assert english == {"GOOD MORNING", "24 OCT", "HAPPY SATURDAY"}
        assert spanish == {"BUENOS DÍAS", "24 OCT", "FELIZ SÁBADO"}

    def test_prefers_the_text_of_a_personal_date(self) -> None:
        # Given
        personal = Personal(dates={"10-24": ("FELICITATS!",)})
        scene = ShowScene(personal, seed=1, clock=lambda: SATURDAY)
        # When
        texts = [scene._text() for _ in range(200)]
        # Then: about half of them
        assert 60 < texts.count("FELICITATS!") < 140

    def test_fades_in_from_black(self) -> None:
        # Given
        canvas = Canvas(10, 6)
        scene = ShowScene(seed=1, clock=lambda: TWO_PAST_TEN)
        scene._items = iter([lambda: ShowItem(RainbowScene(), EFFECT_SECONDS)])
        # When
        scene.render(canvas, 0)
        dark = max(max(color) for row in canvas.rows() for color in row)
        for frame in range(1, int(scene.fps)):
            scene.render(canvas, frame)
        # Then
        assert dark == 0
        assert max(max(color) for row in canvas.rows() for color in row) == 255

    def test_effect_ends_after_its_time(self) -> None:
        # Given: an effect, then a text
        canvas = Canvas(10, 6)
        scene = ShowScene(seed=1, clock=lambda: TWO_PAST_TEN)
        scene._items = iter(
            [
                lambda: ShowItem(RainbowScene(), EFFECT_SECONDS),
                lambda: ShowItem(TextScene("HOLA"), None),
            ]
        )
        # When
        for frame in range(int(EFFECT_SECONDS * scene.fps) + 1):
            scene.render(canvas, frame)
        # Then
        assert scene._item is not None
        assert isinstance(scene._item.scene, TextScene)

    def test_effect_that_is_done_ends_early(self) -> None:
        # Given: a maze, then a text
        canvas = Canvas(10, 6)
        scene = ShowScene(seed=1, clock=lambda: TWO_PAST_TEN)
        scene._items = iter(
            [
                lambda: ShowItem(MazeScene(seed=3), 600.0),
                lambda: ShowItem(TextScene("HOLA"), None),
            ]
        )
        # When: well before the time limit
        for frame in range(int(120 * scene.fps)):
            scene.render(canvas, frame)
            if isinstance(scene._item.scene, TextScene):
                break
        # Then
        assert isinstance(scene._item.scene, TextScene)
