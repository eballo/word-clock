"""Integration tests — multi-language API endpoints."""

from __future__ import annotations

from fastapi.testclient import TestClient


class TestCatalanApi:
    def test_time_returns_catalan_sentence(self, client: TestClient) -> None:
        # Given: catalan language, 10:15
        # When
        r = client.get("/api/time?lang=catalan&h=10&m=15")
        # Then: response contains a catalan quarter sentence
        assert r.status_code == 200
        data = r.json()
        assert data["language"] == "catalan"
        assert "QUART" in data["sentence"]
        assert "ONZE" in data["sentence"]

    def test_grid_returns_16x16(self, client: TestClient) -> None:
        # Given
        # When
        r = client.get("/api/grid?lang=catalan")
        # Then
        assert r.status_code == 200
        data = r.json()
        assert data["language"] == "catalan"
        assert len(data["grid"]) == 16

    def test_en_punt_sentence(self, client: TestClient) -> None:
        # Given: hour on the dot
        # When
        r = client.get("/api/time?lang=catalan&h=2&m=0")
        # Then
        assert r.status_code == 200
        assert "EN PUNT" in r.json()["sentence"]


class TestSpanishApi:
    def test_time_returns_spanish_sentence(self, client: TestClient) -> None:
        # Given: spanish language, 10:30
        # When
        r = client.get("/api/time?lang=spanish&h=10&m=30")
        # Then
        assert r.status_code == 200
        data = r.json()
        assert data["language"] == "spanish"
        assert "DIEZ" in data["sentence"]
        assert "MEDIA" in data["sentence"]

    def test_grid_returns_16x16(self, client: TestClient) -> None:
        # Given
        # When
        r = client.get("/api/grid?lang=spanish")
        # Then
        assert r.status_code == 200
        data = r.json()
        assert data["language"] == "spanish"
        assert len(data["grid"]) == 16

    def test_en_punto_sentence(self, client: TestClient) -> None:
        # Given: hour on the dot
        # When
        r = client.get("/api/time?lang=spanish&h=1&m=0")
        # Then
        assert r.status_code == 200
        assert "EN PUNTO" in r.json()["sentence"]


class TestEnglishApi:
    def test_time_returns_english_sentence(self, client: TestClient) -> None:
        # Given: english language, 10:15
        # When
        r = client.get("/api/time?lang=english&h=10&m=15")
        # Then
        assert r.status_code == 200
        data = r.json()
        assert data["language"] == "english"
        assert "QUARTER" in data["sentence"]
        assert "PAST" in data["sentence"]

    def test_grid_returns_16x16(self, client: TestClient) -> None:
        # Given
        # When
        r = client.get("/api/grid?lang=english")
        # Then
        assert r.status_code == 200
        data = r.json()
        assert data["language"] == "english"
        assert len(data["grid"]) == 16

    def test_oclock_sentence(self, client: TestClient) -> None:
        # Given: hour on the dot
        # When
        r = client.get("/api/time?lang=english&h=3&m=0")
        # Then
        assert r.status_code == 200
        assert "OCLOCK" in r.json()["sentence"]


class TestUnsupportedLanguage:
    def test_time_returns_400_with_detail(self, client: TestClient) -> None:
        # Given: a language that does not exist
        lang = "klingon"
        # When
        r = client.get(f"/api/time?lang={lang}")
        # Then: 400 status and detail identifies the unknown language
        assert r.status_code == 400
        assert "klingon" in r.json()["detail"]

    def test_grid_returns_400_with_detail(self, client: TestClient) -> None:
        # Given: a language that does not exist
        lang = "klingon"
        # When
        r = client.get(f"/api/grid?lang={lang}")
        # Then: 400 status and detail identifies the unknown language
        assert r.status_code == 400
        assert "klingon" in r.json()["detail"]
