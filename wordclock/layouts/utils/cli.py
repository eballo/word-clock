"""CLI entry point for the wordclock-generate command."""

from __future__ import annotations

from argparse import ArgumentParser

from wordclock.layouts.utils.layout import Layout, generate_static


def main() -> None:
    parser = ArgumentParser(description="Generate and persist a static word-clock layout.")
    parser.add_argument(
        "--lang",
        choices=Layout.available(),
        help="Language to generate. Prompted interactively if omitted.",
    )
    parser.add_argument("--seed", type=int, default=None, help="Random seed (optional).")
    args = parser.parse_args()

    available = Layout.available()

    if args.lang:
        lang = args.lang
    else:
        print("Available languages:")
        for i, name in enumerate(available, start=1):
            print(f"  {i}. {name}")
        choice = input("Select language (name or number): ").strip()
        if choice.isdigit():
            idx = int(choice) - 1
            if not (0 <= idx < len(available)):
                print(f"Invalid selection: {choice}")
                raise SystemExit(1)
            lang = available[idx]
        elif choice in available:
            lang = choice
        else:
            print(f"Unknown language: {choice!r}")
            raise SystemExit(1)

    static = generate_static(lang, seed=args.seed)
    print(f"Generated static layout for '{lang}':")
    for row in static:
        print(f"  {row}")
