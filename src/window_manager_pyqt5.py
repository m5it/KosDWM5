#!/usr/bin/env python3
"""
Window Manager module for KosDWM PyQt5
Handles listing and switching between running windows using wmctrl
"""

import subprocess
import re
from PyQt5.QtCore import QObject, pyqtSignal


class WindowManager(QObject):
    """
    Manages window listing and switching using wmctrl
    """
    
    windows_changed = pyqtSignal(list)  # Emitted when window list changes
    
    def __init__(self):
        super().__init__()
        self._windows = []
        self._wmctrl_available = self._check_wmctrl()
    
    def _check_wmctrl(self):
        """Check if wmctrl is installed and available"""
        try:
            result = subprocess.run(
                ['which', 'wmctrl'],
                capture_output=True,
                text=True,
                timeout=2
            )
            return result.returncode == 0
        except Exception:
            return False
    
    def is_available(self):
        """Return True if wmctrl is available"""
        return self._wmctrl_available
    
    def get_windows(self):
        """
        Get list of all windows using wmctrl -l
        
        Returns:
            List of dicts with keys: id, desktop, title, name
        """
        if not self._wmctrl_available:
            return []
        
        try:
            result = subprocess.run(
                ['wmctrl', '-l'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode != 0:
                print(f"wmctrl error: {result.stderr}")
                return self._windows  # Return cached list
            
            windows = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                
                # Parse: 0x01234567  0  Desktop Name - Window Title
                # Format: window_id desktop title (title may contain spaces)
                match = re.match(r'^(\S+)\s+(\d+)\s+(.+)$', line)
                if match:
                    window_id = match.group(1)
                    desktop = int(match.group(2))
                    title = match.group(3).strip()
                    
                    # Extract window name (last part after " - " if present)
                    if ' - ' in title:
                        parts = title.rsplit(' - ', 1)
                        name = parts[-1]
                    else:
                        name = title
                    
                    windows.append({
                        'id': window_id,
                        'desktop': desktop,
                        'title': title,
                        'name': name
                    })
            
            self._windows = windows
            return windows
            
        except subprocess.TimeoutExpired:
            print("wmctrl command timed out")
            return self._windows
        except Exception as e:
            print(f"Error getting windows: {e}")
            return self._windows
    
    def activate_window(self, window_id):
        """
        Activate/focus a window by its ID
        
        Args:
            window_id: Window ID in hex format (e.g., "0x01234567")
        
        Returns:
            True if successful, False otherwise
        """
        if not self._wmctrl_available:
            print("wmctrl not available")
            return False
        
        try:
            result = subprocess.run(
                ['wmctrl', '-ia', window_id],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                return True
            else:
                print(f"Failed to activate window {window_id}: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("wmctrl activate command timed out")
            return False
        except Exception as e:
            print(f"Error activating window: {e}")
            return False
    
    def refresh(self):
        """
        Refresh the window list and emit signal if changed
        
        Returns:
            List of current windows
        """
        old_windows = self._windows.copy()
        new_windows = self.get_windows()
        
        # Simple comparison - could be more sophisticated
        if len(old_windows) != len(new_windows):
            self.windows_changed.emit(new_windows)
        elif old_windows != new_windows:
            self.windows_changed.emit(new_windows)
        
        return new_windows
    
    def get_window_by_id(self, window_id):
        """
        Get window info by ID
        
        Args:
            window_id: Window ID to find
        
        Returns:
            Window dict or None
        """
        for window in self._windows:
            if window['id'] == window_id:
                return window
        return None
