# 03 — Software

## Overview

The software runs on a Raspberry Pi 3B (a 4B works the same way). It
consists of:

- **Raspberry Pi OS Lite (64-bit)** — no desktop; the 7" screen gets a
  minimal kiosk on top later (section 9)
- **Python 3.13** — installed and managed by `uv`
- **wordclock** — the Python package: time logic, LED control, and a
  FastAPI server with the web simulator
- **systemd** — starts the clock on boot

---

## 1. Flash the SD card

Use a new 16–32 GB microSD card if the old one has seen a lot of use:
worn cards are the most common cause of hangs.

Install **Raspberry Pi Imager** from
[raspberrypi.com/software](https://www.raspberrypi.com/software/) and
choose:

| Setting | Value |
|---------|-------|
| Device | Raspberry Pi 3 (or 4) |
| Operating system | Raspberry Pi OS Lite (64-bit) |
| Hostname | `wordclock` |
| Username and password | `pi` (or your choice) and a password |
| Wi-Fi | your network, country `ES` |
| Time zone | `Europe/Madrid` |
| SSH | enabled, public-key authentication only (see section 2 for a dedicated key) |

Write the card, put it in the Pi and power it on with its own supply
(micro-USB, 5V 2,5 A for the Pi 3B).

---

## 2. First connection and update

After a minute or two, from your computer:

```bash
ssh pi@wordclock.local
```

> If `wordclock.local` does not resolve, find the Pi's IP address on your
> router and use `ssh pi@<ip>`.

The examples use the user `pi`: replace it with the user you chose in the
Imager. A dedicated key and a host entry in `~/.ssh/config` shorten the
command to `ssh wordclock`:

```bash
ssh-keygen -t ed25519 -f ~/.ssh/wordclock -C "wordclock-pi"
```

```
Host wordclock
    HostName wordclock.local
    User pi
    IdentityFile ~/.ssh/wordclock
    IdentitiesOnly yes
```

Paste `~/.ssh/wordclock.pub` into the Imager's SSH settings (public-key
authentication only) before writing the card.

Update the system and install the build tools for the LED library:

```bash
sudo apt update && sudo apt full-upgrade -y
sudo apt install -y git build-essential python3-dev
sudo reboot
```

---

## 3. Install the project

```bash
# uv installs Python 3.13 and the dependencies
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env

git clone https://github.com/eballo/word-clock.git
cd word-clock

# All dependencies, including the Raspberry Pi LED library
uv sync --extra rpi --extra dev
```

The first run downloads Python 3.13 and builds `rpi-ws281x`; on a Pi 3B it
takes a few minutes.

---

## 4. Check the installation (no LEDs needed)

```bash
uv run pytest -q                    # the whole test suite must pass
uv run wordclock --mock --display   # clock in the console, web on port 5000
```

Open **http://wordclock.local:5000** from your computer to see the web
simulator. Stop it with `Ctrl+C`.

---

## 5. Prepare GPIO 18 for the LEDs

The LED strip uses the PWM on GPIO 18, which the analogue audio also uses.
Turn the audio off:

```bash
sudo sed -i 's/^dtparam=audio=on/dtparam=audio=off/' /boot/firmware/config.txt
sudo reboot
```

Then follow [06 — Bench Test](06-bench-test.md) to light a first strip.

---

## 6. Run with the real LEDs

The LED library drives the PWM hardware directly, so it needs root:

```bash
cd ~/word-clock
sudo .venv/bin/wordclock --lang catalan
```

`wordclock` shows its help when called without options, so always pass at
least one (`--lang`, `--mock`, …). The web interface is at
**http://wordclock.local:5000**.

---

## 7. Start the clock on boot

Create the service file:

```bash
sudo nano /etc/systemd/system/wordclock.service
```

```ini
[Unit]
Description=Word Clock
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/home/pi/word-clock
ExecStart=/home/pi/word-clock/.venv/bin/wordclock --lang catalan --host 0.0.0.0 --port 5000
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Replace `/home/pi` with your user's home directory if you did not use
`pi`. Enable and start it:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now wordclock
sudo systemctl status wordclock
```

---

## 8. Everyday commands

| Command | Description |
|---------|-------------|
| `sudo systemctl status wordclock` | Check that the service is running |
| `sudo systemctl restart wordclock` | Restart after a code change |
| `sudo journalctl -u wordclock -f` | Follow the live logs |
| `uv run pytest` | Run the test suite |
| `uv run wordclock --mock --display` | Run the clock without LEDs |

To update the code:

```bash
cd ~/word-clock
git pull
uv sync --extra rpi --extra dev
sudo systemctl restart wordclock
```

---

## 9. Planned: touch screen kiosk

The 7" Touch Display goes in the screen module under the clock (see
[05 — Enclosure](05-enclosure.md)). The plan keeps Raspberry Pi OS Lite and
adds only what a kiosk needs, which suits the 1 GB of the Pi 3B better than
the full desktop:

```
Raspberry Pi
├── wordclock service (FastAPI): LEDs, time, camera, button
│      └── web at http://localhost:5000
└── kiosk: Chromium full screen on the 7" display (labwc)
       └── opens http://localhost:5000/kiosk (touch UI)
```

The kiosk page is a web page served by the clock, so it also works from a
phone: home (time and status), photo booth (live camera preview,
countdown on the screen, the buzzer and the letters, the photo shown and
saved), and settings (brightness, colour, language).

> **Note:** The official camera library (Picamera2) is installed with
> `apt`, not with `uv`. The camera phase must make it reachable from the
> project's virtual environment.

---

## 10. Setup checklist

- [ ] Raspberry Pi OS Lite (64-bit) flashed with hostname, Wi-Fi and SSH key
- [ ] System updated, build tools installed
- [ ] `uv` installed, repository cloned, `uv sync --extra rpi --extra dev` done
- [ ] Tests pass and the web simulator opens on port 5000
- [ ] Audio off in `/boot/firmware/config.txt`
- [ ] First strip lit with [06 — Bench Test](06-bench-test.md)
- [ ] systemd service enabled
