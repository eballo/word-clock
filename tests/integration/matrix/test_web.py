from __future__ import annotations

import base64
from io import BytesIO

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from wordclock.matrix.canvas import Canvas
from wordclock.matrix.runner import MatrixRunner
from wordclock.matrix.show import Personal
from wordclock.matrix.web import (
    FACE_PARAMS,
    MATRIX_SCAD,
    Simulator,
    WebLedController,
    create_matrix_app,
    scad_params,
)


@pytest.fixture()
def simulator() -> Simulator:
    controller = WebLedController(num_leds=60, brightness=40)
    runner = MatrixRunner(Canvas(10, 6), controller, max_ma=1500)
    return Simulator(runner, controller, Personal())


@pytest.fixture()
def client(simulator: Simulator) -> TestClient:
    with TestClient(create_matrix_app(simulator)) as c:
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
        self, client: TestClient, simulator: Simulator
    ) -> None:
        # Given: the first LED of row 1, which runs right to left
        simulator.controller.set_pixel(10, 1, 2, 3)
        simulator.controller.show()
        # When
        r = client.get("/api/matrix/frame")
        # Then: it is the last cell of row 1
        assert r.status_code == 200
        assert r.json()["cells"][1][9] == [1, 2, 3]
        assert r.json()["lights"] is True


class TestControls:
    def test_short_press_toggles_the_lights(self, client: TestClient, simulator: Simulator) -> None:
        # Given / When
        client.post("/api/matrix/button", json={"down": True})
        r = client.post("/api/matrix/button", json={"down": False})
        # Then
        assert r.status_code == 200
        assert r.json() == {"action": "toggle"}
        assert simulator.control.lights_on is False

    def test_switches_the_scene(self, client: TestClient, simulator: Simulator) -> None:
        # Given / When
        r = client.post("/api/matrix/scene", json={"name": "text", "text": "HI", "color": "ff0000"})
        # Then
        assert r.status_code == 200
        assert simulator.scene_name == "text"

    @pytest.mark.parametrize(
        "body", [{"name": "tetris"}, {"name": "text", "color": "red"}], ids=["scene", "colour"]
    )
    def test_rejects_a_bad_scene(self, client: TestClient, body: dict) -> None:
        # Given / When
        r = client.post("/api/matrix/scene", json=body)
        # Then
        assert r.status_code == 400

    def test_sets_the_brightness(self, client: TestClient, simulator: Simulator) -> None:
        # Given / When
        r = client.post("/api/matrix/brightness", json={"brightness": 120})
        bad = client.post("/api/matrix/brightness", json={"brightness": 300})
        # Then
        assert r.status_code == 200
        assert simulator.controller.brightness == 120
        assert bad.status_code == 400


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

    def test_countdown_asks_the_browser_for_a_frame(self, simulator: Simulator) -> None:
        # Given
        before = simulator.capture_id
        # When
        simulator.request_capture()
        # Then
        assert simulator.capture_id == before + 1
