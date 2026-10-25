from __future__ import annotations

import subprocess
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from logging import getLogger
from pathlib import Path

from wordclock.cad.bambu import count_bodies, read_stl, write_project
from wordclock.layouts.utils.layout import load_grid

logger = getLogger(__name__)

SCAD_FILE: Path = Path(__file__).parent / "wordclock.scad"
MATRIX_SCAD_FILE: Path = Path(__file__).parent / "matrix.scad"

# Grid lines where the panel is split, matching `splits` in the SCAD model.
# A 3x3 split keeps every tile under 17.5 cm, well inside the 25 cm bed of
# the Bambu Lab A1.
TILE_SPLITS: tuple[int, ...] = (0, 5, 11, 16)

# Cell ranges (col_start, col_end, row_start, row_end), end exclusive.
TILES: dict[str, tuple[int, int, int, int]] = {
    f"r{i}c{j}": (TILE_SPLITS[j], TILE_SPLITS[j + 1], TILE_SPLITS[i], TILE_SPLITS[i + 1])
    for i in range(len(TILE_SPLITS) - 1)
    for j in range(len(TILE_SPLITS) - 1)
}

# Top-left 4x4 corner, used to test fit, letters and light bleed.
TEST_TILE: tuple[int, int, int, int] = (0, 4, 0, 4)

FACE_PARTS: tuple[str, ...] = ("face",)
GRID_PART = "grid"
# Single parts that do not depend on the language: the screen module under
# the clock (Touch Display v1, Raspberry Pi and camera) with its hanger.
EXTRA_PARTS: tuple[str, ...] = ("screenfront", "screenback", "screenhanger")

# Parts rendered only on request: the spacer ring and the black recess ring
# that can hold the panel in the frame (four identical pieces each), and a
# Raspberry Pi Zero 2 W tray for a clock without the screen module.
OPTIONAL_PARTS: tuple[str, ...] = ("spacer", "recess", "pitray")

# Mini 10x6 matrix for the 30 LEDs/metre strip: the tray, the grid and the
# face in two halves, one stand box for the Raspberry Pi and the wiring, and
# the button cap.
MATRIX_PARTS: tuple[str, ...] = ("tray", "grid", "face")
MATRIX_HALVES: dict[str, int] = {"left": 0, "right": 1}
MATRIX_BOX_PART = "box"
MATRIX_SINGLE_PARTS: tuple[str, ...] = (MATRIX_BOX_PART, "button")


@dataclass(frozen=True)
class RenderJob:
    """One STL file to render from the SCAD model."""

    part: str
    output: Path
    tile: tuple[int, int, int, int] | None = None
    rows: tuple[str, ...] | None = None
    half: int | None = None
    scad: Path = SCAD_FILE


def scad_string_list(values: list[str] | tuple[str, ...]) -> str:
    """
    Format strings as an OpenSCAD list literal.

    Args:
        values: Strings to embed, e.g. grid rows.

    Returns:
        A literal such as ``["AB", "C\\"D"]``.
    """
    escaped = (v.replace("\\", "\\\\").replace('"', '\\"') for v in values)
    return "[" + ", ".join(f'"{v}"' for v in escaped) + "]"


def scad_command(job: RenderJob, openscad: str = "openscad") -> list[str]:
    """
    Build the OpenSCAD command line for a render job.

    Args:
        job: The part, tile and letters to render.
        openscad: Path or name of the OpenSCAD binary.

    Returns:
        Command arguments ready for :func:`subprocess.run`.
    """
    cmd = [openscad, "--backend=manifold", "-o", str(job.output), "-D", f'part="{job.part}"']
    if job.tile is not None:
        cmd += ["-D", "tile=[{}]".format(", ".join(str(v) for v in job.tile))]
    if job.rows is not None:
        cmd += ["-D", f"rows={scad_string_list(job.rows)}"]
    if job.half is not None:
        cmd += ["-D", f"half={job.half}"]
    cmd.append(str(job.scad))
    return cmd


