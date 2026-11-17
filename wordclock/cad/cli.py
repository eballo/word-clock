from __future__ import annotations

import shutil
from logging import INFO, basicConfig
from pathlib import Path
from typing import Annotated

import typer

from wordclock.cad.build import (
    find_loose_parts,
    oversized_parts,
    plan_box_jobs,
    plan_jobs,
    plan_matrix_jobs,
    render_all,
    write_bambu_projects,
    write_box_projects,
    write_matrix_projects,
    write_preview,
)
from wordclock.layouts.utils.layout import Layout

app = typer.Typer()


@app.command()
def main(
    lang: Annotated[
        list[str] | None, typer.Option(help="Language to render (repeatable, default: all)")
    ] = None,
    out: Annotated[Path, typer.Option(help="Output directory")] = Path("build/stl"),
    grid: Annotated[bool, typer.Option(help="Render the light grid tiles")] = True,
    extras: Annotated[bool, typer.Option(help="Render the screen module")] = True,
    optional: Annotated[
        bool, typer.Option(help="Also render optional parts (frame rings, Pi Zero tray)")
    ] = False,
    test: Annotated[bool, typer.Option(help="Render only the 4x4 test corner")] = False,
    matrix: Annotated[
        bool, typer.Option(help="Render only the mini 10x6 matrix for the 30 LEDs/m strip")
    ] = False,
    box: Annotated[
        bool,
        typer.Option(help="Render only the mini matrix in one flat box, with the display inside"),
    ] = False,
    preview: Annotated[
        bool, typer.Option(help="Write assembly preview files for the OpenSCAD GUI instead")
    ] = False,
    openscad: Annotated[str, typer.Option(help="OpenSCAD binary")] = "openscad",
    workers: Annotated[int, typer.Option(help="Parallel OpenSCAD processes")] = 4,
) -> None:
    """Render the enclosure STL files for the IKEA SANNAHED frame."""
    basicConfig(level=INFO, format="%(message)s")
    available = Layout.available()
    languages = lang or available
    unknown = [name for name in languages if name not in available]
    if unknown:
        typer.echo(f"Unknown language(s): {', '.join(unknown)}", err=True)
        raise typer.Exit(1)
    if preview:
        for name in languages:
            for path in write_preview(name, out.parent / "preview"):
                typer.echo(f"Open in OpenSCAD: {path}")
        return
    if shutil.which(openscad) is None:
        typer.echo(f"OpenSCAD not found: {openscad!r}", err=True)
        raise typer.Exit(1)

    if box:
        jobs = plan_box_jobs(out)
    elif matrix:
        jobs = plan_matrix_jobs(out)
    else:
        jobs = plan_jobs(languages, out, grid=grid, extras=extras, optional=optional, test=test)
    typer.echo(f"Rendering {len(jobs)} STL files into {out}/ ...")
    try:
        paths = render_all(jobs, openscad=openscad, workers=workers)
    except RuntimeError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc
    loose = find_loose_parts(paths)
    for path, bodies in loose.items():
        typer.echo(f"Loose parts: {path} has {bodies} separate bodies", err=True)
    too_big = oversized_parts(paths)
    for path, (width, length) in too_big.items():
        typer.echo(f"Too big for the bed: {path} is {width:.0f} x {length:.0f} mm", err=True)
    if loose or too_big:
        raise typer.Exit(1)
    if box:
        projects = write_box_projects(out, out.parent / "bambu")
    elif matrix:
        projects = write_matrix_projects(out, out.parent / "bambu")
    else:
        projects = write_bambu_projects(languages, out, out.parent / "bambu")
    for project in projects:
        typer.echo(f"Bambu Studio project: {project}")
    typer.echo("Done.")
