from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

from wordclock.cad.bambu import (
    BED_SIZE,
    PLATE_STRIDE,
    Mesh,
    centred,
    count_bodies,
    plate_origin,
    read_stl,
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
