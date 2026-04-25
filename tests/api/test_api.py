"""Integration tests — Flask API."""

import pytest

from wordclock.api.app import create_app


@pytest.fixture()
def client():
    app = create_app(led_controller=None)
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


class TestHealth:
    def test_health_ok(self, client):
        r = client.get("/api/health")
        assert r.status_code == 200
        assert r.get_json()["status"] == "ok"


class TestGrid:
    def test_grid_default_language(self, client):
        r = client.get("/api/grid")
        assert r.status_code == 200
        data = r.get_json()
        assert data["rows"] == 16
        assert data["cols"] == 16
        assert len(data["grid"]) == 16

    def test_grid_unknown_language(self, client):
        r = client.get("/api/grid?lang=klingon")
        assert r.status_code == 400


class TestTime:
    def test_current_time(self, client):
        r = client.get("/api/time")
        assert r.status_code == 200
        data = r.get_json()
        assert "sentence" in data
        assert "coords" in data
        assert "led_indices" in data

    def test_specific_time(self, client):
        r = client.get("/api/time?h=10&m=15")
        assert r.status_code == 200
        data = r.get_json()
        assert "QUARTER" in data["sentence"]
        assert "PAST" in data["sentence"]

    def test_invalid_hour(self, client):
        r = client.get("/api/time?h=25&m=0")
        assert r.status_code == 400

    def test_invalid_minute(self, client):
        r = client.get("/api/time?h=10&m=61")
        assert r.status_code == 400

    def test_unknown_language(self, client):
        r = client.get("/api/time?lang=klingon")
        assert r.status_code == 400


class TestBrightness:
    def test_set_brightness(self, client):
        r = client.post("/api/brightness", json={"brightness": 100})
        assert r.status_code == 200
        assert r.get_json()["brightness"] == 100

    def test_invalid_brightness(self, client):
        r = client.post("/api/brightness", json={"brightness": 300})
        assert r.status_code == 400
