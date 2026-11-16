from __future__ import annotations

import base64
from datetime import datetime
from io import BytesIO

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from wordclock.matrix.canvas import Canvas
from wordclock.matrix.catalog import Catalog
from wordclock.matrix.dimmer import BrightnessLevels, Dimmer
from wordclock.matrix.runner import MatrixRunner
from wordclock.matrix.screens import PomodoroScene
from wordclock.matrix.show import Personal
from wordclock.matrix.web import (
    FACE_PARAMS,
    MATRIX_SCAD,
    MatrixService,
    WebLedController,
    create_matrix_app,
    scad_params,
)


@pytest.fixture()
def service() -> MatrixService:
    controller = WebLedController(num_leds=60, brightness=40)
    runner = MatrixRunner(Canvas(10, 6), controller, max_ma=1500)
    return MatrixService(runner, controller, Catalog(Personal()))


@pytest.fixture()
def client(service: MatrixService) -> TestClient:
    with TestClient(create_matrix_app(service)) as c:
        yield c


def png_data_url() -> str:
    data = BytesIO()
    Image.new("RGB", (40, 24), (255, 0, 0)).save(data, "PNG")
    return "data:image/png;base64," + base64.b64encode(data.getvalue()).decode()


class TestScadParams:
    def test_reads_the_face_sizes(self) -> None:
        # Given / When
        params = scad_params(MATRIX_SCAD, FACE_PARAMS)
        # Then
        assert params["cols"] == 10
        assert params["pitch"] == pytest.approx(1000 / 30)
        assert isinstance(params["cam_lens"], list)

    def test_missing_parameter(self) -> None:
        # Given / When / Then
        with pytest.raises(KeyError, match="nothing_here"):
            scad_params(MATRIX_SCAD, ("nothing_here",))


class TestPage:
    def test_serves_the_page_with_the_face_sizes(self, client: TestClient) -> None:
        # Given / When
        r = client.get("/")
        # Then
        assert r.status_code == 200
        assert '<canvas id="matrix"' in r.text
        assert '"margin_bottom"' in r.text

    def test_serves_the_script(self, client: TestClient) -> None:
        # Given / When
        r = client.get("/static/js/matrix.js")
        # Then
        assert r.status_code == 200


class TestFrame:
    def test_returns_the_picture_as_seen_from_the_front(
        self, client: TestClient, service: MatrixService
    ) -> None:
        # Given: the first LED of row 1, which runs right to left
        service.controller.set_pixel(10, 1, 2, 3)
        service.controller.show()
        # When
        r = client.get("/api/matrix/frame")
        # Then: it is the last cell of row 1
        assert r.status_code == 200
        assert r.json()["cells"][1][9] == [1, 2, 3]
        assert r.json()["lights"] is True


class TestControls:
    def test_short_press_toggles_the_lights(
        self, client: TestClient, service: MatrixService
    ) -> None:
        # Given / When
        client.post("/api/matrix/button", json={"down": True})
        r = client.post("/api/matrix/button", json={"down": False})
        # Then
        assert r.status_code == 200
        assert r.json() == {"action": "toggle"}
        assert service.control.lights_on is False

    def test_switches_the_scene(self, client: TestClient, service: MatrixService) -> None:
        # Given / When
        r = client.post("/api/matrix/scene", json={"name": "text", "text": "HI", "color": "ff0000"})
        # Then
        assert r.status_code == 200
        assert service.scene_name == "text"

    @pytest.mark.parametrize(
        "body", [{"name": "tetris"}, {"name": "text", "color": "red"}], ids=["scene", "colour"]
    )
    def test_rejects_a_bad_scene(self, client: TestClient, body: dict) -> None:
        # Given / When
        r = client.post("/api/matrix/scene", json=body)
        # Then
        assert r.status_code == 400

    def test_sets_the_brightness(self, client: TestClient, service: MatrixService) -> None:
        # Given / When
        r = client.post("/api/matrix/brightness", json={"brightness": 120})
        bad = client.post("/api/matrix/brightness", json={"brightness": 300})
        # Then
        assert r.status_code == 200
        assert service.controller.brightness == 120
        assert bad.status_code == 400

    def test_brightness_by_hand_holds_over_the_dimmer(self, service: MatrixService) -> None:
        # Given
        service.runner.dimmer = Dimmer(BrightnessLevels(), clock=lambda: datetime(2026, 1, 1, 13))
        with TestClient(create_matrix_app(service)) as client:
            auto = client.get("/api/matrix/frame").json()["auto_brightness"]
            # When
            client.post("/api/matrix/brightness", json={"brightness": 150})
            service.runner.show_frame()
            frame = client.get("/api/matrix/frame").json()
        # Then
        assert auto is True
        assert frame["brightness"] == 150
        assert frame["auto_brightness"] is False