def plan_jobs(
    languages: list[str],
    out_dir: Path,
    grid: bool = True,
    extras: bool = True,
    optional: bool = False,
    test: bool = False,
) -> list[RenderJob]:
    """
    List every STL needed for the given languages.

    Face parts depend on the language; grid tiles and extra parts do not.

    Args:
        languages: Layout names, e.g. ``["catalan"]``.
        out_dir: Directory for the STL files.
        grid: Include the light grid tiles.
        extras: Include the screen module parts.
        optional: Include the optional parts, such as the Pi Zero tray.
        test: Render only the 4x4 test corner instead of the full tiles.

    Returns:
        Render jobs, one per STL file.
    """
    tiles = {"test": TEST_TILE} if test else TILES
    jobs: list[RenderJob] = []
    for lang in languages:
        rows = tuple(load_grid(lang))
        for name, tile in tiles.items():
            for part in FACE_PARTS:
                output = out_dir / lang / f"{part}_{name}.stl"
                jobs.append(RenderJob(part, output, tile, rows))
    if grid:
        for name, tile in tiles.items():
            jobs.append(RenderJob(GRID_PART, out_dir / "common" / f"grid_{name}.stl", tile))
    if optional and not test:
        for part in OPTIONAL_PARTS:
            jobs.append(RenderJob(part, out_dir / "optional" / f"{part}.stl"))
    if extras and not test:
        for part in EXTRA_PARTS:
            jobs.append(RenderJob(part, out_dir / "common" / f"{part}.stl"))
    return jobs


def plan_matrix_jobs(out_dir: Path) -> list[RenderJob]:
    """
    List every STL of the mini matrix.

    Args:
        out_dir: Directory for the STL files; they go into ``matrix/``.

    Returns:
        Render jobs for the left and right halves of the tray, the grid and
        the face, and for the stand box and the button cap.
    """
    jobs = [
        RenderJob(part, out_dir / "matrix" / f"{part}_{name}.stl", half=half, scad=MATRIX_SCAD_FILE)
        for part in MATRIX_PARTS
        for name, half in MATRIX_HALVES.items()
    ]
    return jobs + [
        RenderJob(part, out_dir / "matrix" / f"{part}.stl", scad=MATRIX_SCAD_FILE)
        for part in MATRIX_SINGLE_PARTS
    ]


# Per-object print settings in the Bambu Studio projects.
FACE_SETTINGS: dict[str, str] = {"sparse_infill_density": "100%"}
GRID_SETTINGS: dict[str, str] = {"wall_loops": "3", "sparse_infill_density": "15%"}


def write_bambu_projects(languages: list[str], stl_dir: Path, out_dir: Path) -> list[Path]:
    """
    Group rendered STL files into Bambu Studio projects, one part per plate.

    Writes ``face_<lang>.3mf`` for every language and ``grid.3mf`` with the
    grid tiles and the extra parts. The 4x4 test corner, when rendered, goes
    into ``test_<lang>.3mf`` together with its grid tile.

    Args:
        languages: Layout names, e.g. ``["catalan"]``.
        stl_dir: Directory with the rendered STL files.
        out_dir: Directory for the projects.

    Returns:
        Paths of the written projects.
    """
    projects = []
    grid_test = stl_dir / "common" / "grid_test.stl"
    for lang in languages:
        faces = [stl_dir / lang / f"face_{name}.stl" for name in TILES]
        if all(path.exists() for path in faces):
            projects.append(write_project(faces, out_dir / f"face_{lang}.3mf", FACE_SETTINGS))
        face_test = stl_dir / lang / "face_test.stl"
        if face_test.exists() and grid_test.exists():
            projects.append(write_project([face_test, grid_test], out_dir / f"test_{lang}.3mf"))
    grids = [stl_dir / "common" / f"grid_{name}.stl" for name in TILES]
    extras = [stl_dir / "common" / f"{part}.stl" for part in EXTRA_PARTS]
    if all(path.exists() for path in grids):
        parts = grids + [path for path in extras if path.exists()]
        projects.append(write_project(parts, out_dir / "grid.3mf", GRID_SETTINGS))
    return projects


