from __future__ import annotations

import zipfile
from pathlib import Path

from wordclock.cad import (
    EXTRA_PARTS,
    FACE_PARTS,
    OPTIONAL_PARTS,
    SCAD_FILE,
    TEST_TILE,
    TILE_SPLITS,
    TILES,
    RenderJob,
    plan_jobs,
    scad_command,
    scad_string_list,
    write_bambu_projects,
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
    def test_grid_project_prints_the_spacer_four_times(self, tmp_path: Path) -> None:
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
        # Then: one plate per grid tile, four spacers, the other extra parts
        with zipfile.ZipFile(projects[0]) as zf:
            settings = zf.read("Metadata/model_settings.config").decode()
        assert settings.count("<plate>") == len(TILES) + 4 + len(EXTRA_PARTS) - 1
        assert settings.count('key="plater_name" value="spacer"') == 4