class TestSimulatedTime:
    @pytest.fixture()
    def dimmed(self, service: MatrixService) -> MatrixService:
        levels = BrightnessLevels(day=90, evening=30, night=6)
        service.runner.dimmer = Dimmer(levels, clock=lambda: datetime(2026, 1, 1, 13))
        return service

    def test_frame_shows_the_time_of_day(self, dimmed: MatrixService) -> None:
        # Given
        with TestClient(create_matrix_app(dimmed)) as client:
            # When
            frame = client.get("/api/matrix/frame").json()
        # Then
        assert frame["time"] == "13:00"
        assert frame["phase"] == "day"
        assert frame["simulated_time"] is False
        assert frame["sun"] == {"sunrise": "08:00", "sunset": "19:00"}

    def test_sets_a_time_and_dims_the_strip(self, dimmed: MatrixService) -> None:
        # Given
        with TestClient(create_matrix_app(dimmed)) as client:
            # When
            r = client.post("/api/matrix/time", json={"time": "23:45"})
            frame = client.get("/api/matrix/frame").json()
        # Then
        assert r.status_code == 200
        assert r.json()["phase"] == "night"
        assert frame["time"] == "23:45"
        assert frame["simulated_time"] is True
        assert frame["brightness"] == 6

    def test_back_to_the_real_time(self, dimmed: MatrixService) -> None:
        # Given
        with TestClient(create_matrix_app(dimmed)) as client:
            client.post("/api/matrix/time", json={"time": "23:45"})
            # When
            r = client.post("/api/matrix/time", json={"time": None})
        # Then
        assert r.json()["simulated_time"] is False
        assert dimmed.controller.brightness == 90

    def test_rejects_a_bad_time(self, dimmed: MatrixService) -> None:
        # Given
        with TestClient(create_matrix_app(dimmed)) as client:
            # When
            r = client.post("/api/matrix/time", json={"time": "25:00"})
        # Then
        assert r.status_code == 400
        assert r.json() == {"detail": "time must be HH:MM"}

    def test_needs_the_automatic_brightness(self, client: TestClient) -> None:
        # Given: a fixed brightness, no dimmer
        # When
        r = client.post("/api/matrix/time", json={"time": "23:45"})
        frame = client.get("/api/matrix/frame").json()
        # Then
        assert r.status_code == 400
        assert "--brightness" in r.json()["detail"]
        assert frame["time"] is None


