from __future__ import annotations

from typing import Annotated

import typer

from wordclock.layouts.utils.layout import Layout, generate_static

app = typer.Typer()


@app.command()
def main(
    lang: Annotated[str | None, typer.Option(help="Language to generate")] = None,
    seed: Annotated[int | None, typer.Option(help="Random seed")] = None,
) -> None:
    available = Layout.available()

    if lang is None:
        typer.echo("Available languages:")
        for i, name in enumerate(available, start=1):
            typer.echo(f"  {i}. {name}")
        typer.echo("  0. Exit")
        choice = typer.prompt("Select language (name or number)").strip()
        if choice in ("0", "q", "exit", "quit", ""):
            typer.echo("Aborted.")
            raise typer.Exit(0)
        if choice.isdigit():
            idx = int(choice) - 1
            if not (0 <= idx < len(available)):
                typer.echo(f"Invalid selection: {choice}", err=True)
                raise typer.Exit(1)
            lang = available[idx]
        elif choice in available:
            lang = choice
        else:
            typer.echo(f"Unknown language: {choice!r}", err=True)
            raise typer.Exit(1)
    elif lang not in available:
        typer.echo(f"Unknown language: {lang!r}", err=True)
        raise typer.Exit(1)

    static = generate_static(lang, seed=seed)
    typer.echo(f"Generated static layout for '{lang}':")
    for row in static:
        typer.echo(f"  {row}")
