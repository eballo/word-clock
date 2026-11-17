from __future__ import annotations

import zipfile
from pathlib import Path

from wordclock.cad import (
    BOX_PIECES,
    BOX_SCAD_FILE,
    BOX_TEST_PIECES,
    EXTRA_PARTS,
    FACE_PARTS,
    MATRIX_BOX_PART,
    MATRIX_HALVES,
    MATRIX_PARTS,
    MATRIX_SCAD_FILE,
    MATRIX_SINGLE_PARTS,
    OPTIONAL_PARTS,
    SCAD_FILE,
    TEST_TILE,
    TILE_SPLITS,
    TILES,
    RenderJob,
    oversized_parts,
    plan_box_jobs,
    plan_box_test_jobs,
    plan_jobs,
    plan_matrix_jobs,
    scad_command,
    scad_string_list,
    write_bambu_projects,
    write_box_projects,
    write_matrix_projects,
    write_preview,
)


class TestScadStringList:
    def test_formats_plain_strings(self) -> None:
        # Given
        values = ["AB", "CD"]
        # When
        literal = scad_string_list(values)
        # Then
        assert literal == '["AB", "CD"]'

    def test_escapes_quotes_and_backslashes(self) -> None:
        # Given
        values = ['A"B', "C\\D"]
        # When
        literal = scad_string_list(values)
        # Then
        assert literal == '["A\\"B", "C\\\\D"]'

    def test_keeps_accents_and_apostrophes(self) -> None:
        # Given: a Catalan row
        values = ["ÉSÓND'LA"]
        # When
        literal = scad_string_list(values)
        # Then
        assert literal == '["ÉSÓND\'LA"]'


class TestScadCommand:
    def test_includes_part_tile_and_rows(self) -> None:
        # Given
        job = RenderJob("face", Path("out/face.stl"), (0, 8, 0, 8), ("AB",))
        # When
        cmd = scad_command(job)
        # Then
        assert cmd[0] == "openscad"
        assert 'part="face"' in cmd
        assert "tile=[0, 8, 0, 8]" in cmd
        assert 'rows=["AB"]' in cmd
        assert cmd[-1] == str(SCAD_FILE)

    def test_omits_tile_and_rows_when_not_set(self) -> None:
        # Given
        job = RenderJob("screenback", Path("out/screenback.stl"))
        # When
        cmd = scad_command(job, openscad="/opt/bin/openscad")
        # Then
        assert cmd[0] == "/opt/bin/openscad"
        assert not any(arg.startswith(("tile=", "rows=")) for arg in cmd)


class TestPlanJobs:
    def test_full_build_for_one_language(self) -> None:
        # Given
        out = Path("build")
        # When
        jobs = plan_jobs(["catalan"], out)
        # Then: face parts per tile, one grid per tile and the screen module
        assert len(jobs) == len(TILES) * len(FACE_PARTS) + len(TILES) + len(EXTRA_PARTS)
        assert RenderJob("screenfront", out / "common" / "screenfront.stl") in jobs

    def test_face_jobs_carry_language_rows(self) -> None:
        # Given
        out = Path("build")
        # When
        jobs = plan_jobs(["english"], out, grid=False, extras=False)
        # Then
        assert all(job.rows is not None and len(job.rows) == 16 for job in jobs)
        assert all(job.output.parent == out / "english" for job in jobs)

    def test_optional_parts_only_on_request(self) -> None:
        # Given
        out = Path("build")
        # When
        default = plan_jobs(["catalan"], out)
        with_optional = plan_jobs(["catalan"], out, optional=True)
        # Then
        assert not any(job.part in OPTIONAL_PARTS for job in default)
        assert RenderJob("pitray", out / "optional" / "pitray.stl") in with_optional
        assert RenderJob("spacer", out / "optional" / "spacer.stl") in with_optional

    def test_test_build_uses_corner_tile_only(self) -> None:
        # Given
        out = Path("build")
        # When
        jobs = plan_jobs(["spanish"], out, test=True)
        # Then: no extra parts, every job uses the 4x4 corner
        assert len(jobs) == len(FACE_PARTS) + 1
        assert all(job.tile == TEST_TILE for job in jobs)

    def test_splits_match_the_scad_model(self) -> None:
        # Given
        scad = SCAD_FILE.read_text(encoding="utf-8")
        # When
        literal = "splits = [{}];".format(", ".join(str(k) for k in TILE_SPLITS))
        # Then
        assert literal in scad

    def test_tiles_cover_the_whole_grid_once(self) -> None:
        # Given
        covered: list[tuple[int, int]] = []
        # When
        for c0, c1, r0, r1 in TILES.values():
            covered += [(r, c) for r in range(r0, r1) for c in range(c0, c1)]
        # Then
        assert sorted(covered) == [(r, c) for r in range(16) for c in range(16)]


