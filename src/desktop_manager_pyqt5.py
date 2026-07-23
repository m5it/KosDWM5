#!/usr/bin/env python3
"""
Desktop Manager for KosDWM PyQt5
Handles virtual desktops and window management
"""

import subprocess
import re
from PyQt5.QtCore import QObject, pyqtSignal, QTimer


class DesktopManager(QObject):
    """
    Manages virtual desktops using wmctrl
    """
    
    desktop_changed = pyqtSignal(int)
    window_list_changed = pyqtSignal(list)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_desktop = 0
        self.total_desktops = 4
        self.windows = {}
        
        # Timer to update window list
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_window_list)
        self.timer.start(1000)  # Update every second
        
        # Initial update
        self.update_window_list()
        self.get_current_desktop()
    
    def get_current_desktop(self):
        """Get current desktop using wmctrl"""
        try:
            result = subprocess.run(
                ["wmctrl", "-d"],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                # Parse output to find current desktop
                for line in result.stdout.strip().split("\n"):
                    if "*" in line:  # Current desktop has asterisk
                        parts = line.split()
                        self.current_desktop = int(parts[0])
                        self.desktop_changed.emit(self.current_desktop)
                        return self.current_desktop
        except Exception as e:
            print(f"Error getting current desktop: {e}")
        return self.current_desktop
    
    def switch_to_desktop(self, desktop_id):
        """Switch to specified desktop"""
        try:
            subprocess.run(
                ["wmctrl", "-s", str(desktop_id)],
                check=True,
                timeout=2
            )
            self.current_desktop = desktop_id
            self.desktop_changed.emit(desktop_id)
            return True
        except Exception as e:
            print(f"Error switching desktop: {e}")
            return False
    
    def update_window_list(self):
        """Update list of windows using wmctrl -l"""
        try:
            result = subprocess.run(
                ["wmctrl", "-l"],
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                new_windows = {}
                for line in result.stdout.strip().split("\n"):
                    if line:
                        parts = line.split(None, 3)
                        if len(parts) >= 4:
                            wid, desktop, host, name = parts[0], parts[1], parts[2], parts[3]
                            new_windows[wid] = {
                                "id": wid,
                                "desktop": desktop,
                                "host": host,
                                "name": name
                            }
                self.windows = new_windows
                self.window_list_changed.emit(list(self.windows.values()))
        except Exception as e:
            print(f"Error updating window list: {e}")
    
    def activate_window(self, window_id):
        """Activate a specific window"""
        try:
            subprocess.run(
                ["wmctrl", "-i", "-a", window_id],
                check=True,
                timeout=2
            )
            return True
        except Exception as e:
            print(f"Error activating window: {e}")
            return False
    
    def close_window(self, window_id):
        """Close a specific window"""
        try:
            subprocess.run(
                ["wmctrl", "-i", "-c", window_id],
                check=True,
                timeout=2
            )
            return True
        except Exception as e:
            print(f"Error closing window: {e}")
            return False
    
    def get_windows_for_desktop(self, desktop_id):
        """Get list of windows on a specific desktop"""
        return [
            win for win in self.windows.values()
            if win["desktop"] == str(desktop_id)
        ]
