#!/usr/bin/env python3
"""
Hotspot Applet for Pop!_OS
A system tray applet to manage Wi-Fi hotspot sharing
"""

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, AppIndicator3, GLib
import subprocess
import os
import json

class HotspotApplet:
    CONFIG_FILE = os.path.expanduser("~/.config/hotspot-applet/config.json")
    CONNECTION_NAME = "hotspot-applet"
    
    def __init__(self):
        self.load_config()
        
        # Create the indicator
        self.indicator = AppIndicator3.Indicator.new(
            "hotspot-applet",
            "network-wireless-hotspot-symbolic",
            AppIndicator3.IndicatorCategory.SYSTEM_SERVICES
        )
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        
        # Build menu
        self.build_menu()
        
        # Update status every 5 seconds
        GLib.timeout_add_seconds(5, self.update_status)
        self.update_status()
    
    def load_config(self):
        """Load configuration from file"""
        self.config = {
            "ssid": "PopOS-Hotspot",
            "password": "hotspot123",
            "interface": self.detect_wifi_interface(),
            "band": "bg"  # bg = 2.4GHz, a = 5GHz
        }
        
        os.makedirs(os.path.dirname(self.CONFIG_FILE), exist_ok=True)
        
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, 'r') as f:
                    saved = json.load(f)
                    self.config.update(saved)
            except:
                pass
    
    def save_config(self):
        """Save configuration to file"""
        os.makedirs(os.path.dirname(self.CONFIG_FILE), exist_ok=True)
        with open(self.CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def detect_wifi_interface(self):
        """Detect the Wi-Fi interface name"""
        try:
            result = subprocess.run(
                ["nmcli", "-t", "-f", "DEVICE,TYPE", "device"],
                capture_output=True, text=True
            )
            for line in result.stdout.strip().split('\n'):
                if ':wifi' in line:
                    return line.split(':')[0]
        except:
            pass
        return "wlan0"
    
    def is_hotspot_active(self):
        """Check if hotspot is currently active"""
        try:
            result = subprocess.run(
                ["nmcli", "-t", "-f", "NAME,TYPE", "connection", "show", "--active"],
                capture_output=True, text=True
            )
            for line in result.stdout.strip().split('\n'):
                if self.CONNECTION_NAME in line:
                    return True
        except:
            pass
        return False
    
    def get_connected_clients(self):
        """Get list of connected clients"""
        clients = []
        try:
            # Check ARP table for connected devices
            result = subprocess.run(
                ["arp", "-n"],
                capture_output=True, text=True
            )
            for line in result.stdout.strip().split('\n')[1:]:
                parts = line.split()
                if len(parts) >= 3 and parts[0].startswith("10.42."):
                    clients.append({"ip": parts[0], "mac": parts[2]})
        except:
            pass
        return clients

    def build_menu(self):
        """Build the indicator menu"""
        self.menu = Gtk.Menu()
        
        # Status item
        self.status_item = Gtk.MenuItem(label="Status: Checking...")
        self.status_item.set_sensitive(False)
        self.menu.append(self.status_item)
        
        # SSID display
        self.ssid_item = Gtk.MenuItem(label=f"SSID: {self.config['ssid']}")
        self.ssid_item.set_sensitive(False)
        self.menu.append(self.ssid_item)
        
        self.menu.append(Gtk.SeparatorMenuItem())
        
        # Toggle hotspot
        self.toggle_item = Gtk.MenuItem(label="Start Hotspot")
        self.toggle_item.connect("activate", self.toggle_hotspot)
        self.menu.append(self.toggle_item)
        
        self.menu.append(Gtk.SeparatorMenuItem())
        
        # Connected clients submenu
        self.clients_item = Gtk.MenuItem(label="Connected Clients")
        self.clients_submenu = Gtk.Menu()
        self.clients_item.set_submenu(self.clients_submenu)
        self.menu.append(self.clients_item)
        
        self.menu.append(Gtk.SeparatorMenuItem())
        
        # Settings
        settings_item = Gtk.MenuItem(label="Settings...")
        settings_item.connect("activate", self.show_settings)
        self.menu.append(settings_item)
        
        self.menu.append(Gtk.SeparatorMenuItem())
        
        # Quit
        quit_item = Gtk.MenuItem(label="Quit")
        quit_item.connect("activate", self.quit)
        self.menu.append(quit_item)
        
        self.menu.show_all()
        self.indicator.set_menu(self.menu)
    
    def update_status(self):
        """Update the status display"""
        active = self.is_hotspot_active()
        
        if active:
            self.status_item.set_label("Status: Active ✓")
            self.toggle_item.set_label("Stop Hotspot")
            self.indicator.set_icon("network-wireless-hotspot-symbolic")
        else:
            self.status_item.set_label("Status: Inactive")
            self.toggle_item.set_label("Start Hotspot")
            self.indicator.set_icon("network-wireless-offline-symbolic")
        
        self.ssid_item.set_label(f"SSID: {self.config['ssid']}")
        
        # Update clients list
        self.update_clients_menu()
        
        return True  # Keep the timeout running
    
    def update_clients_menu(self):
        """Update the connected clients submenu"""
        # Clear existing items
        for child in self.clients_submenu.get_children():
            self.clients_submenu.remove(child)
        
        clients = self.get_connected_clients()
        
        if clients:
            for client in clients:
                item = Gtk.MenuItem(label=f"{client['ip']} ({client['mac']})")
                item.set_sensitive(False)
                self.clients_submenu.append(item)
        else:
            item = Gtk.MenuItem(label="No clients connected")
            item.set_sensitive(False)
            self.clients_submenu.append(item)
        
        self.clients_submenu.show_all()
    
    def toggle_hotspot(self, widget):
        """Toggle the hotspot on/off"""
        if self.is_hotspot_active():
            self.stop_hotspot()
        else:
            self.start_hotspot()
        
        GLib.timeout_add(1000, self.update_status)
    
    def start_hotspot(self):
        """Start the hotspot"""
        # First, delete any existing connection with same name
        subprocess.run(
            ["nmcli", "connection", "delete", self.CONNECTION_NAME],
            capture_output=True
        )
        
        # Create and start hotspot
        result = subprocess.run([
            "nmcli", "device", "wifi", "hotspot",
            "ifname", self.config["interface"],
            "con-name", self.CONNECTION_NAME,
            "ssid", self.config["ssid"],
            "password", self.config["password"]
        ], capture_output=True, text=True)
        
        if result.returncode != 0:
            self.show_error("Failed to start hotspot", result.stderr)
    
    def stop_hotspot(self):
        """Stop the hotspot"""
        subprocess.run(
            ["nmcli", "connection", "down", self.CONNECTION_NAME],
            capture_output=True
        )

    def show_settings(self, widget):
        """Show the settings dialog"""
        dialog = Gtk.Dialog(
            title="Hotspot Settings",
            parent=None,
            flags=0
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_SAVE, Gtk.ResponseType.OK
        )
        dialog.set_default_size(350, 200)
        
        content = dialog.get_content_area()
        content.set_spacing(10)
        content.set_margin_start(15)
        content.set_margin_end(15)
        content.set_margin_top(15)
        content.set_margin_bottom(15)
        
        # SSID
        ssid_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        ssid_label = Gtk.Label(label="Network Name (SSID):")
        ssid_label.set_xalign(0)
        ssid_entry = Gtk.Entry()
        ssid_entry.set_text(self.config["ssid"])
        ssid_entry.set_hexpand(True)
        ssid_box.pack_start(ssid_label, False, False, 0)
        ssid_box.pack_start(ssid_entry, True, True, 0)
        content.pack_start(ssid_box, False, False, 0)
        
        # Password
        pass_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        pass_label = Gtk.Label(label="Password:")
        pass_label.set_xalign(0)
        pass_entry = Gtk.Entry()
        pass_entry.set_text(self.config["password"])
        pass_entry.set_visibility(False)
        pass_entry.set_hexpand(True)
        show_pass = Gtk.CheckButton(label="Show")
        show_pass.connect("toggled", lambda w: pass_entry.set_visibility(w.get_active()))
        pass_box.pack_start(pass_label, False, False, 0)
        pass_box.pack_start(pass_entry, True, True, 0)
        pass_box.pack_start(show_pass, False, False, 0)
        content.pack_start(pass_box, False, False, 0)
        
        # Interface
        iface_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        iface_label = Gtk.Label(label="Wi-Fi Interface:")
        iface_label.set_xalign(0)
        iface_entry = Gtk.Entry()
        iface_entry.set_text(self.config["interface"])
        iface_entry.set_hexpand(True)
        iface_box.pack_start(iface_label, False, False, 0)
        iface_box.pack_start(iface_entry, True, True, 0)
        content.pack_start(iface_box, False, False, 0)
        
        # Band selection
        band_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        band_label = Gtk.Label(label="Frequency Band:")
        band_label.set_xalign(0)
        band_combo = Gtk.ComboBoxText()
        band_combo.append("bg", "2.4 GHz")
        band_combo.append("a", "5 GHz")
        band_combo.set_active_id(self.config.get("band", "bg"))
        band_box.pack_start(band_label, False, False, 0)
        band_box.pack_start(band_combo, True, True, 0)
        content.pack_start(band_box, False, False, 0)
        
        dialog.show_all()
        response = dialog.run()
        
        if response == Gtk.ResponseType.OK:
            self.config["ssid"] = ssid_entry.get_text()
            self.config["password"] = pass_entry.get_text()
            self.config["interface"] = iface_entry.get_text()
            self.config["band"] = band_combo.get_active_id()
            self.save_config()
            
            # If hotspot is active, restart it with new settings
            if self.is_hotspot_active():
                self.stop_hotspot()
                GLib.timeout_add(1000, self.start_hotspot)
        
        dialog.destroy()
    
    def show_error(self, title, message):
        """Show an error dialog"""
        dialog = Gtk.MessageDialog(
            parent=None,
            flags=0,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=title
        )
        dialog.format_secondary_text(message)
        dialog.run()
        dialog.destroy()
    
    def quit(self, widget):
        """Quit the applet"""
        Gtk.main_quit()


def main():
    applet = HotspotApplet()
    Gtk.main()


if __name__ == "__main__":
    main()
