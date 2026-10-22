from __future__ import annotations

import shutil
from logging import INFO, basicConfig
from pathlib import Path
from typing import Annotated

import typer

from wordclock.cad.build import plan_jobs, render_all
from wordclock.layouts.utils.layout import Layout

app = typer.Typer()


@app.command()
def main(
    lang: Annotated[
        list[str] | None, typer.Option(help="Language to render (repeatable, default: all)")
    ] = None,
    out: Annotated[Path, typer.Option(help="Output directory")] = Path("build/stl"),
    grid: Annotated[bool, typer.Option(help="Render the light grid tiles")] = True,
    pi: Annotated[bool, typer.Option(help="Render the Raspberry Pi box")] = True,
    test: Annotated[bool, typer.Option(help="Render only the 4x4 test corner")] = False,
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
    if shutil.which(openscad) is None:
        typer.echo(f"OpenSCAD not found: {openscad!r}", err=True)
        raise typer.Exit(1)

    jobs = plan_jobs(languages, out, grid=grid, pi=pi, test=test)
    typer.echo(f"Rendering {len(jobs)} STL files into {out}/ ...")
    try:
        render_all(jobs, openscad=openscad, workers=workers)
    except RuntimeError as exc:
        typer.echo(str(exc), err=True)
        raise typer.Exit(1) from exc
    typer.echo("Done.")
