from __future__ import annotations

from datetime import date

import pytest

from wordclock.matrix import feeds
from wordclock.matrix.feeds import (
    Feed,
    Weather,
    contribution_level,
    contributions_fetcher,
    parse_contributions,
    parse_weather,
    weather_fetcher,
    weather_kind,
)


class FakeClock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now


def contributions_answer(counts: dict[str, int]) -> dict:
    days = [{"date": day, "contributionCount": n} for day, n in counts.items()]
    calendar = {"weeks": [{"contributionDays": days}]}
    return {"data": {"user": {"contributionsCollection": {"contributionCalendar": calendar}}}}


class TestFeed:
    def test_fetches_on_first_use(self) -> None:
        # Given
        feed = Feed(lambda: 42, interval=60, name="test", background=False)
        # When / Then
        assert feed.get() == 42

    def test_refreshes_only_when_stale(self) -> None:
        # Given
        clock = FakeClock()
        calls: list[int] = []
        feed = Feed(lambda: calls.append(1) or len(calls), 60, "test", clock, background=False)
        # When
        feed.get()
        clock.now = 30
        feed.get()
        clock.now = 61
        value = feed.get()
        # Then
        assert calls == [1, 1]
        assert value == 2

    def test_keeps_the_last_value_when_a_fetch_fails(self) -> None:
        # Given
        clock = FakeClock()
        answers = iter([7])

        def fetch() -> int:
            return next(answers, None) or (_ for _ in ()).throw(OSError("offline"))

        feed = Feed(fetch, 60, "test", clock, background=False)
        feed.get()
        # When
        clock.now = 61
        value = feed.get()
        # Then
        assert value == 7
        assert feed.error == "offline"


class TestWeather:
    @pytest.mark.parametrize(
        ("code", "kind"),
        [(0, "clear"), (2, "cloudy"), (45, "fog"), (53, "drizzle"), (63, "rain")]
        + [(81, "rain"), (73, "snow"), (95, "storm"), (1234, "cloudy")],
    )
    def test_groups_the_wmo_codes(self, code: int, kind: str) -> None:
        # Given / When / Then
        assert weather_kind(code) == kind

    def test_reads_the_current_weather(self) -> None:
        # Given
        data = {"current": {"temperature_2m": 17.6, "weather_code": 61, "is_day": 0}}
        # When / Then
        assert parse_weather(data) == Weather(17.6, 61, False)

    def test_looks_the_city_up_once(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # Given
        urls: list[str] = []

        def fake_get_json(url: str, headers=None, body=None) -> dict:
            urls.append(url)
            if url.startswith(feeds.GEOCODING_URL):
                return {"results": [{"latitude": 41.4, "longitude": 2.2}]}
            return {"current": {"temperature_2m": 20, "weather_code": 0, "is_day": 1}}

        monkeypatch.setattr(feeds, "get_json", fake_get_json)
        fetch = weather_fetcher("Barcelona")
        # When
        fetch()
        weather = fetch()
        # Then
        assert weather == Weather(20.0, 0, True)
        assert sum(url.startswith(feeds.GEOCODING_URL) for url in urls) == 1
        assert "latitude=41.4" in urls[-1]

    def test_unknown_city(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # Given
        monkeypatch.setattr(feeds, "get_json", lambda url, headers=None, body=None: {})
        # When / Then
        with pytest.raises(KeyError, match="Atlantis"):
            weather_fetcher("Atlantis")()


class TestContributions:
    def test_one_count_per_day_ending_today(self) -> None:
        # Given
        data = contributions_answer({"2026-10-24": 3, "2026-10-25": 1, "2026-01-01": 9})
        # When
        counts = parse_contributions(data, 3, date(2026, 10, 25))
        # Then
        assert counts == [0, 3, 1]

    def test_github_errors_raise(self) -> None:
        # Given
        data = {"errors": [{"message": "Bad credentials"}]}
        # When / Then
        with pytest.raises(ValueError, match="Bad credentials"):
            parse_contributions(data, 60, date(2026, 10, 25))

    def test_sends_the_token_and_the_dates(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # Given
        sent: dict = {}

        def fake_get_json(url: str, headers=None, body=None) -> dict:
            sent.update(url=url, headers=headers, body=body)
            return contributions_answer({"2026-10-25": 2})

        monkeypatch.setattr(feeds, "get_json", fake_get_json)
        fetch = contributions_fetcher("eballo", "secret", 60, today=lambda: date(2026, 10, 25))
        # When
        counts = fetch()
        # Then
        assert counts[-1] == 2 and len(counts) == 60
        assert sent["headers"] == {"Authorization": "Bearer secret"}
        assert sent["body"]["variables"]["from"] == "2026-08-27T00:00:00Z"

    @pytest.mark.parametrize(("count", "level"), [(0, 0), (1, 1), (5, 2), (9, 3), (12, 4)])
    def test_levels_like_github(self, count: int, level: int) -> None:
        # Given / When / Then
        assert contribution_level(count, [0, 1, 12]) == level