class TestLanguage:
    def test_catalan_by_default(self, client: TestClient) -> None:
        # Given / When
        r = client.get("/api/matrix/language")
        # Then
        assert r.status_code == 200
        assert r.json() == {
            "language": "catalan",
            "languages": ["catalan", "english", "spanish", "dutch"],
        }

    def test_switches_live(self, client: TestClient, service: MatrixService) -> None:
        # Given / When
        r = client.post("/api/matrix/language", json={"language": "english"})
        frame = client.get("/api/matrix/frame").json()
        # Then
        assert r.status_code == 200
        assert r.json()["language"] == "english"
        assert frame["language"] == "english"
        assert service.catalog.locale.texts.morning == "GOOD MORNING"

    def test_rejects_an_unknown_language(self, client: TestClient) -> None:
        # Given / When
        r = client.post("/api/matrix/language", json={"language": "klingon"})
        # Then
        assert r.status_code == 400
        assert r.json() == {"detail": "Unknown language: klingon"}

    def test_page_offers_the_languages(self, client: TestClient) -> None:
        # Given / When
        r = client.get("/")
        # Then
        assert '<option value="spanish">' in r.text
        assert '<option value="dutch">' in r.text


class TestApiDocs:
    def test_serves_swagger(self, client: TestClient) -> None:
        # Given / When
        r = client.get("/docs")
        # Then
        assert r.status_code == 200
        assert "swagger" in r.text.lower()

    def test_schema_lists_every_endpoint(self, client: TestClient) -> None:
        # Given / When
        schema = client.get("/openapi.json").json()
        # Then
        assert schema["info"]["title"] == "Mini Matrix API"
        assert {
            "/api/matrix/frame",
            "/api/matrix/scenes",
            "/api/matrix/scene",
            "/api/matrix/button",
            "/api/matrix/press",
            "/api/matrix/brightness",
            "/api/matrix/language",
            "/api/matrix/time",
            "/api/matrix/photo",
        } <= set(schema["paths"])

    def test_every_endpoint_has_a_tag_and_a_description(self, client: TestClient) -> None:
        # Given
        schema = client.get("/openapi.json").json()
        # When
        operations = [op for path in schema["paths"].values() for op in path.values()]
        # Then
        assert all(op.get("tags") and op.get("description") for op in operations)


class TestRemoteControl:
    def test_lists_the_scenes_that_can_play(self, client: TestClient) -> None:
        # Given: no city and no GitHub account
        # When
        r = client.get("/api/matrix/scenes")
        # Then
        assert r.status_code == 200
        assert "pomodoro" in r.json()["scenes"]
        assert "weather" not in r.json()["scenes"]
        assert r.json()["scene"] == "show"

    def test_weather_needs_a_city(self, client: TestClient) -> None:
        # Given / When
        r = client.post("/api/matrix/scene", json={"name": "weather"})
        # Then
        assert r.status_code == 400
        assert "city" in r.json()["detail"]

    def test_press_pauses_the_pomodoro(self, client: TestClient, service: MatrixService) -> None:
        # Given
        client.post("/api/matrix/scene", json={"name": "pomodoro"})
        # When
        r = client.post("/api/matrix/press", json={})
        # Then: the press went to the pomodoro, the lights stay on
        assert r.json() == {"action": "toggle"}
        pomodoro = service.control._base.scene
        assert isinstance(pomodoro, PomodoroScene) and pomodoro.paused
        assert service.control.lights_on is True

    def test_press_can_ask_for_a_photo(self, client: TestClient) -> None:
        # Given / When
        r = client.post("/api/matrix/press", json={"action": "photo"})
        # Then
        assert r.json() == {"action": "photo"}


class TestPhoto:
    def test_shows_a_webcam_photo(self, client: TestClient) -> None:
        # Given / When
        r = client.post("/api/matrix/photo", json={"image": png_data_url()})
        # Then
        assert r.status_code == 200
        assert r.json() == {"cells": 60}

    def test_rejects_data_that_is_not_an_image(self, client: TestClient) -> None:
        # Given / When
        r = client.post("/api/matrix/photo", json={"image": "data:image/jpeg;base64,AAAA"})
        # Then
        assert r.status_code == 400
        assert r.json() == {"detail": "image must be a JPEG or PNG"}

    def test_countdown_asks_the_browser_for_a_frame(self, service: MatrixService) -> None:
        # Given
        before = service.capture_id
        # When
        service.request_capture()
        # Then
        assert service.capture_id == before + 1
