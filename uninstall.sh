#!/bin/bash
# Hotspot Applet Uninstaller

echo "=== Hotspot Applet Uninstaller ==="
echo ""

# Stop any running instance
pkill -f hotspot-applet 2>/dev/null || true

# Remove files
echo "Removing applet..."
sudo rm -f /usr/local/bin/hotspot-applet
sudo rm -f /usr/share/applications/hotspot-applet.desktop
rm -f ~/.config/autostart/hotspot-applet.desktop

echo ""
echo "Uninstallation complete."
echo "Config file at ~/.config/hotspot-applet/ was preserved."
echo "Remove it manually if you want a clean uninstall."
