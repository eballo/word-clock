from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pytest

from wordclock.matrix.canvas import Canvas
from wordclock.matrix.clocks import BlocksClock, DialClock, TixClock
from wordclock.matrix.font import GLYPHS, fold_char
from wordclock.matrix.scenes import (
    ClockScene,
    IpScene,
    RainbowScene,
    RainScene,
    SparkleScene,
    TextScene,
)
from wordclock.matrix.show import (
    EFFECT_SECONDS,
    ICON_SECONDS,
    ICONS,
    MONTHS,
    WEEKDAYS,
    IconScene,
    Personal,
    ShowScene,
    date_text,
    day_texts,
    greeting,
    load_personal,
)

# Every kind of clock the show plays.
CLOCKS = (ClockScene, BlocksClock, DialClock, TixClock)

# 24 October 2026 is a Saturday.
SATURDAY = datetime(2026, 10, 24, 10, 0)


def every_day_text() -> list[str]:
    texts: set[str] = set()
    for day in range(19, 26):
        for hour in range(24):
            texts.update(day_texts(datetime(2026, 10, day, hour)))
    return sorted(texts)


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

    @pytest.mark.parametrize("text", every_day_text() + list(WEEKDAYS + MONTHS))
    def test_every_text_has_glyphs(self, text: str) -> None:
        # Given / When
        missing = [char for char in text if fold_char(char) not in GLYPHS]
        # Then
        assert missing == []


class TestLoadPersonal:
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

    @pytest.mark.parametrize("content", ["messages = [", "messages = [1, 2]", "dates = 3"])
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

    def test_plays_ip_then_clock_text_effect_clock_text_icon(self) -> None:
        # Given
        scene = ShowScene(seed=1, clock=lambda: SATURDAY)
        # When: long enough for one round
        seen = self.play(scene, 120 + EFFECT_SECONDS + ICON_SECONDS)
        # Then
        assert seen[0] is IpScene
        assert seen[1] in CLOCKS and seen[2] is TextScene
        assert seen[3] in (RainbowScene, RainScene, SparkleScene)
        assert seen[4] in CLOCKS and seen[5:7] == [TextScene, IconScene]

    def test_uses_every_kind_of_clock(self) -> None:
        # Given
        scene = ShowScene(seed=1, clock=lambda: SATURDAY)
        # When
        kinds = {type(scene._clock_scene()) for _ in range(100)}
        # Then
        assert kinds == set(CLOCKS)

    def test_shows_the_zzz_at_night(self) -> None:
        # Given
        scene = ShowScene(seed=1, clock=lambda: datetime(2026, 10, 24, 2, 0))
        # When
        icon = scene._icon()
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
        scene = ShowScene(seed=1)
        scene._items = iter([RainbowScene])
        # When
        scene.render(canvas, 0)
        dark = max(max(color) for row in canvas.rows() for color in row)
        for frame in range(1, int(scene.fps)):
            scene.render(canvas, frame)
        # Then
        assert dark == 0
        assert max(max(color) for row in canvas.rows() for color in row) == 255

    def test_effect_ends_after_its_time(self) -> None:
        # Given: an effect, then a clock
        canvas = Canvas(10, 6)
        scene = ShowScene(seed=1)
        scene._items = iter([RainbowScene, ClockScene])
        # When
        for frame in range(int(EFFECT_SECONDS * scene.fps) + 1):
            scene.render(canvas, frame)
        # Then
        assert scene._item is not None
        assert isinstance(scene._item.scene, ClockScene)
