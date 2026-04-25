# 03 — Software

## Overview

The software stack runs entirely on the Raspberry Pi. It consists of:

- **Raspberry Pi OS Lite** — headless operating system
- **Python 3.13+** — managed by `uv`
- **wordclock** — the Python package (LED control, time logic)
- **Flask API** — serves the web interface and REST endpoints
- **systemd** — keeps the clock running automatically on boot

---

## 1. Raspberry Pi OS Lite setup

### 1.1 Flash the SD card

Download and install the **Raspberry Pi Imager** from [raspberrypi.com/software](https://www.raspberrypi.com/software/).

In the imager:
1. Choose **Raspberry Pi OS Lite (64-bit)** as the operating system
2. Select your SD card
3. Click the **gear icon (⚙)** to open advanced settings before flashing:

### 1.2 Configure Wi-Fi and SSH in the imager

In the advanced settings panel fill in:

| Setting | Value |
|---------|-------|
| Hostname | `wordclock` |
| Enable SSH | ✅ Use password authentication |
| Username | `pi` (or your preference) |
| Password | choose a strong password |
| Wi-Fi SSID | your network name |
| Wi-Fi password | your network password |
| Wi-Fi country | `ES` |
| Locale / timezone | `Europe/Madrid` |

Flash the card, insert it into the Raspberry Pi and power it on.

### 1.3 Connect via SSH

After a minute or two, connect from your computer:

```bash
ssh pi@wordclock.local
```

> If `wordclock.local` does not resolve, find the IP address from your router and use that instead.

---

## 2. System dependencies

Update the system and install the packages needed to drive the LED strip:

```bash
sudo apt update && sudo apt upgrade -y

# Required for rpi-ws281x
sudo apt install -y python3-pip python3-dev gcc make git
```

---

## 3. Install uv

`uv` is a fast Python package and project manager. It replaces `pip`, `venv` and `pyenv` in a single tool.

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh

# Reload the shell so the uv command is available
source $HOME/.local/bin/env
```

Verify the installation:

```bash
uv --version
```

---

## 4. Clone the repository

```bash
cd ~
git clone https://github.com/eballo/word-clock.git
cd word-clock
```

---

## 5. Create the virtual environment and install dependencies

```bash
# Create the venv and install all dependencies
uv sync

# Install the Raspberry Pi LED library (hardware only)
uv pip install "wordclock[rpi]"
```

The virtual environment is created automatically inside `.venv/`.

---

## 6. Enable SPI and PWM for the LED strip

The WS2812B strip uses the PWM interface on GPIO 18. Edit the boot configuration:

```bash
sudo nano /boot/firmware/config.txt
```

Add or verify the following lines at the end:

```ini
# Disable audio (conflicts with PWM on GPIO 18)
dtparam=audio=off

# Enable PWM
core_freq=500
core_freq_min=500
```

Save and reboot:

```bash
sudo reboot
```

---

## 7. Test the installation

After rebooting, SSH back in and run a quick test:

```bash
cd ~/word-clock

# Test the time logic (no hardware needed)
uv run python -m wordclock.layouts.catalan

# Test the LED controller in mock mode (no hardware needed)
uv run wordclock --mock --debug

# Run the Flask API in mock mode and open http://wordclock.local:5000
uv run wordclock-api --mock --debug
```

To test with the real LED strip connected:

```bash
# The LED strip requires root access to the PWM interface
sudo .venv/bin/wordclock --debug
```

---

## 8. Run the tests

```bash
uv run pytest
```

---

## 9. Configure systemd to run on boot

Create a systemd service file:

```bash
sudo nano /etc/systemd/system/wordclock.service
```

Paste the following content (adjust the username if you chose a different one):

```ini
[Unit]
Description=Word Clock
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/home/pi/word-clock
ExecStart=/home/pi/word-clock/.venv/bin/wordclock-api --host 0.0.0.0 --port 5000
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start the service:

```bash
# Reload systemd configuration
sudo systemctl daemon-reload

# Enable the service to start on boot
sudo systemctl enable wordclock

# Start it now
sudo systemctl start wordclock

# Check it is running
sudo systemctl status wordclock
```

The web interface will be available at **http://wordclock.local:5000** from any device on the same network.

---

## 10. Useful commands

| Command | Description |
|---------|-------------|
| `sudo systemctl status wordclock` | Check if the service is running |
| `sudo systemctl restart wordclock` | Restart after a code change |
| `sudo systemctl stop wordclock` | Stop the service |
| `sudo journalctl -u wordclock -f` | Follow the live logs |
| `uv run pytest` | Run the test suite |
| `uv run wordclock --mock` | Run clock loop in mock mode |
| `uv run wordclock-api --mock` | Run API in mock mode |

---

## 11. Updating the code

```bash
cd ~/word-clock

# Pull the latest changes
git pull

# Re-sync dependencies if pyproject.toml changed
uv sync

# Restart the service
sudo systemctl restart wordclock
```