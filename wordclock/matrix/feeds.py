from __future__ import annotations

import json
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, timedelta
from logging import getLogger
from threading import Lock, Thread
from typing import Generic, TypeVar
from urllib.parse import urlencode
from urllib.request import Request, urlopen

logger = getLogger(__name__)

HTTP_TIMEOUT = 10
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"

T = TypeVar("T")


def get_json(url: str, headers: dict[str, str] | None = None, body: dict | None = None) -> dict:
    """
    Fetch a JSON document, with a GET or, when there is a body, a POST.

    Args:
        url: The address.
        headers: Extra request headers.
        body: JSON body to POST.

    Returns:
        The decoded JSON object.

    Raises:
        OSError: On a network or HTTP error.
        ValueError: If the answer is not JSON.
    """
    data = json.dumps(body).encode() if body is not None else None
    request = Request(url, data=data, headers={"User-Agent": "wordclock-matrix", **(headers or {})})
    with urlopen(request, timeout=HTTP_TIMEOUT) as response:
        return json.loads(response.read())


class Feed(Generic[T]):
    """
    Data from the network, refreshed in the background.

    Scenes call :meth:`get` every frame: it never waits for the network. It
    returns the last value (None until the first fetch ends) and starts a
    refresh in a thread when the value is older than the interval.
    """

    def __init__(
        self,
        fetch: Callable[[], T],
        interval: float,
        name: str,
        clock: Callable[[], float] = time.monotonic,
        background: bool = True,
    ) -> None:
        self._fetch = fetch
        self.interval = interval
        self.name = name
        self._clock = clock
        self._background = background
        self._lock = Lock()
        self._busy = False
        self._fetched_at: float | None = None
        self.value: T | None = None
        self.error: str | None = None

    def get(self) -> T | None:
        """
        Return the last value, and refresh it when it is stale.

        Returns:
            The value, or None before the first successful fetch.
        """
        with self._lock:
            stale = self._fetched_at is None or self._clock() - self._fetched_at >= self.interval
            start = stale and not self._busy
            if start:
                self._busy = True
                # Count a failed fetch too, so a dead network is not hammered.
                self._fetched_at = self._clock()
        if start:
            if self._background:
                Thread(target=self._refresh, name=f"feed-{self.name}", daemon=True).start()
            else:
                self._refresh()
        return self.value

    def _refresh(self) -> None:
        try:
            value = self._fetch()
        except (OSError, ValueError, KeyError, TypeError) as exc:
            logger.warning("%s: %s", self.name, exc)
            self.error = str(exc)
        else:
            self.value = value
            self.error = None
        finally:
            with self._lock:
                self._busy = False


# --- Weather ----------------------------------------------------------------


@dataclass(frozen=True)
class Weather:
    """The weather now, from Open-Meteo."""

    temperature: float
    code: int
    is_day: bool


# WMO weather codes, as Open-Meteo gives them, grouped by what is drawn.
WEATHER_KINDS: tuple[tuple[str, frozenset[int]], ...] = (
    ("clear", frozenset({0})),
    ("cloudy", frozenset({1, 2, 3})),
    ("fog", frozenset({45, 48})),
    ("drizzle", frozenset({51, 53, 55, 56, 57})),
    ("rain", frozenset({61, 63, 65, 66, 67, 80, 81, 82})),
    ("snow", frozenset({71, 73, 75, 77, 85, 86})),
    ("storm", frozenset({95, 96, 99})),
)

WEATHER_WORDS: dict[str, str] = {
    "clear": "SOL",
    "cloudy": "NÚVOLS",
    "fog": "BOIRA",
    "drizzle": "PLUGIM",
    "rain": "PLUJA",
    "snow": "NEU",
    "storm": "TEMPESTA",
}


def weather_kind(code: int) -> str:
    """
    Group a WMO weather code into what the matrix draws.

    Args:
        code: The WMO code.

    Returns:
        One of the keys of :data:`WEATHER_WORDS`; ``cloudy`` for unknown codes.
    """
    return next((kind for kind, codes in WEATHER_KINDS if code in codes), "cloudy")


