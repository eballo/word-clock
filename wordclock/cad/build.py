from __future__ import annotations

import subprocess
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from logging import getLogger
from pathlib import Path

from wordclock.layouts.utils.layout import load_grid

logger = getLogger(__name__)

SCAD_FILE: Path = Path(__file__).parent / "wordclock.scad"

# Cell ranges (col_start, col_end, row_start, row_end), end exclusive.
# A 2x2 split keeps every tile under 256 mm, the Bambu Lab A1 bed size.
TILES: dict[str, tuple[int, int, int, int]] = {
    "r0c0": (0, 8, 0, 8),
    "r0c1": (8, 16, 0, 8),
    "r1c0": (0, 8, 8, 16),
    "r1c1": (8, 16, 8, 16),
}

# Top-left 4x4 corner, used to test fit, letters and light bleed.
TEST_TILE: tuple[int, int, int, int] = (0, 4, 0, 4)

FACE_PARTS: tuple[str, ...] = ("face", "letters", "diffuser")
GRID_PART = "grid"
PI_PARTS: tuple[str, ...] = ("pibox", "pilid")


@dataclass(frozen=True)
class RenderJob:
    """One STL file to render from the SCAD model."""

    part: str
    output: Path
    tile: tuple[int, int, int, int] | None = None
    rows: tuple[str, ...] | None = None


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
    cmd.append(str(SCAD_FILE))
    return cmd


def plan_jobs(
    languages: list[str],
    out_dir: Path,
    grid: bool = True,
    pi: bool = True,
    test: bool = False,
) -> list[RenderJob]:
    """
    List every STL needed for the given languages.

    Face parts depend on the language; grid and Raspberry Pi parts do not.

    Args:
        languages: Layout names, e.g. ``["catalan"]``.
        out_dir: Directory for the STL files.
        grid: Include the light grid tiles.
        pi: Include the Raspberry Pi box and lid.
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
    if pi and not test:
        for part in PI_PARTS:
            jobs.append(RenderJob(part, out_dir / "common" / f"{part}.stl"))
    return jobs


def write_preview(lang: str, out_dir: Path) -> Path:
    """
    Write a SCAD file that shows the assembled clock for one language.

    The file includes the model and overrides ``part`` and ``rows``, so it
    opens directly in the OpenSCAD GUI with the Customizer available.

    Args:
        lang: Layout name, e.g. ``"catalan"``.
        out_dir: Directory for the preview file.

    Returns:
        Path of the written SCAD file.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"preview_{lang}.scad"
    rows = scad_string_list(load_grid(lang))
    path.write_text(
        f'include <{SCAD_FILE.resolve()}>\n\npart = "assembly";\nrows = {rows};\n',
        encoding="utf-8",
    )
    logger.info("Wrote %s", path)
    return path


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
