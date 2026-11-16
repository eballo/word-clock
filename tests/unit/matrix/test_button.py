from __future__ import annotations

import pytest

from wordclock.matrix.button import ButtonAction, ButtonHandler, action_for


class FakeClock:
    def __init__(self) -> None:
        self.now = 100.0

    def __call__(self) -> float:
        return self.now


class TestActionFor:
    @pytest.mark.parametrize(
        ("held", "action"),
        [
            (0.1, ButtonAction.TOGGLE),
            (2.9, ButtonAction.TOGGLE),
            (3.0, ButtonAction.PHOTO),
            (9.9, ButtonAction.PHOTO),
            (10.0, ButtonAction.SHUTDOWN),
        ],
    )
    def test_picks_the_action_by_time_held(self, held: float, action: ButtonAction) -> None:
        # Given / When / Then
        assert action_for(held) == action


class TestButtonHandler:
    def test_times_a_press(self) -> None:
        # Given
        clock = FakeClock()
        button = ButtonHandler(clock)
        # When: held for 4 s
        button.press()
        clock.now += 4
        action = button.release()
        # Then
        assert action == ButtonAction.PHOTO
        assert button.held() == 0

    def test_release_without_press_does_nothing(self) -> None:
        # Given
        button = ButtonHandler(FakeClock())
        # When / Then
        assert button.release() == ButtonAction.NONE

    def test_a_second_press_keeps_the_first_time(self) -> None:
        # Given: a repeated "down" from the switch or the browser
        clock = FakeClock()
        button = ButtonHandler(clock)
        button.press()
        clock.now += 2
        # When
        button.press()
        clock.now += 2
        # Then
        assert button.release() == ButtonAction.PHOTO