def geocode(city: str) -> tuple[float, float]:
    """
    Find the coordinates of a city with the Open-Meteo geocoding API.

    Args:
        city: City name, such as ``Barcelona``.

    Returns:
        Latitude and longitude.

    Raises:
        KeyError: If the city is not found.
    """
    query = urlencode({"name": city, "count": 1, "language": "ca", "format": "json"})
    results = get_json(f"{GEOCODING_URL}?{query}").get("results") or []
    if not results:
        raise KeyError(f"City not found: {city}")
    return results[0]["latitude"], results[0]["longitude"]


def parse_weather(data: dict) -> Weather:
    """
    Read the current weather from an Open-Meteo forecast answer.

    Args:
        data: The decoded answer, with a ``current`` block.

    Returns:
        The weather now.
    """
    current = data["current"]
    return Weather(
        temperature=float(current["temperature_2m"]),
        code=int(current["weather_code"]),
        is_day=bool(current["is_day"]),
    )


def weather_fetcher(city: str) -> Callable[[], Weather]:
    """
    Build the fetch function of a weather feed.

    Args:
        city: City name; it is looked up once, on the first fetch.

    Returns:
        A function that returns the weather now.
    """
    place: list[tuple[float, float]] = []

    def fetch() -> Weather:
        if not place:
            place.append(geocode(city))
        latitude, longitude = place[0]
        query = urlencode(
            {
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m,weather_code,is_day",
            }
        )
        return parse_weather(get_json(f"{FORECAST_URL}?{query}"))

    return fetch


# --- GitHub contributions ---------------------------------------------------

CONTRIBUTIONS_QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar {
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""


def parse_contributions(data: dict, days: int, today: date) -> list[int]:
    """
    Read daily contribution counts from a GitHub GraphQL answer.

    Args:
        data: The decoded answer.
        days: How many days to return.
        today: The last day.

    Returns:
        One count per day, oldest first, ending today; 0 for missing days.

    Raises:
        ValueError: If GitHub answered with errors.
    """
    if data.get("errors"):
        raise ValueError(data["errors"][0].get("message", "GitHub error"))
    weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    counts = {
        day["date"]: day["contributionCount"] for week in weeks for day in week["contributionDays"]
    }
    first = today - timedelta(days=days - 1)
    return [counts.get((first + timedelta(days=i)).isoformat(), 0) for i in range(days)]


def contributions_fetcher(
    user: str, token: str, days: int, today: Callable[[], date] = date.today
) -> Callable[[], list[int]]:
    """
    Build the fetch function of a GitHub contributions feed.

    Args:
        user: GitHub login.
        token: A GitHub token; no scopes are needed for public contributions.
        days: How many days to fetch.
        today: Today's date.

    Returns:
        A function that returns the daily counts, oldest first.
    """

    def fetch() -> list[int]:
        end = today()
        start = end - timedelta(days=days - 1)
        variables = {
            "login": user,
            "from": f"{start.isoformat()}T00:00:00Z",
            "to": f"{end.isoformat()}T23:59:59Z",
        }
        data = get_json(
            GITHUB_GRAPHQL_URL,
            headers={"Authorization": f"Bearer {token}"},
            body={"query": CONTRIBUTIONS_QUERY, "variables": variables},
        )
        return parse_contributions(data, days, end)

    return fetch


def contribution_level(count: int, counts: list[int]) -> int:
    """
    Shade a day like GitHub does: 0 for no contributions, then 1 to 4 by
    quarters of the busiest day.

    Args:
        count: Contributions on the day.
        counts: Contributions on every day shown.

    Returns:
        The level, 0 to 4.
    """
    top = max(counts, default=0)
    if count <= 0 or top <= 0:
        return 0
    return min(4, 1 + (4 * (count - 1)) // top)