class TestWritePreview:
    def test_writes_assembly_and_pieces_files(self, tmp_path: Path) -> None:
        # Given
        out = tmp_path / "preview"
        # When
        paths = write_preview("catalan", out)
        # Then
        assert paths == [out / "preview_catalan.scad", out / "pieces_catalan.scad"]
        assembly, pieces = (path.read_text(encoding="utf-8") for path in paths)
        assert f"include <{SCAD_FILE.resolve()}>" in assembly
        assert 'part = "assembly";' in assembly
        assert 'part = "pieces";' in pieces
        assert "ÉSÓN" in assembly and "ÉSÓN" in pieces


class TestStencilFont:
    def test_font_and_licence_are_bundled(self) -> None:
        # Given
        fonts = SCAD_FILE.parent / "fonts"
        # When
        font_file = fonts / "KarlaBoldStencil.ttf"
        licence = fonts / "OFL.txt"
        # Then
        assert font_file.is_file()
        assert "SIL Open Font License" in licence.read_text(encoding="utf-8")

    def test_model_loads_the_bundled_font(self) -> None:
        # Given
        scad = SCAD_FILE.read_text(encoding="utf-8")
        # When / Then
        assert "use <fonts/KarlaBoldStencil.ttf>" in scad


class TestWriteBambuProjects:
    def test_grid_project_has_one_plate_per_part(self, tmp_path: Path) -> None:
        # Given: a tiny STL for every grid tile and extra part
        stl = "\n".join(
            ["solid s", "facet normal 0 0 1", "outer loop", "vertex 0 0 0", "vertex 1 0 0"]
            + ["vertex 0 1 0", "endloop", "endfacet", "endsolid s", ""]
        )
        common = tmp_path / "stl" / "common"
        common.mkdir(parents=True)
        for name in [f"grid_{tile}" for tile in TILES] + list(EXTRA_PARTS):
            (common / f"{name}.stl").write_text(stl, encoding="ascii")
        # When
        projects = write_bambu_projects([], tmp_path / "stl", tmp_path / "bambu")
        # Then: one plate per grid tile and per extra part
        with zipfile.ZipFile(projects[0]) as zf:
            settings = zf.read("Metadata/model_settings.config").decode()
        assert settings.count("<plate>") == len(TILES) + len(EXTRA_PARTS)


