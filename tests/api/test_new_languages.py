import pytest
from fastapi.testclient import TestClient

from wordclock.api.app import create_app


@pytest.fixture()
def client():
    app = create_app(led_controller=None)
    with TestClient(app) as c:
        yield c


def test_api_catalan(client):
    r = client.get("/api/time?lang=catalan&h=10&m=15")
    assert r.status_code == 200
    data = r.json()
    assert data["language"] == "catalan"
    assert "QUART" in data["sentence"]
    assert "ONZE" in data["sentence"]


def test_api_spanish(client):
    r = client.get("/api/time?lang=spanish&h=10&m=30")
    assert r.status_code == 200
    data = r.json()
    assert data["language"] == "spanish"
    assert "DIEZ" in data["sentence"]
    assert "MEDIA" in data["sentence"]


def test_grid_catalan(client):
    r = client.get("/api/grid?lang=catalan")
    assert r.status_code == 200
    data = r.json()
    assert data["language"] == "catalan"
    assert len(data["grid"]) == 16


def test_grid_spanish(client):
    r = client.get("/api/grid?lang=spanish")
    assert r.status_code == 200
    data = r.json()
    assert data["language"] == "spanish"
    assert len(data["grid"]) == 16
