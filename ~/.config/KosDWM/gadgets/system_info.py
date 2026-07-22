"""
System Info Gadget for KosDWM
=============================

Displays basic system information when clicked.
Demonstrates running system commands and displaying results.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from gadgets import GadgetBase
from tkinter import messagebox
import platform
import subprocess


class SystemInfoGadget(GadgetBase):
    """
    A gadget that displays system information.
    Shows hostname, OS, kernel version, and uptime when clicked.
    """
    
    def __init__(self):
        super().__init__()
        self.hostname = platform.node()
    
    def get_name(self) -> str:
        return "system_info"
    
    def get_icon(self) -> str:
        return "SYS"
    
    def get_tooltip(self) -> str:
        return "Click to view system information"
    
    def get_description(self) -> str:
        return "Displays hostname, OS version, and system uptime."
    
    def on_click(self, event=None):
        """Gather and display system information."""
        try:
            # Get OS info
            os_info = f"{platform.system()} {platform.release()}"
            
            # Get uptime (Linux-specific)
            uptime = "Unknown"
            try:
                result = subprocess.run(['uptime', '-p'], 
                                      capture_output=True, text=True, timeout=2)
                if result.returncode == 0:
                    uptime = result.stdout.strip()
            except:
                pass
            
            # Get memory info (Linux-specific)
            mem_info = "Unknown"
            try:
                with open('/proc/meminfo', 'r') as f:
                    lines = f.readlines()
                    mem_total = next((l for l in lines if l.startswith('MemTotal:')), '')
                    mem_free = next((l for l in lines if l.startswith('MemFree:')), '')
                    if mem_total and mem_free:
                        total_mb = int(mem_total.split()[1]) // 1024
                        free_mb = int(mem_free.split()[1]) // 1024
                        used_mb = total_mb - free_mb
                        mem_info = f"{used_mb}MB / {total_mb}MB used"
            except:
                pass
            
            info_text = (
                f"Hostname: {self.hostname}\n"
                f"OS: {os_info}\n"
                f"Uptime: {uptime}\n"
                f"Memory: {mem_info}"
            )
            
            messagebox.showinfo("System Information", info_text)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to get system info: {e}")
