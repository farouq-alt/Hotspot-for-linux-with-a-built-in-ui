#!/bin/bash
# Hotspot Applet Installer for Pop!_OS

set -e

echo "=== Hotspot Applet Installer ==="
echo ""

# Check if running on Pop!_OS or Ubuntu-based system
if ! command -v apt &> /dev/null; then
    echo "Error: This installer requires apt (Debian/Ubuntu-based system)"
    exit 1
fi

# Install dependencies
echo "[1/4] Installing dependencies..."
sudo apt update
sudo apt install -y python3 python3-gi gir1.2-appindicator3-0.1 gir1.2-gtk-3.0

# Copy the applet script
echo "[2/4] Installing applet..."
sudo cp hotspot-applet.py /usr/local/bin/hotspot-applet
sudo chmod +x /usr/local/bin/hotspot-applet

# Install desktop entry for app menu
echo "[3/4] Installing desktop entry..."
sudo cp hotspot-applet.desktop /usr/share/applications/

# Install autostart entry
echo "[4/4] Setting up autostart..."
mkdir -p ~/.config/autostart
cp hotspot-applet.desktop ~/.config/autostart/

echo ""
echo "=== Installation Complete ==="
echo ""
echo "You can now:"
echo "  1. Run 'hotspot-applet' from terminal to test"
echo "  2. Find 'Hotspot Applet' in your applications menu"
echo "  3. It will auto-start on next login"
echo ""
echo "The applet will appear in your system tray (top bar)."
echo ""
