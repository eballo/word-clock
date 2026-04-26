"""Integration tests — core API endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient


class TestHealth:
    def test_returns_ok_status(self, client: TestClient) -> None:
        # Given: the API is running
        # When: health endpoint is called
        r = client.get("/api/health")
        # Then: status is ok
        assert r.status_code == 200
        assert r.json()["status"] == "ok"


class TestGrid:
    def test_default_language_returns_16x16_grid(self, client: TestClient) -> None:
        # Given: no language specified (defaults to english)
        # When
        r = client.get("/api/grid")
        # Then: 16×16 grid is returned
        assert r.status_code == 200
        data = r.json()
        assert data["rows"] == 16
        assert data["cols"] == 16
        assert len(data["grid"]) == 16

    def test_unknown_language_returns_400(self, client: TestClient) -> None:
        # Given: a language that does not exist
        # When
        r = client.get("/api/grid?lang=klingon")
        # Then
        assert r.status_code == 400


class TestTime:
    def test_current_time_returns_required_fields(self, client: TestClient) -> None:
        # Given: no time parameters (uses current time)
        # When
        r = client.get("/api/time")
        # Then: all required fields are present
        assert r.status_code == 200
        data = r.json()
        assert "sentence" in data
        assert "coords" in data
        assert "led_indices" in data

    def test_specific_time_returns_correct_sentence(self, client: TestClient) -> None:
        # Given: a specific time where quarter past is expected
        # When
        r = client.get("/api/time?h=10&m=15")
        # Then
        assert r.status_code == 200
        data = r.json()
        assert "QUARTER" in data["sentence"]
        assert "PAST" in data["sentence"]

    def test_invalid_hour_returns_400(self, client: TestClient) -> None:
        # Given: hour out of 0-23 range
        # When
        r = client.get("/api/time?h=25&m=0")
        # Then
        assert r.status_code == 400

    def test_invalid_minute_returns_400(self, client: TestClient) -> None:
        # Given: minute out of 0-59 range
        # When
        r = client.get("/api/time?h=10&m=61")
        # Then
        assert r.status_code == 400

    def test_unknown_language_returns_400(self, client: TestClient) -> None:
        # Given
        # When
        r = client.get("/api/time?lang=klingon")
        # Then
        assert r.status_code == 400


class TestBrightness:
    def test_valid_brightness_is_accepted(self, client: TestClient) -> None:
        # Given: brightness within 0-255
        # When
        r = client.post("/api/brightness", json={"brightness": 100})
        # Then
        assert r.status_code == 200
        assert r.json()["brightness"] == 100

    def test_brightness_above_255_returns_400(self, client: TestClient) -> None:
        # Given: brightness above maximum
        # When
        r = client.post("/api/brightness", json={"brightness": 300})
        # Then
        assert r.status_code == 400
