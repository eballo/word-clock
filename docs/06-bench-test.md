# 06 — Bench Test

## Overview

Before ordering the whole strip, light a short piece of it on the bench:
a Raspberry Pi 3B, the Freenove breadboard and one metre of the 144
LEDs/metre strip under the printed 4 × 4 test corner. The test checks the
wiring, the colour order, how many LEDs per cell look best, whether the
strip's LEDs line up with the cells, and how much work the soldering is.
Everything bought for it, except the test strip, is reused in the final
clock.

---

## 1. Parts

### 1.1 Already at hand

| Part | Use |
|------|-----|
| Raspberry Pi 3B, microSD card and its power supply | Drives the strip |
| Freenove RFID Starter Kit FNK0025 | Breadboard, GPIO T-extension board, 40-pin ribbon cable, jumper wires, 220 Ω resistor, rectifier diode |
| Printed test corner (`build/bambu/test_catalan.3mf`) | Black face tile and white grid tile, 4 × 4 cells |
| Soldering iron and solder | Joins the strip pieces |

### 1.2 To buy

| Part | Amazon.es | Price (Oct 2026) |
|------|-----------|------------------|
| CUQI WS2812B strip, 144 LEDs/metre, 1 m, black PCB | [B0BTV9TD36](https://www.amazon.es/dp/B0BTV9TD36) | 11,99 € |
| 5V 10 A power supply (final supply) | [B083QNN7Z7](https://www.amazon.es/dp/B083QNN7Z7) | 24,99 € |
| DC jack (female) to screw terminal adapter, same size as the supply plug | electronics shop | ~3 € |
| 1000 µF 16 V electrolytic capacitors, 5 units | [B0DQ9M2BR8](https://www.amazon.es/dp/B0DQ9M2BR8) | 4,94 € |
| JST SM 3-pin connectors with 15 cm 22 AWG leads, 20 pairs | [B0CBWZK4VF](https://www.amazon.es/dp/B0CBWZK4VF) | 9,59 € |
| Tracing paper, one A4 sheet (or baking paper to compare) | stationery shop | 1–3 € |

The Freenove kit has 10 µF and 0,1 µF capacitors only: too small to
protect the strip, so buy the 1000 µF ones.

---

## 2. Wiring

The Pi powers itself from its own supply; the 5V supply powers only the
strip. The two share GND and nothing else.

```
 Raspberry Pi 3B ══ 40-pin cable ══ GPIO T-extension board on the breadboard
                                      │ GPIO18 (pin 12) ──[220 Ω]──────────► strip DIN (green)
                                      │ GND ─────────────┐
                                                         │
 5V supply ── screw adapter ──► rail + ──────────────────┼────────────────► strip 5V (red)
                                rail − ──────────────────┴────────────────► strip GND (white/black)
                                     └──[1000 µF]──┘  (between + and −, stripe to −)
```

| From | To | Note |
|------|----|------|
| Pi GPIO 18 (pin 12) | 220 Ω resistor → strip DIN | Data line |
| Pi GND | Breadboard rail − | Common ground |
| Supply + | Breadboard rail + → strip 5V | Strip power only |
| Supply − | Breadboard rail − → strip GND | |
| 1000 µF capacitor | Between rail + and rail −, close to the strip | Stripe (negative) to rail − |

> ⚠️ Use one breadboard power rail for the strip only. The T-extension board
> brings the Pi's 5V and 3,3V to breadboard rows: never connect the 5V
> supply to them. Do not use the kit's breadboard power module either.

> **Note:** A breadboard carries 1–2 A at most. That is enough for 64 LEDs
> at low brightness. The final clock wires the strip straight to the supply
> and solders the 74AHCT125 on a perfboard.

The JST leads are stranded wire and do not hold in breadboard holes: tin
their ends, or bridge them with male-to-male jumper wires from the kit.

If the strip shows random colours or flickers, the 3,3V data from the Pi is
too weak for it. Power the first strip piece through the kit's rectifier
diode (stripe towards the strip): the LEDs then run at about 4,3V and read
the Pi's data reliably. The final clock uses a 74AHCT125 instead.

---

## 3. Safety check and power-up order

Before plugging the 5V supply in:

- [ ] Strip polarity: supply + to strip 5V, supply − to strip GND
- [ ] Strip direction: wired at the DIN end (the printed arrows point away from it)
- [ ] Pi GND joined to the supply GND
- [ ] Data: GPIO 18 → 220 Ω → DIN
- [ ] The 5V supply touches no pin of the Pi
- [ ] `BRIGHTNESS = 20` in the test program

Power up:

1. Start the Pi with its own supply.
2. Plug the 5V supply into the wall.
3. Run the test program.

Power down in reverse: stop the program, unplug the 5V supply, shut the
Pi down. Never connect or disconnect the strip while the supply is on.

---

## 4. Raspberry Pi setup

Install Raspberry Pi OS Lite (64-bit) with Raspberry Pi Imager, with the
hostname `wordclock`, the Wi-Fi network and SSH enabled. Then, over SSH:

```bash
# GPIO 18 shares the PWM with the analogue audio: turn the audio off
sudo sed -i 's/^dtparam=audio=on/dtparam=audio=off/' /boot/firmware/config.txt
sudo reboot

# After the reboot
sudo apt update && sudo apt install -y python3-venv python3-dev build-essential
python3 -m venv ~/ledtest
~/ledtest/bin/pip install rpi_ws281x
```

---

## 5. Test program

Save it as `~/test_leds.py`. Set `LED_COUNT` to the LEDs connected: 64 for
the test corner, 60 for the 2 m Tremex strip.

```python
"""Light a WS2812B strip LED by LED, then in red, green and blue."""

import time

from rpi_ws281x import Color, PixelStrip

LED_COUNT = 64
LED_PIN = 18
BRIGHTNESS = 20  # 0-255: keep it low on the bench

strip = PixelStrip(LED_COUNT, LED_PIN, 800_000, 10, False, BRIGHTNESS)
strip.begin()


def fill(color: int, count: int = LED_COUNT) -> None:
    for i in range(LED_COUNT):
        strip.setPixelColor(i, color if i < count else Color(0, 0, 0))
    strip.show()


try:
    # One LED at a time: shows where the chain stops if a joint is bad
    for i in range(LED_COUNT):
        fill(Color(0, 0, 0))
        strip.setPixelColor(i, Color(255, 255, 255))
        strip.show()
        time.sleep(0.05)
    # Red, green, blue on the first 16 LEDs: checks the colour order
    for color in (Color(255, 0, 0), Color(0, 255, 0), Color(0, 0, 255)):
        fill(color, 16)
        time.sleep(1)
finally:
    fill(Color(0, 0, 0))
```

```bash
sudo ~/ledtest/bin/python ~/test_leds.py
```

`sudo` is needed because the library drives the PWM hardware directly.
Phase 1 of the software turns this into the `wordclock test-strip`
command.

---

## 6. Strip under the test corner

The test corner is 4 cells wide, and every cell sits over 4 LEDs.

```
row 0  [16 LEDs] →──┐
row 1  [16 LEDs] ←──┘──┐      snake: DOUT of one row → DIN of the next
row 2  [16 LEDs] →─────┘──┐
row 3  [16 LEDs] ←────────┘   64 LEDs in total
```

1. Measure the strip width. The grid notches are 14 mm wide, for strips up
   to 12 mm; the test corner printed before that change has 12 mm notches.
2. Cut four pieces of 16 LEDs, on the copper cut marks.
3. Solder a JST SM lead to each end, so the rows plug together in a snake.
4. Stick each piece along the centre of its row of cells, through the wall
   notches, so every cell has four LEDs and no LED sits under a wall.
5. Lay the tracing paper on the grid and the face on top.

---

## 7. What to look at

| Check | What to note |
|-------|--------------|
| LED pitch | Every cell over 4 LEDs, none under a wall |
| LEDs per letter | Light 1, 2 and 4 LEDs per cell and compare evenness and brightness |
| Black PCB | Whether the CUQI strip's black board makes the cells too dark |
| Light bleed | Whether light reaches the neighbouring letters |
| Diffuser | Tracing paper against baking paper |
| Colour order | Red, green and blue come out in that order |
| Soldering | How long the four rows took |

If something fails:

| Symptom | Likely cause |
|---------|--------------|
| Nothing lights | Strip wired at the DOUT end, GND not common, supply off |
| Random colours or flicker | 3,3V data too weak: use the diode trick (section 2) |
| Chain stops at one LED | Bad joint or a cut through a pad just before that LED |
| Red shows as green | Different colour order: change the strip type in the program |

---

## 8. Bench test checklist

- [ ] Raspberry Pi OS installed, audio off, `rpi_ws281x` installed
- [ ] Strip wired on the breadboard, safety check done
- [ ] `test_leds.py` runs: every LED lights in turn, colours in order
- [ ] Four strip rows soldered and stuck under the test corner
- [ ] 1, 2 and 4 LEDs per letter compared under the paper and the face
- [ ] Decision taken: CUQI 144 LEDs/metre strip or hand-soldered pixels
