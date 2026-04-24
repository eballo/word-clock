# Word Clock

A 65 × 65 cm word clock with a 16 × 16 LED matrix (256 LEDs) driven by a Raspberry Pi.
The front panel is 3D-printed and interchangeable, allowing the clock to display time
in different languages without any hardware changes.

## Repository structure

```
word-clock/
├── prototype/    # Browser-based JavaScript simulator to validate the grid layout
├── wordclock/    # Python package — LED control, time logic, Flask API and web UI
├── tests/        # Unit and integration tests
├── docs/         # Step-by-step build documentation
└── README.md
```

## Documentation

The `docs/` folder walks through the full build process:

- `01-introduction.md` — project overview and how it works
- `02-hardware.md` — components, wiring and 3D-printed panel
- `03-software.md` — setting up the Raspberry Pi and running the code
- `04-assembly.md` — putting it all together

## TODO

- Multilanguage support (Catalan, Spanish, English, Dutch)

## Reference/Useful links
- [rpi_wordclock](https://github.com/bk1285/rpi_wordclock) — inspiration for the software and API design
- [Free fonts for 3D printing](https://en.solidmakarna.se/supportblogg/20-gratis-typsnitt-for-laserskarning)

## Acknowledgements

- [petercmonaco — WordClockSimulator](https://github.com/petercmonaco/WordClockSimulator)