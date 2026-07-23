#!/usr/bin/env python3
"""
Notices Gadget Installation Script
==================================

Installs the notices gadget into KosDWM with automatic path detection.
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'


def print_status(msg, status="info"):
    """Print colored status message."""
    if status == "success":
        print(f"{Colors.GREEN}✓{Colors.RESET} {msg}")
    elif status == "error":
        print(f"{Colors.RED}✗{Colors.RESET} {msg}")
    elif status == "warning":
        print(f"{Colors.YELLOW}⚠{Colors.RESET} {msg}")
    else:
        print(f"{Colors.BLUE}ℹ{Colors.RESET} {msg}")


def find_kosdwm():
    """Find KosDWM installation."""
    home = Path.home()
    
    # Check environment variable
    if 'KOSDWM_HOME' in os.environ:
        path = Path(os.environ['KOSDWM_HOME'])
        if (path / "src" / "gadgets.py").exists():
            return path
    
    # Check common locations
    locations = [
        home / "adata2" / "OurAI" / "playground" / "KosDWM",
        home / "KosDWM",
        home / "projects" / "KosDWM",
        Path("/usr/local/share/KosDWM"),
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


def install():
    """Main installation."""
    print(f"{Colors.BLUE}╔══════════════════════════════════════════════════════════════╗{Colors.RESET}")
    print(f"{Colors.BLUE}║     NOTICES GADGET INSTALLER                                 ║{Colors.RESET}")
    print(f"{Colors.BLUE}╚══════════════════════════════════════════════════════════════╝{Colors.RESET}")
    print()
    
    # Find KosDWM
    kosdwm = find_kosdwm()
    
    if kosdwm:
        print_status(f"Found KosDWM at: {kosdwm}", "success")
    else:
        print_status("KosDWM not found automatically", "warning")
        user_path = input("Enter KosDWM path: ").strip()
        if not user_path:
            print_status("Cancelled", "error")
            return 1
        kosdwm = Path(user_path).expanduser()
        if not (kosdwm / "src" / "gadgets.py").exists():
            print_status("Invalid KosDWM path", "error")
            return 1
    
    # Install source files
    src_dir = kosdwm / "src"
    config_dir = Path.home() / ".config" / "KosDWM"
    gadget_dir = config_dir / "gadgets"
    
    config_dir.mkdir(parents=True, exist_ok=True)
    gadget_dir.mkdir(parents=True, exist_ok=True)
    
    # Create config
    config = {
        "kosdwm_path": str(kosdwm),
        "installed_at": datetime.now().isoformat(),
        "version": "1.0.0"
    }
    
    config_file = config_dir / "notices_gadget.conf"
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    print_status(f"Created config: {config_file}", "success")
    
    # Install source files (simplified versions)
    # Copy from current directory if available
    script_dir = Path(__file__).parent
    
    source_files = ["notices_store.py", "notices_api.py", "notifications.py"]
    
    for fname in source_files:
        src = script_dir / "src" / fname
        dst = src_dir / fname
        
        if src.exists():
            # Read and copy
            with open(src, 'r') as f:
                content = f.read()
            with open(dst, 'w') as f:
                f.write(content)
            print_status(f"Installed {fname}", "success")
        else:
            print_status(f"Source not found: {src}", "warning")
    
    # Create gadget file
    gadget_file = gadget_dir / "notices.py"
    
    gadget_code = f'''#!/usr/bin/env python3
"""
Notices Gadget for KosDWM
"""

import sys
from pathlib import Path
import json

# Load config
KOSDWM_PATH = None
config_file = Path.home() / ".config" / "KosDWM" / "notices_gadget.conf"
if config_file.exists():
    with open(config_file) as f:
        cfg = json.load(f)
        KOSDWM_PATH = Path(cfg.get("kosdwm_path", ""))

if not KOSDWM_PATH or not KOSDWM_PATH.exists():
    # Fallback
    KOSDWM_PATH = Path.home() / "adata2" / "OurAI" / "playground" / "KosDWM"

sys.path.insert(0, str(KOSDWM_PATH / "src"))

from gadgets import GadgetBase

try:
    from notices_store import NoticesStore, Notice
    STORE_OK = True
except ImportError as e:
    print(f"Notices import error: {{e}}")
    STORE_OK = False

from tkinter import messagebox, ttk
import tkinter as tk
from datetime import datetime, timedelta


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
            return "📝!"
        count = self.store.get_active_count()
        return f"📝{{count}}" if count > 0 else "📝"
    
    def get_tooltip(self):
        if not self.store:
            return "Notices (Error)"
        active = self.store.get_active_count()
        overdue = len(self.store.get_overdue())
        parts = []
        if overdue > 0:
            parts.append(f"{{overdue}} overdue")
n        if active > 0:
            parts.append(f"{{active}} active")
n        return "Notices: " + ", ".join(parts) if parts else "Click to view notices"
n    \n    def get_description(self):\n        return "Manage notices and reminders"\n    \n    def on_click(self, event=None):\n        if not self.store:\n            messagebox.showerror("Error", "Store not available")\n            return\n        if self.window and self.window.winfo_exists():\n            self.window.lift()\n            return\n        self._create_window()\n    \n    def _create_window(self):\n        self.window = tk.Toplevel()\n        self.window.title("Notices Manager")\n        self.window.geometry("900x600")\n        \n        # Header\n        header = tk.Frame(self.window)\n        header.pack(fill=tk.X, padx=10, pady=10)\n        tk.Label(header, text="📋 Notices Manager", font=('Arial', 16, 'bold')).pack(side=tk.LEFT)\n        \n        # Stats\n        stats_frame = tk.Frame(self.window)\n        stats_frame.pack(fill=tk.X, padx=10)\n        stats = self.store.get_stats()\n        tk.Label(stats_frame, text=f"Total: {{stats['total']}} | Active: {{stats['active']}} | Overdue: {{stats['overdue']}}", fg='gray').pack(side=tk.LEFT)\n        \n        # Toolbar\n        toolbar = tk.Frame(self.window)\n        toolbar.pack(fill=tk.X, padx=10, pady=5)\n        tk.Button(toolbar, text="➕ New", command=self._add_notice, bg='#4a90d9', fg='white').pack(side=tk.LEFT, padx=2)\n        tk.Button(toolbar, text="✏️ Edit", command=self._edit_selected).pack(side=tk.LEFT, padx=2)\n        tk.Button(toolbar, text="✓ Complete", command=self._complete_selected, bg='#5cb85c', fg='white').pack(side=tk.LEFT, padx=2)\n        tk.Button(toolbar, text="🗑️ Delete", command=self._delete_selected, fg='red').pack(side=tk.LEFT, padx=2)\n        tk.Button(toolbar, text="🔄 Refresh", command=self._refresh).pack(side=tk.LEFT, padx=2)\n        \n        # Filter\n        filter_frame = tk.Frame(self.window)\n        filter_frame.pack(fill=tk.X, padx=10)\n        tk.Label(filter_frame, text="Filter:").pack(side=tk.LEFT)\n        self.filter_var = tk.StringVar(value="all")\n        for text, val in [("All", "all"), ("Active", "active"), ("Completed", "completed"), ("Overdue", "overdue")]:\n            tk.Radiobutton(filter_frame, text=text, variable=self.filter_var, value=val, command=self._refresh).pack(side=tk.LEFT, padx=5)\n        \n        # Search\n        search_frame = tk.Frame(self.window)\n        search_frame.pack(fill=tk.X, padx=10, pady=5)\n        tk.Label(search_frame, text="Search:").pack(side=tk.LEFT)\n        self.search_var = tk.StringVar()\n        self.search_var.trace('w', lambda *args: self._refresh())\n        tk.Entry(search_frame, textvariable=self.search_var, width=30).pack(side=tk.LEFT, padx=5)\n        \n        # Tree\n        tree_frame = tk.Frame(self.window)\n        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)\n        \n        columns = ('title', 'due_date', 'priority', 'status')\n        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings')\n        self.tree.heading('title', text='Title')\n        self.tree.heading('due_date', text='Due Date')\n        self.tree.heading('priority', text='Priority')\n        self.tree.heading('status', text='Status')\n        self.tree.column('title', width=400)\n        self.tree.column('due_date', width=150)\n        self.tree.column('priority', width=100)\n        self.tree.column('status', width=100)\n        \n        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)\n        self.tree.configure(yscrollcommand=vsb.set)\n        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)\n        vsb.pack(side=tk.RIGHT, fill=tk.Y)\n        \n        self.tree.bind('<Double-1>', lambda e: self._edit_selected())\n        \n        self._refresh()\n    \n    def _get_notices(self):\n        filt = self.filter_var.get() if self.filter_var else "all"\n        if filt == "all":\n            notices = self.store.get_all()\n        elif filt == "active":\n            notices = self.store.get_active()\n        elif filt == "completed":\n            notices = self.store.get_completed()\n        elif filt == "overdue":\n            notices = self.store.get_overdue()\n        else:\n            notices = self.store.get_all()\n        \n        search = self.search_var.get().lower() if self.search_var else ""\n        if search:\n            notices = [n for n in notices if search in n.title.lower()]\n        \n        notices.sort(key=lambda n: (n.due_date is None, n.due_date or datetime.max))\n        return notices\n    \n    def _status(self, n):\n        if n.completed:\n            return "Completed"\n        elif n.is_overdue():\n            return "Overdue"\n        elif n.is_due_today():\n            return "Due Today"\n        elif n.due_date:\n            return f"In {{(n.due_date - datetime.now()).days}} days"\n        return "No Due Date"\n    \n    def _prio(self, n):\n        return {{"high": "🔴 High", "medium": "🟡 Medium", "low": "🟢 Low"}}.get(n.priority, n.priority)\n    \n    def _refresh(self):\n        if not self.tree:\n            return\n        for item in self.tree.get_children():\n            self.tree.delete(item)\n        \n        for n in self._get_notices():\n            dd = n.due_date.strftime('%Y-%m-%d') if n.due_date else "-"\n            vals = (n.title, dd, self._prio(n), self._status(n))\n            tag = 'overdue' if n.is_overdue() else ('due_today' if n.is_due_today() else ('completed' if n.completed else 'normal'))\n            self.tree.insert('', tk.END, iid=n.id, values=vals, tags=(tag,))\n        \n        self.tree.tag_configure('overdue', foreground='#cc0000', font=('Arial', 9, 'bold'))\n        self.tree.tag_configure('due_today', foreground='#cc6600')\n        self.tree.tag_configure('completed', foreground='gray')\n    \n    def _selected(self):\n        sel = self.tree.selection()\n        return sel[0] if sel else None\n    \n    def _edit_selected(self):\n        nid = self._selected()\n        if not nid:\n            messagebox.showinfo("Select", "Select a notice to edit")\n            return\n        n = self.store.get(nid)\n        if n:\n            d = NoticeDialog(self.window, self.store, n)\n            if d.result:\n                self._refresh()\n    \n    def _complete_selected(self):\n        nid = self._selected()\n        if nid:\n            self.store.mark_completed(nid, True)\n            self._refresh()\n    \n    def _delete_selected(self):\n        nid = self._selected()\n        if nid:\n            n = self.store.get(nid)\n            if n and messagebox.askyesno("Delete", f"Delete '{{n.title}}'?"):\n                self.store.delete(nid)\n                self._refresh()\n    \n    def _add_notice(self):\n        d = NoticeDialog(self.window, self.store)\n        if d.result:\n            self._refresh()\n\n\nclass NoticeDialog:\n    def __init__(self, parent, store, notice=None):\n        self.store = store\n        self.notice = notice\n        self.result = False\n        \n        self.d = tk.Toplevel(parent)\n        self.d.title("Edit Notice" if notice else "New Notice")\n        self.d.geometry("400x350")\n        self.d.transient(parent)\n        self.d.grab_set()\n        \n        tk.Label(self.d, text="Title *", font=('Arial', 10, 'bold')).pack(anchor='w', padx=20, pady=(20,5))\n        self.title = tk.StringVar(value=notice.title if notice else "")\n        tk.Entry(self.d, textvariable=self.title, width=40).pack(fill=tk.X, padx=20)\n        \n        tk.Label(self.d, text="Content").pack(anchor='w', padx=20, pady=(10,5))\n        self.content = tk.Text(self.d, width=40, height=3)\n        self.content.pack(fill=tk.X, padx=20)\n        if notice and notice.content:\n            self.content.insert('1.0', notice.content)\n        \n        tk.Label(self.d, text="Due Date (YYYY-MM-DD)").pack(anchor='w', padx=20, pady=(10,5))\n        due = notice.due_date.strftime('%Y-%m-%d') if notice and notice.due_date else ""\n        self.due = tk.StringVar(value=due)\n        tk.Entry(self.d, textvariable=self.due, width=40).pack(fill=tk.X, padx=20)\n        \n        tk.Label(self.d, text="Priority").pack(anchor='w', padx=20, pady=(10,5))\n        f = tk.Frame(self.d)\n        f.pack(anchor='w', padx=20)\n        self.prio = tk.StringVar(value=notice.priority if notice else "medium")\n        for t, v in [(\"🔴 High\", \"high\"), (\"🟡 Medium\", \"medium\"), (\"🟢 Low\", \"low\")]:\n            tk.Radiobutton(f, text=t, variable=self.prio, value=v).pack(side=tk.LEFT, padx=5)\n        \n        if notice:\n            self.completed = tk.BooleanVar(value=notice.completed)\n            tk.Checkbutton(self.d, text="Completed\", variable=self.completed).pack(anchor='w', padx=20, pady=10)\n        \n        btn = tk.Frame(self.d)\n        btn.pack(fill=tk.X, pady=20)\n        tk.Button(btn, text="Cancel\", command=self.d.destroy, width=10).pack(side=tk.RIGHT, padx=5)\n        tk.Button(btn, text="Save\", command=self._save, bg='#4a90d9', fg='white', width=10).pack(side=tk.RIGHT, padx=5)\n        \n        parent.wait_window(self.d)\n    \n    def _save(self):\n        t = self.title.get().strip()\n        if not t:\n            messagebox.showerror("Error\", "Title required\", parent=self.d)\n            return\n        \n        c = self.content.get('1.0', tk.END).strip()\n        \n        dd = None\n        if self.due.get().strip():\n            try:\n                dd = datetime.strptime(self.due.get().strip(), '%Y-%m-%d')\n            except ValueError:\n                messagebox.showerror("Error\", "Invalid date\", parent=self.d)\n                return\n        \n        try:\n            if self.notice:\n                self.store.update(self.notice.id, title=t, content=c, due_date=dd, \n                                priority=self.prio.get(), completed=self.completed.get())\n            else:\n                self.store.create(title=t, content=c, due_date=dd, priority=self.prio.get())\n            self.result = True\n            self.d.destroy()\n        except Exception as e:\n            messagebox.showerror("Error\", str(e), parent=self.d)\n'''\n    
    with open(gadget_file, 'w') as f:
        f.write(gadget_code)
    print_status(f"Created gadget: {gadget_file}", "success")
    
    # Summary
    print()
    print_status("Installation complete!", "success")
    print()
    print("Next steps:")
    print("  1. Click ⚙️ in KosDWM panel")
    print("  2. Click 'Reload Gadgets'")
    print("  3. Enable 'notices' gadget")
    print()
    
    return 0


if __name__ == "__main__":
    sys.exit(install())