class TestMatrix:
    def test_plans_both_halves_of_each_layer_and_the_single_parts(self) -> None:
        # Given
        out = Path("build/stl")
        # When
        jobs = plan_matrix_jobs(out)
        # Then
        assert len(jobs) == len(MATRIX_PARTS) * len(MATRIX_HALVES) + len(MATRIX_SINGLE_PARTS)
        assert RenderJob("button", out / "matrix" / "button.stl", scad=MATRIX_SCAD_FILE) in jobs
        assert RenderJob(MATRIX_BOX_PART, out / "matrix" / "box.stl", scad=MATRIX_SCAD_FILE) in jobs
        assert (
            RenderJob("face", out / "matrix" / "face_right.stl", half=1, scad=MATRIX_SCAD_FILE)
            in jobs
        )
        assert all(job.scad == MATRIX_SCAD_FILE for job in jobs)

    def test_command_passes_the_half_and_the_matrix_model(self) -> None:
        # Given
        job = plan_matrix_jobs(Path("build"))[0]
        # When
        cmd = scad_command(job)
        # Then
        assert 'part="tray"' in cmd
        assert "half=0" in cmd
        assert cmd[-1] == str(MATRIX_SCAD_FILE)

    def test_box_command_has_no_half(self) -> None:
        # Given
        job = next(job for job in plan_matrix_jobs(Path("build")) if job.part == MATRIX_BOX_PART)
        # When
        cmd = scad_command(job)
        # Then
        assert 'part="box"' in cmd
        assert not any(arg.startswith("half=") for arg in cmd)

    def test_model_matches_the_strip(self) -> None:
        # Given
        scad = MATRIX_SCAD_FILE.read_text(encoding="utf-8")
        # When / Then: 10 x 6 cells, one LED of a 30 LEDs/metre strip each
        assert "cols = 10;" in scad
        assert "rows = 6;" in scad
        assert "pitch = 1000 / 30;" in scad

    def test_writes_one_project_per_part(self, tmp_path: Path) -> None:
        # Given: a tiny STL for every half, the box and the button
        stl = "\n".join(
            ["solid s", "facet normal 0 0 1", "outer loop", "vertex 0 0 0", "vertex 1 0 0"]
            + ["vertex 0 1 0", "endloop", "endfacet", "endsolid s", ""]
        )
        matrix = tmp_path / "stl" / "matrix"
        matrix.mkdir(parents=True)
        for job in plan_matrix_jobs(tmp_path / "stl"):
            job.output.write_text(stl, encoding="ascii")
        # When
        projects = write_matrix_projects(tmp_path / "stl", tmp_path / "bambu")
        # Then
        assert projects == [
            tmp_path / "bambu" / "matrix_tray.3mf",
            tmp_path / "bambu" / "matrix_grid.3mf",
            tmp_path / "bambu" / "matrix_face.3mf",
            tmp_path / "bambu" / "matrix_box.3mf",
        ]
        with zipfile.ZipFile(projects[0]) as zf:
            settings = zf.read("Metadata/model_settings.config").decode()
        assert settings.count("<plate>") == 2

    def test_box_project_holds_the_box_and_the_button(self, tmp_path: Path) -> None:
        # Given
        stl = "\n".join(
            ["solid s", "facet normal 0 0 1", "outer loop", "vertex 0 0 0", "vertex 1 0 0"]
            + ["vertex 0 1 0", "endloop", "endfacet", "endsolid s", ""]
        )
        (tmp_path / "stl" / "matrix").mkdir(parents=True)
        for job in plan_matrix_jobs(tmp_path / "stl"):
            job.output.write_text(stl, encoding="ascii")
        # When
        projects = write_matrix_projects(tmp_path / "stl", tmp_path / "bambu")
        # Then: one plate each
        with zipfile.ZipFile(projects[-1]) as zf:
            settings = zf.read("Metadata/model_settings.config").decode()
        assert settings.count("<plate>") == len(MATRIX_SINGLE_PARTS)


def tiny_stl(size: float = 1.0) -> str:
    return "\n".join(
        ["solid s", "facet normal 0 0 1", "outer loop", "vertex 0 0 0", f"vertex {size} 0 0"]
        + [f"vertex 0 {size} 0", "endloop", "endfacet", "endsolid s", ""]
    )


