# 01 — Introduction

## What is a Word Clock?

A word clock is a clock that displays the time using words instead of numbers. Rather than showing "10:35", it lights up letters arranged in a grid to spell out a phrase like *"IT IS TWENTY FIVE TO ELEVEN"* — or in Catalan, *"SÓN DOS QUARTS MENYS CINC D'ONZE"*.

The result is a clock that reads like a sentence, turning something functional into something conversational and visually striking.

---

## The Project

The goal is to build a **65 × 65 cm word clock** with a **16 × 16 LED matrix** (256 individually addressable LEDs) driven by a Raspberry Pi.

One of the key design decisions is that the **front panel is interchangeable**. The panel is a 3D-printed piece with the letters, sitting in front of the LED matrix. Light only escapes through the letter-shaped openings. Swapping the panel changes the language of the clock without touching any hardware underneath.

### Planned language support

- Catalan *(primary)*
- Spanish
- English
- Dutch

---

## How It Works

```
┌─────────────────────────────────────┐
│          Front panel (stencil)      │  ← 3D-printed, language-specific
│   É S Ó N   V O R A   . . .         │
│   U N   D O S   T R E S   . .       │
│   . . .                             │
└─────────────────────────────────────┘
           ↕  light passes through cut letters only
┌─────────────────────────────────────┐
│        LED matrix  16 × 16          │  ← WS2812B strip, snake-wired
│   ○ ○ ○ ● ● ● ○ ○ ● ● ● ● ○ ○ ○     │     ● = lit,  ○ = off
└─────────────────────────────────────┘
           ↕  GPIO (PWM)
┌─────────────────────────────────────┐
│          Raspberry Pi               │  ← runs the Python software
└─────────────────────────────────────┘
           ↕  Wi-Fi
┌─────────────────────────────────────┐
│       Web browser / API client      │  ← optional remote control
└─────────────────────────────────────┘
```

Every minute (or every 5 minutes, since the clock reads in 5-minute steps) the Raspberry Pi calculates which LEDs to light up for the current time, sends the signal to the strip, and goes back to sleep.

A Flask API and a web interface allow you to control the clock from any device on the same network — change the time display, adjust brightness, or switch language panels.

---

## Repository Structure

```
word-clock/
├── prototype/          # JavaScript simulator — test the grid in a browser
├── wordclock/          # Python package (layouts, LED control, API, web UI)
├── tests/              # Unit and integration tests
├── docs/               # This documentation
├── pyproject.toml      # Project definition and dependencies (managed by uv)
└── README.md
```

### The prototype

Before building any hardware, the `prototype/` folder contains a browser-based simulator written in JavaScript. It renders the full 16 × 16 grid and lights up the correct letters for any time you enter. This was used to validate the grid layout and the Catalan time logic before writing a single line of Python.

---

## Acknowledgements

- [petercmonaco — WordClockSimulator](https://github.com/petercmonaco/WordClockSimulator) — inspiration for the JavaScript prototype
- [Solid Makarna — free fonts for 3D printing](https://en.solidmakarna.se/supportblogg/20-gratis-typsnitt-for-laserskarning) — font resources for the front panel design
