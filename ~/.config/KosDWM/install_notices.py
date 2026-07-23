#!/usr/bin/env python3
"""
Install Notices Gadget for KosDWM
"""

import os
import sys
import json
from pathlib import Path


def find_kosdwm():
    """Find KosDWM installation."""
    home = Path.home()
    
    # Check common locations
    locations = [
        home / "adata2" / "OurAI" / "playground" / "KosDWM",
        home / "KosDWM",
    ]
    
    for loc in locations:
        if (loc / "src" / "gadgets.py").exists():
            return loc
    
    # Check current directory and parents
    current = Path.cwd()
    for parent in [current] + list(current.parents):
        if (parent / "src" / "gadgets.py").exists():
            return parent
    
    return None


def main():
    print("=" * 60)
    print("Notices Gadget Installer")
    print("=" * 60)
    print()
    
    # Find KosDWM
    kosdwm = find_kosdwm()
    
    if kosdwm:
        print(f"Found KosDWM at: {kosdwm}")
    else:
        print("KosDWM not found automatically.")
        user_path = input("Enter KosDWM path: ").strip()
        if not user_path:
            print("Cancelled")
            return 1
        kosdwm = Path(user_path).expanduser()
    
    # Verify
    if not (kosdwm / "src" / "gadgets.py").exists():
        print(f"Error: Not a valid KosDWM installation")
        return 1
    
    # Setup paths
    src_dir = kosdwm / "src"
    config_dir = Path.home() / ".config" / "KosDWM"
    gadget_dir = config_dir / "gadgets"
    
    config_dir.mkdir(parents=True, exist_ok=True)
    gadget_dir.mkdir(parents=True, exist_ok=True)
    
    # Save config
    config = {"kosdwm_path": str(kosdwm)}
    with open(config_dir / "notices_gadget.conf", 'w') as f:
        json.dump(config, f)
    print(f"Config saved")
    
    # Check if source files exist in KosDWM src
    source_files = ["notices_store.py", "notices_api.py", "notifications.py"]
    script_dir = Path(__file__).parent
    
    for fname in source_files:
        src_file = script_dir / "src" / fname
        dst_file = src_dir / fname
        
        if src_file.exists():
            with open(src_file, 'r') as f:
                content = f.read()
            with open(dst_file, 'w') as f:
                f.write(content)
            print(f"Installed: {fname}")
        else:
            print(f"Warning: {fname} not found in {src_file}")
    
    # Create simplified gadget file
    gadget_file = gadget_dir / "notices.py"
    
    gadget_code = '''#!/usr/bin/env python3
"""
Notices Gadget
"""

import sys
from pathlib import Path
import json

# Load KosDWM path from config
KOSDWM_PATH = None
config_path = Path.home() / ".config" / "KosDWM" / "notices_gadget.conf"
if config_path.exists():
    with open(config_path) as f:
        cfg = json.load(f)
        KOSDWM_PATH = Path(cfg.get("kosdwm_path", ""))

if not KOSDWM_PATH or not KOSDWM_PATH.exists():
    KOSDWM_PATH = Path.home() / "adata2" / "OurAI" / "playground" / "KosDWM"

sys.path.insert(0, str(KOSDWM_PATH / "src"))

from gadgets import GadgetBase

try:
    from notices_store import NoticesStore
    STORE_OK = True
except ImportError as e:
    print(f"Notices error: {e}")
    STORE_OK = False

from tkinter import messagebox, ttk
import tkinter as tk
from datetime import datetime


class NoticesGadget(GadgetBase):
    def __init__(self):
        super().__init__()
        self.store = NoticesStore() if STORE_OK else None
        self.window = None
        self.tree = None
        self.filter_var = None
        self.search_var = None
    
    def get_name(self):
        return "notices"
    
    def get_icon(self):
        if not self.store:
            return "ERR"
        count = self.store.get_active_count()
        return f"N:{count}" if count > 0 else "N:0"
    
    def get_tooltip(self):
        if not self.store:
            return "Notices (Error)"
        active = self.store.get_active_count()
        return f"Notices: {active} active"
    
    def get_description(self):
        return "Manage notices and reminders"
    
    def on_click(self, event=None):
        if not self.store:
            messagebox.showerror("Error", "Store not available")
            return
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return
        self._create_window()
    
    def _create_window(self):
        self.window = tk.Toplevel()
        self.window.title("Notices")
        self.window.geometry("800x500")
        
        # Header
        header = tk.Frame(self.window)
        header.pack(fill=tk.X, padx=10, pady=10)
        tk.Label(header, text="Notices Manager", font=('Arial', 14, 'bold')).pack(side=tk.LEFT)
        
        # Toolbar
        toolbar = tk.Frame(self.window)
        toolbar.pack(fill=tk.X, padx=10)
        tk.Button(toolbar, text="New", command=self._add).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="Edit", command=self._edit).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="Delete", command=self._delete).pack(side=tk.LEFT, padx=2)
        tk.Button(toolbar, text="Refresh", command=self._refresh).pack(side=tk.LEFT, padx=2)
        
        # Tree
        tree_frame = tk.Frame(self.window)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        columns = ('title', 'due', 'priority', 'status')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        self.tree.heading('title', text='Title')
        self.tree.heading('due', text='Due Date')
        self.tree.heading('priority', text='Priority')
        self.tree.heading('status', text='Status')
        self.tree.pack(fill=tk.BOTH, expand=True)
        
        self.tree.bind('<Double-1>', lambda e: self._edit())
        
        self._refresh()
    
    def _get_notices(self):
        return self.store.get_all()
    
    def _refresh(self):
        if not self.tree:
            return
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        for n in self._get_notices():
            dd = n.due_date.strftime('%Y-%m-%d') if n.due_date else "-"
            status = "Done" if n.completed else ("Overdue" if n.is_overdue() else "Active")
            self.tree.insert('', tk.END, iid=n.id, values=(n.title, dd, n.priority, status))
    
    def _selected(self):
        sel = self.tree.selection()
        return sel[0] if sel else None
    
    def _edit(self):
        pass
    
    def _delete(self):
        pass
    
    def _add(self):
        pass
'''
    
    with open(gadget_file, 'w') as f:
        f.write(gadget_code)
    
    print(f"Gadget file created: {gadget_file}")
    print()
    print("Installation complete!")
    print()
    print("Next steps:")
    print("  1. Click the gear icon in KosDWM panel")
    print("  2. Click 'Reload Gadgets'")
    print("  3. Enable 'notices' gadget")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