def write_matrix_projects(stl_dir: Path, out_dir: Path) -> list[Path]:
    """
    Group the mini matrix STL files into Bambu Studio projects.

    Writes ``matrix_tray.3mf``, ``matrix_grid.3mf`` and ``matrix_face.3mf``,
    one half per plate, and ``matrix_box.3mf`` with the stand box and the
    button cap, so each project carries the print settings of its part.

    Args:
        stl_dir: Directory with the rendered STL files.
        out_dir: Directory for the projects.

    Returns:
        Paths of the written projects.
    """
    settings = {"tray": GRID_SETTINGS, "grid": GRID_SETTINGS, "face": FACE_SETTINGS}
    projects = []
    for part in MATRIX_PARTS:
        halves = [stl_dir / "matrix" / f"{part}_{name}.stl" for name in MATRIX_HALVES]
        if all(path.exists() for path in halves):
            output = out_dir / f"matrix_{part}.3mf"
            projects.append(write_project(halves, output, settings[part]))
    singles = [stl_dir / "matrix" / f"{part}.stl" for part in MATRIX_SINGLE_PARTS]
    if all(path.exists() for path in singles):
        projects.append(write_project(singles, out_dir / "matrix_box.3mf", GRID_SETTINGS))
    return projects


# Preview views: file prefix and the SCAD part that draws it.
PREVIEW_VIEWS: dict[str, str] = {
    "preview": "assembly",
    "pieces": "pieces",
}


def write_preview(lang: str, out_dir: Path) -> list[Path]:
    """
    Write SCAD files that show the clock for one language in the OpenSCAD GUI.

    ``preview_<lang>.scad`` shows the assembled clock and
    ``pieces_<lang>.scad`` shows every printed tile pulled apart and
    labelled. Each file includes the model and overrides ``part`` and
    ``rows``, so the Customizer stays available.

    Args:
        lang: Layout name, e.g. ``"catalan"``.
        out_dir: Directory for the preview files.

    Returns:
        Paths of the written SCAD files.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = scad_string_list(load_grid(lang))
    paths = []
    for prefix, part in PREVIEW_VIEWS.items():
        path = out_dir / f"{prefix}_{lang}.scad"
        path.write_text(
            f'include <{SCAD_FILE.resolve()}>\n\npart = "{part}";\nrows = {rows};\n',
            encoding="utf-8",
        )
        logger.info("Wrote %s", path)
        paths.append(path)
    return paths


def render(job: RenderJob, openscad: str = "openscad") -> Path:
    """
    Render one job to STL.

    Args:
        job: The job to render.
        openscad: Path or name of the OpenSCAD binary.

    Returns:
        Path of the written STL file.

    Raises:
        RuntimeError: If OpenSCAD exits with an error.
    """
    job.output.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(scad_command(job, openscad), capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"OpenSCAD failed for {job.output}:\n{result.stderr}")
    logger.info("Rendered %s", job.output)
    return job.output


def find_loose_parts(paths: list[Path]) -> dict[Path, int]:
    """
    Find STL files that contain more than one solid body.

    Args:
        paths: Rendered STL files.

    Returns:
        Each file with loose parts and its number of bodies.
    """
    counts = {path: count_bodies(read_stl(path)) for path in paths}
    return {path: n for path, n in counts.items() if n != 1}


def render_all(jobs: list[RenderJob], openscad: str = "openscad", workers: int = 4) -> list[Path]:
    """
    Render jobs in parallel.

    Args:
        jobs: Jobs from :func:`plan_jobs`.
        openscad: Path or name of the OpenSCAD binary.
        workers: Number of OpenSCAD processes to run at once.

    Returns:
        Paths of the written STL files, in job order.
    """
    with ThreadPoolExecutor(max_workers=workers) as pool:
        return list(pool.map(lambda job: render(job, openscad), jobs))
