from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest

from wordclock.cad.bambu import (
    BED_SIZE,
    BLACK,
    PLATE_STRIDE,
    Mesh,
    centred,
    count_bodies,
    pack_plate,
    plate_origin,
    project_settings,
    read_stl,
    write_plate,
    write_project,
)

# Two triangles sharing an edge: a 10 x 10 mm square at z = 5
SQUARE_STL = """solid square
facet normal 0 0 1
 outer loop
  vertex 10 10 5
  vertex 20 10 5
  vertex 20 20 5
 endloop
endfacet
facet normal 0 0 1
 outer loop
  vertex 10 10 5
  vertex 20 20 5
  vertex 10 20 5
 endloop
endfacet
endsolid square
"""


@pytest.fixture
def square_stl(tmp_path: Path) -> Path:
    path = tmp_path / "square.stl"
    path.write_text(SQUARE_STL, encoding="ascii")
    return path


class TestReadStl:
    def test_merges_shared_corners(self, square_stl: Path) -> None:
        # Given: two triangles with two shared corners
        # When
        mesh = read_stl(square_stl)
        # Then
        assert len(mesh.vertices) == 4
        assert mesh.triangles == [(0, 1, 2), (0, 2, 3)]


class TestCountBodies:
    def test_one_body_when_triangles_share_vertices(self, square_stl: Path) -> None:
        # Given: a square made of two triangles
        mesh = read_stl(square_stl)
        # When / Then
        assert count_bodies(mesh) == 1

    def test_counts_separate_pieces(self) -> None:
        # Given: two triangles with no shared vertex
        mesh = Mesh(
            [(0, 0, 0), (1, 0, 0), (0, 1, 0), (5, 5, 0), (6, 5, 0), (5, 6, 0)],
            [(0, 1, 2), (3, 4, 5)],
        )
        # When / Then
        assert count_bodies(mesh) == 2


class TestCentred:
    def test_centres_footprint_and_rests_on_bed(self, square_stl: Path) -> None:
        # Given
        mesh = read_stl(square_stl)
        # When
        moved = centred(mesh)
        # Then
        xs = [v[0] for v in moved.vertices]
        ys = [v[1] for v in moved.vertices]
        assert (min(xs), max(xs), min(ys), max(ys)) == (-5, 5, -5, 5)
        assert {v[2] for v in moved.vertices} == {0}

    def test_keeps_triangles(self) -> None:
        # Given
        mesh = Mesh([(0, 0, 1), (2, 0, 1), (0, 2, 1)], [(0, 1, 2)])
        # When / Then
        assert centred(mesh).triangles == [(0, 1, 2)]


class TestPlateOrigin:
    def test_first_plate_at_origin(self) -> None:
        # Given / When / Then
        assert plate_origin(0, 9) == (0, 0)

    def test_nine_plates_in_three_columns(self) -> None:
        # Given
        count = 9
        # When
        origins = [plate_origin(k, count) for k in range(count)]
        # Then
        assert origins[2] == (2 * PLATE_STRIDE, 0)
        assert origins[3] == (0, -PLATE_STRIDE)
        assert origins[8] == (2 * PLATE_STRIDE, -2 * PLATE_STRIDE)

    def test_ten_plates_in_four_columns(self) -> None:
        # Given / When / Then
        assert plate_origin(4, 10) == (0, -PLATE_STRIDE)


class TestWriteProject:
    def test_one_plate_per_stl(self, square_stl: Path, tmp_path: Path) -> None:
        # Given
        output = tmp_path / "out.3mf"
        # When
        write_project([square_stl, square_stl], output, {"sparse_infill_density": "100%"})
        # Then
        with zipfile.ZipFile(output) as zf:
            names = set(zf.namelist())
            settings = zf.read("Metadata/model_settings.config").decode()
            model = zf.read("3D/3dmodel.model").decode()
        assert {"3D/Objects/object_1.model", "3D/Objects/object_2.model"} <= names
        assert "Metadata/project_settings.config" in names
        assert settings.count("<plate>") == 2
        assert 'key="sparse_infill_density" value="100%"' in settings
        centre = BED_SIZE / 2
        assert f"{centre:.4f} {centre:.4f} 0" in model
        assert f"{PLATE_STRIDE + centre:.4f} {centre:.4f} 0" in model


class TestPackPlate:
    def test_rows_of_parts_with_gaps(self) -> None:
        # Given: three 100 mm squares on a 256 mm bed
        sizes = [(100.0, 100.0)] * 3
        # When
        centres = pack_plate(sizes)
        # Then: two in the first row, one in the second
        assert centres[0] == (56.0, 56.0)
        assert centres[1] == (162.0, 56.0)
        assert centres[2] == (56.0, 162.0)

    def test_parts_never_overlap(self) -> None:
        # Given
        sizes = [(80.0, 70.0), (100.0, 60.0), (45.0, 50.0), (40.0, 50.0), (75.0, 45.0)]
        # When
        centres = pack_plate(sizes)
        # Then
        boxes = [
            (cx - w / 2, cy - d / 2, cx + w / 2, cy + d / 2)
            for (cx, cy), (w, d) in zip(centres, sizes, strict=True)
        ]
        for i, a in enumerate(boxes):
            assert a[0] >= 0 and a[1] >= 0 and a[2] <= BED_SIZE and a[3] <= BED_SIZE
            for b in boxes[i + 1 :]:
                assert a[2] <= b[0] or b[2] <= a[0] or a[3] <= b[1] or b[3] <= a[1]

    def test_too_many_parts(self) -> None:
        # Given / When / Then
        with pytest.raises(ValueError, match="do not fit"):
            pack_plate([(120.0, 120.0)] * 5)


class TestWritePlate:
    def test_every_part_on_the_first_plate(self, tmp_path: Path, square_stl: Path) -> None:
        # Given
        output = tmp_path / "test.3mf"
        # When
        write_plate([square_stl, square_stl, square_stl], output)
        # Then
        with zipfile.ZipFile(output) as zf:
            settings = zf.read("Metadata/model_settings.config").decode()
            model = zf.read("3D/3dmodel.model").decode()
        assert settings.count("<plate>") == 1
        assert settings.count("<model_instance>") == 3
        assert model.count("<item ") == 3


class TestProjectColour:
    def test_colour_in_the_project_settings(self, tmp_path: Path, square_stl: Path) -> None:
        # Given
        output = tmp_path / "black.3mf"
        # When
        write_project([square_stl], output, colour=BLACK)
        # Then
        with zipfile.ZipFile(output) as zf:
            settings = json.loads(zf.read("Metadata/project_settings.config"))
        assert settings["filament_colour"] == ["#000000"]
        assert settings["filament_type"] == ["PLA"]

    def test_default_colour_kept(self) -> None:
        # Given / When
        settings = json.loads(project_settings())
        # Then
        assert settings["filament_colour"] == ["#00AE42"]
