"""Shared fixtures for API integration tests."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from wordclock.api.app import create_app


@pytest.fixture()
def client() -> TestClient:
    app = create_app(led_controller=None)
    with TestClient(app) as c:
        yield c
