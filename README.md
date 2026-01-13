# 📡 Hotspot Applet for Linux

A lightweight system tray applet to manage Wi-Fi hotspot sharing. Works on Pop!_OS, Ubuntu, Fedora, Arch, and other Linux distros with GNOME.

## Features

- 🔘 One-click hotspot toggle from system tray
- ⚙️ Configure SSID, password, and frequency band
- 📱 View connected clients
- 🚀 Auto-start on login
- 💾 Persistent settings

---

## Quick Start

```bash
git clone https://github.com/farouq-alt/Hotspot-for-linux-with-a-built-in-ui.git
cd Hotspot-for-linux-with-a-built-in-ui
python3 hotspot-applet.py
```

---

## Installation by Distro

### Pop!_OS / Ubuntu / Debian

```bash
# Install dependencies
sudo apt update
sudo apt install python3 python3-gi gir1.2-appindicator3-0.1 gir1.2-gtk-3.0

# Run the applet
python3 hotspot-applet.py

# Or use the installer for permanent setup
chmod +x install.sh
./install.sh
```

### Fedora

```bash
# Install dependencies
sudo dnf install python3 python3-gobject gtk3 libappindicator-gtk3

# Run the applet
python3 hotspot-applet.py
```

### Arch Linux / Manjaro

```bash
# Install dependencies
sudo pacman -S python python-gobject gtk3 libappindicator-gtk3

# Run the applet
python3 hotspot-applet.py
```

### openSUSE

```bash
# Install dependencies
sudo zypper install python3 python3-gobject gtk3 typelib-1_0-AppIndicator3-0_1

# Run the applet
python3 hotspot-applet.py
```

---

## Enable System Tray Support

Most GNOME-based distros need an extension to show tray icons.

### Pop!_OS / Ubuntu
```bash
sudo apt install gnome-shell-extension-appindicator
```
Then log out and back in, or enable it in the Extensions app.

### Fedora
```bash
sudo dnf install gnome-shell-extension-appindicator
```

### Arch
```bash
sudo pacman -S gnome-shell-extension-appindicator
```

---

## Check if Your Wi-Fi Supports Hotspot

Your Wi-Fi adapter must support AP (Access Point) mode:

```bash
iw list | grep -A 10 "Supported interface modes"
```

Look for `* AP` in the output. If it's missing, your hardware can't create a hotspot.

---

## Usage

1. Run the applet (it appears in your system tray)
2. Click the icon → "Start Hotspot"
3. Click "Settings..." to change SSID/password
4. Connected devices show under "Connected Clients"

### Default Settings
- SSID: `PopOS-Hotspot`
- Password: `hotspot123`
- Band: 2.4 GHz

---

## Autostart on Login

### Option 1: Use the installer (Pop!_OS/Ubuntu)
```bash
./install.sh
```

### Option 2: Manual
Copy the desktop file to autostart:
```bash
mkdir -p ~/.config/autostart
cp hotspot-applet.desktop ~/.config/autostart/
```

---

## Configuration

Settings are saved to: `~/.config/hotspot-applet/config.json`

```json
{
  "ssid": "MyHotspot",
  "password": "SecurePassword123",
  "interface": "wlan0",
  "band": "bg"
}
```

Band options:
- `bg` = 2.4 GHz
- `a` = 5 GHz

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| No tray icon | Install and enable AppIndicator extension (see above) |
| Hotspot won't start | Check if Wi-Fi supports AP mode (`iw list`) |
| Clients can't get internet | Make sure you're connected via Ethernet |
| "Connection failed" | Check `journalctl -xe` for NetworkManager errors |
| Wrong interface detected | Edit interface in Settings or config.json |

---

## Uninstall

```bash
./uninstall.sh
```

Or manually:
```bash
rm -f ~/.config/autostart/hotspot-applet.desktop
rm -rf ~/.config/hotspot-applet
```

---

## Requirements

- Python 3.6+
- GTK 3
- NetworkManager
- libappindicator3
- Wi-Fi adapter with AP mode support

---

## License

MIT
