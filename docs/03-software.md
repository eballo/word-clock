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

### 1.1 Create an SSH key for the Pi

On your computer, create a key used only for the clock and a host entry,
so that `ssh wordclock` is enough to connect. Use the same user name you
will set in the Imager (here `pi`).

```bash
ssh-keygen -t ed25519 -f ~/.ssh/wordclock -C "wordclock-pi"
```

Add to `~/.ssh/config`:

```
Host wordclock
    HostName wordclock.local
    User pi
    IdentityFile ~/.ssh/wordclock
    IdentitiesOnly yes
    ServerAliveInterval 60
```

Copy the public key to paste it in the Imager later:

```bash
pbcopy < ~/.ssh/wordclock.pub    # macOS
```

### 1.2 Write the card with Raspberry Pi Imager

Install **Raspberry Pi Imager** from
[raspberrypi.com/software](https://www.raspberrypi.com/software/). Use a
new 16–32 GB microSD card if the old one has seen a lot of use: worn cards
are the most common cause of hangs.

1. **Device:** Raspberry Pi 3 (or 4). Pick it first: the 64-bit systems
   only appear for models that support them.
2. **Operating system:** open **Raspberry Pi OS (other)** and choose
   **Raspberry Pi OS Lite (64-bit)**. It is not in the first list.
3. **Storage:** the microSD card. Check the size so you do not pick another
   disk. There is no need to erase the card first: the Imager overwrites
   everything on it, partitions included.
4. **Customise the system** when the Imager asks (answer yes):

| Setting | Value |
|---------|-------|
| Hostname | `wordclock` |
| Username and password | the user from 1.1 and a password |
| Wi-Fi | your network, country `ES` |
| Time zone | `Europe/Madrid` |
| SSH | enabled, **public-key authentication only**, with `~/.ssh/wordclock.pub` pasted in |
| Raspberry Pi Connect | off (see below) |

5. Write the card. The Imager verifies it and ejects it.

If writing fails, use **Operating system → Erase** to format the card
completely and try again. If it still fails, replace the card.

> **Raspberry Pi Connect** gives remote access to the Pi from a browser at
> [connect.raspberrypi.com](https://connect.raspberrypi.com), through
> Raspberry Pi's servers and with a Raspberry Pi account. At home `ssh
> wordclock` is enough. To reach the Pi from outside later, install the
> shell-only version: `sudo apt install rpi-connect-lite` and
> `rpi-connect signin`.

### 1.3 First boot

Put the card in the Pi and power it on with its own supply (micro-USB, 5V
2,5 A for the Pi 3B). The first boot takes a minute or two while it
applies the settings.

---

## 2. First connection and update

From your computer:

```bash
ssh wordclock
```

> If `wordclock.local` does not resolve, find the Pi's IP address on your
> router, change `HostName` in `~/.ssh/config` to that address, and try
> again.

The rest of this guide uses the user `pi` in paths such as `/home/pi`:
replace it with your user if you chose another one.

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

- [ ] SSH key `~/.ssh/wordclock` created and `wordclock` host added to `~/.ssh/config`
- [ ] Raspberry Pi OS Lite (64-bit) flashed with hostname, Wi-Fi and SSH key, Raspberry Pi Connect off
- [ ] `ssh wordclock` connects
- [ ] System updated, build tools installed
- [ ] `uv` installed, repository cloned, `uv sync --extra rpi --extra dev` done
- [ ] Tests pass and the web simulator opens on port 5000
- [ ] Audio off in `/boot/firmware/config.txt`
- [ ] First strip lit with [06 — Bench Test](06-bench-test.md)
- [ ] systemd service enabled