class TestBox:
    def test_plans_every_piece(self) -> None:
        # Given
        out = Path("build/stl")
        # When
        jobs = plan_box_jobs(out)
        # Then: four tiles of shell and face, two halves of grid and cover, one leg
        assert len(jobs) == sum(len(names) for names in BOX_PIECES.values()) == 13
        assert (
            RenderJob("shell", out / "box" / "shell_top_left.stl", scad=BOX_SCAD_FILE, piece=2)
            in jobs
        )
        assert (
            RenderJob("cover", out / "box" / "cover_right.stl", scad=BOX_SCAD_FILE, piece=1) in jobs
        )
        assert RenderJob("leg", out / "box" / "leg.stl", scad=BOX_SCAD_FILE) in jobs

    def test_command_passes_the_piece(self) -> None:
        # Given
        job = next(
            job for job in plan_box_jobs(Path("build")) if job.part == "face" and job.piece == 3
        )
        # When
        cmd = scad_command(job)
        # Then
        assert 'part="face"' in cmd
        assert "piece=3" in cmd
        assert cmd[-1] == str(BOX_SCAD_FILE)

    def test_leg_has_no_piece(self) -> None:
        # Given
        job = next(job for job in plan_box_jobs(Path("build")) if job.part == "leg")
        # When / Then
        assert not any(arg.startswith("piece=") for arg in scad_command(job))

    def test_model_parts_match_the_plan(self) -> None:
        # Given
        scad = BOX_SCAD_FILE.read_text(encoding="utf-8")
        # When / Then: every planned part is drawn by the model
        for part in BOX_PIECES:
            assert f'part == "{part}"' in scad

    def test_writes_one_project_per_part(self, tmp_path: Path) -> None:
        # Given
        for job in plan_box_jobs(tmp_path / "stl"):
            job.output.parent.mkdir(parents=True, exist_ok=True)
            job.output.write_text(tiny_stl(), encoding="ascii")
        # When
        projects = write_box_projects(tmp_path / "stl", tmp_path / "bambu")
        # Then
        names = [path.name for path in projects]
        assert names == [
            "box_shell.3mf",
            "box_face.3mf",
            "box_grid.3mf",
            "box_cover.3mf",
            "box_legs.3mf",
        ]
        with zipfile.ZipFile(projects[-1]) as zf:
            legs = zf.read("Metadata/model_settings.config").decode()
        assert legs.count("<plate>") == 2
        with zipfile.ZipFile(projects[1]) as zf:
            face = zf.read("Metadata/model_settings.config").decode()
        assert face.count("<plate>") == 4
        assert 'value="100%"' in face


class TestOversizedParts:
    def test_flags_parts_bigger_than_the_bed(self, tmp_path: Path) -> None:
        # Given
        small = tmp_path / "small.stl"
        big = tmp_path / "big.stl"
        small.write_text(tiny_stl(200), encoding="ascii")
        big.write_text(tiny_stl(252), encoding="ascii")
        # When
        too_big = oversized_parts([small, big])
        # Then: 252 mm leaves less than 3 mm on each side of the 256 mm bed
        assert list(too_big) == [big]
        assert too_big[big] == (252.0, 252.0)


class TestBoxFitTest:
    def test_one_plate_job(self) -> None:
        # Given / When
        jobs = plan_box_test_jobs(Path("build/stl"))
        # Then
        assert jobs == [
            RenderJob("test_plate", Path("build/stl/box/test_plate.stl"), scad=BOX_SCAD_FILE)
        ]

    def test_model_lists_every_test_piece(self) -> None:
        # Given
        scad = BOX_SCAD_FILE.read_text(encoding="utf-8")
        start = scad.index("function test_pieces()")
        block = scad[start : scad.index("];", start)]
        # When
        pieces = block.count('["')
        # Then
        assert pieces == BOX_TEST_PIECES

    def test_project_has_one_plate(self, tmp_path: Path) -> None:
        # Given
        stl = tmp_path / "stl" / "box" / "test_plate.stl"
        stl.parent.mkdir(parents=True)
        stl.write_text(tiny_stl(), encoding="ascii")
        # When
        projects = write_box_projects(tmp_path / "stl", tmp_path / "bambu")
        # Then
        assert projects == [tmp_path / "bambu" / "box_test.3mf"]
