from __future__ import annotations

from signal import SIGTERM

import pytest
import typer

from wordclock.matrix.cli import parse_color, stop_on_sigterm


class TestParseColor:
    @pytest.mark.parametrize("value", ["ff8800", "#ff8800"])
    def test_reads_hex_with_or_without_hash(self, value: str) -> None:
        # Given / When
        color = parse_color(value)
        # Then
        assert color == (255, 136, 0)

    def test_rejects_other_text(self) -> None:
        # Given / When / Then
        with pytest.raises(typer.BadParameter):
            parse_color("orange")


class TestStopOnSigterm:
    def test_stops_like_ctrl_c(self) -> None:
        # Given / When / Then: the runner turns the LEDs off on KeyboardInterrupt
        with pytest.raises(KeyboardInterrupt):
            stop_on_sigterm(SIGTERM, None)
