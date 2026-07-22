"""
CPU Monitor Gadget for KosDWM
==============================

A simple CPU usage monitor that shows current CPU load.
Demonstrates reading system statistics and updating display dynamically.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from gadgets import GadgetBase
from tkinter import messagebox
import time


class CpuMonitorGadget(GadgetBase):
    """
    A gadget that monitors CPU usage.
    Shows current CPU load percentage when clicked.
    """
    
    def __init__(self):
        super().__init__()
        self.last_cpu_times = None
    
    def get_name(self) -> str:
        return "cpu_monitor"
    
    def get_icon(self) -> str:
        return "CPU"
    
    def get_tooltip(self) -> str:
        return "Click to view CPU usage"
    
    def get_description(self) -> str:
        return "Displays current CPU usage percentage (Linux only)."
    
    def _read_cpu_stats(self):
        """Read CPU statistics from /proc/stat."""
        try:
            with open('/proc/stat', 'r') as f:
                line = f.readline()
                # First line is aggregate CPU stats
                # Format: cpu user nice system idle iowait irq softirq steal guest guest_nice
                fields = line.strip().split()
                if fields[0] != 'cpu':
                    return None
                
                # Sum all time fields (skip 'cpu' label)
                times = [int(x) for x in fields[1:]]
                user_time = times[0]
                nice_time = times[1]
                system_time = times[2]
                idle_time = times[3]
                iowait_time = times[4] if len(times) > 4 else 0
                
                busy_time = user_time + nice_time + system_time
                total_time = busy_time + idle_time + iowait_time
                
                return {'busy': busy_time, 'total': total_time}
        except:
            return None
    
    def _calculate_cpu_usage(self):
        """Calculate current CPU usage percentage."""
        current_stats = self._read_cpu_stats()
        
        if current_stats is None:
            return None
        
        if self.last_cpu_times is None:
            # First reading, store and wait for next
            self.last_cpu_times = current_stats
            time.sleep(0.1)  # Short delay for second reading
            current_stats = self._read_cpu_stats()
        
        if current_stats is None or self.last_cpu_times is None:
            return None
        
        # Calculate difference
        busy_diff = current_stats['busy'] - self.last_cpu_times['busy']
        total_diff = current_stats['total'] - self.last_cpu_times['total']
        
        self.last_cpu_times = current_stats
        
        if total_diff == 0:
            return 0.0
        
        usage = (busy_diff / total_diff) * 100
        return usage
    
    def on_click(self, event=None):
        """Display current CPU usage."""
        usage = self._calculate_cpu_usage()
        
        if usage is None:
            messagebox.showinfo(
                "CPU Monitor", 
                "Unable to read CPU statistics.\n\n"
                "This gadget works on Linux systems only."
            )
            return
        
        # Get CPU count
        try:
            with open('/proc/cpuinfo', 'r') as f:
                cpu_count = sum(1 for line in f if line.startswith('processor'))
        except:
            cpu_count = "Unknown"
        
        usage_text = (
            f"Current CPU Usage: {usage:.1f}%\n"
            f"CPU Cores: {cpu_count}\n\n"
            f"Status: {'High' if usage > 80 else 'Moderate' if usage > 50 else 'Low'}"
        )
        
        messagebox.showinfo("CPU Monitor", usage_text)
