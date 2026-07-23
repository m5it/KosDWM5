"""
Notices Gadget for KosDWM
==========================

A gadget for managing notices/reminders with due dates and priorities.
Includes HTTP API for external access and notification system.
"""

import sys
from pathlib import Path

# Add KosDWM src directory to path
# Path from ~/.config/KosDWM/gadgets/ to actual KosDWM installation
sys.path.insert(0, str(Path.home() / "adata2" / "OurAI" / "playground" / "KosDWM" / "src"))

from gadgets import GadgetBase

# Try to import notices modules, handle if not available
try:
    from notices_store import NoticesStore, Notice
    STORE_AVAILABLE = True
except ImportError as e:
    print(f"Notices: notices_store not available: {e}")
    STORE_AVAILABLE = False

try:
    from notices_api import NoticesAPIServer
    API_AVAILABLE = True
except ImportError as e:
    print(f"Notices: notices_api not available: {e}")
    API_AVAILABLE = False

try:
    from notifications import ReminderThread, NotificationSettingsDialog, ReminderSettings
    NOTIFICATIONS_AVAILABLE = True
except ImportError as e:
    print(f"Notices: notifications not available: {e}")
    NOTIFICATIONS_AVAILABLE = False

from tkinter import messagebox, simpledialog, ttk
import tkinter as tk
from datetime import datetime, timedelta
import threading
import time


class NoticesGadget(GadgetBase):
    """
    A gadget for managing notices and reminders with HTTP API and notification support.
    """
    
    # Default API port
    API_PORT = 5000
    
    def __init__(self):
        super().__init__()
        
        # Check if store is available
        if not STORE_AVAILABLE:
            self.error_message = "Notices store not available"
            self.store = None
        else:
            self.store = NoticesStore()
            self.error_message = None
        
        self.window = None
        self.refresh_timer = None
        self.api_server = None
        self.api_running = False
        self.api_lock = threading.Lock()
        
        # Notification system
        self.reminder_settings = None
        self.reminder_thread = None
        self.notification_alert = False
        
        # GUI state
        self.search_var = None
        self.sort_var = None
        self.filter_var = None
        self.tree = None
        
        if self.store:
            # Start the API server
            self._start_api_server()
            
            # Start the reminder thread
            self._start_reminder_thread()
            
            # Start refresh timer
            self._start_refresh_timer()
    
    def _start_api_server(self):
        """Start the HTTP API server."""
        if not API_AVAILABLE or not self.store:
            return
            
        try:
            with self.api_lock:
                if self.api_server is None:
                    self.api_server = NoticesAPIServer(
                        store=self.store,
                        port=self.API_PORT
                    )
                    self.api_running = self.api_server.start(threaded=True)
                    if self.api_running:
                        print(f"Notices API started on port {self.API_PORT}")
        except Exception as e:
            print(f"Failed to start API server: {e}")
            self.api_running = False
    
    def _stop_api_server(self):
        """Stop the HTTP API server."""
        with self.api_lock:
            if self.api_server:
                self.api_server.stop()
                self.api_running = False
                print("Notices API stopped")
    
    def _start_reminder_thread(self):
        """Start the reminder notification thread."""
        if not NOTIFICATIONS_AVAILABLE or not self.store:
            return
            
        if self.reminder_thread is None or not getattr(self.reminder_thread, '_running', False):
            self.reminder_settings = ReminderSettings()
            self.reminder_thread = ReminderThread(
                notices_store=self.store,
                on_reminder=self._on_reminder_triggered,
                settings=self.reminder_settings
            )
            self.reminder_thread.start()
            print("Reminder thread started")
    
    def _stop_reminder_thread(self):
        """Stop the reminder notification thread."""
        if self.reminder_thread:
            self.reminder_thread.stop()
            self.reminder_thread = None
            print("Reminder thread stopped")
    
    def _on_reminder_triggered(self, notice_id: str, title: str, content: str):
        """Callback when a reminder is triggered."""
        print(f"Reminder triggered: {title}")
        
        # Set visual alert
        self.notification_alert = True
        
        # Show popup if window exists
        if self.window and self.window.winfo_exists():
            self.window.after(0, lambda: self._show_reminder_popup(
                notice_id, title, content
            ))
    
    def _show_reminder_popup(self, notice_id: str, title: str, content: str):
        """Show a reminder popup notification."""
        if self.reminder_thread:
            self.reminder_thread.show_popup(notice_id, title, content, self.window)
    
    def _start_refresh_timer(self):
        """Start a timer to refresh the badge count periodically."""
        if not self.store:
            return
            
        def refresh_loop():
            while True:
                time.sleep(60)  # Refresh every minute
                if self.window and self.window.winfo_exists():
                    try:
                        self.window.after(0, self._refresh_list)
                    except:
                        pass
        
        self.refresh_timer = threading.Thread(target=refresh_loop, daemon=True)
        self.refresh_timer.start()
    
    def get_name(self) -> str:
        return "notices"
    
    def get_icon(self) -> str:
        """Return icon with badge count if there are active notices."""
        if not self.store:
            return "📝!"
        
        active_count = self.store.get_active_count()
        
        # Show alert indicator if notifications are pending
        if self.notification_alert:
            if active_count > 0:
                return f"🔔{active_count}"
            return "🔔"
        
        if active_count > 0:
            return f"📝{active_count}"
        return "📝"
    
    def get_tooltip(self) -> str:
        if not self.store:
            return "Notices (Error: Store not available)"
        
        active = self.store.get_active_count()
        overdue = len(self.store.get_overdue())
        due_today = len(self.store.get_due_today())
        
        parts = []
        if overdue > 0:
            parts.append(f"{overdue} overdue")
        if due_today > 0:
            parts.append(f"{due_today} due today")
        if active > 0:
            parts.append(f"{active} active")
        
        api_status = "API: ON" if self.api_running else "API: OFF"
        
        if self.notification_alert:
            parts.insert(0, "🔔 Reminder!")
        
        if parts:
            return f"Notices ({api_status}): " + ", ".join(parts)
        return f"Click to view notices ({api_status})"
    
    def get_description(self) -> str:
        if not self.store:
            return "Notices gadget - ERROR: Store module not available. Check that notices_store.py is in the src directory."
        return "Manage notices and reminders with due dates, priorities, HTTP API, and notifications."
    
    def on_click(self, event=None):
        """Open the notices window."""
        if not self.store:
            messagebox.showerror(
                "Error",
                "Notices store not available.\n\nPlease ensure notices_store.py is in the KosDWM src directory."
            )
            return
        
        # Clear notification alert when user opens the window
        self.notification_alert = False
        
        if self.window and self.window.winfo_exists():
            self.window.lift()
            return
        
        self._create_window()
    
    def _create_window(self):
        """Create the main notices window with comprehensive GUI."""
        if not self.store:
            return
            
        self.window = tk.Toplevel()
        self.window.title("Notices Manager")
        self.window.geometry("900x600")
        self.window.resizable(True, True)
        
        # Header frame
        header_frame = tk.Frame(self.window)
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            header_frame,
            text="📋 Notices Manager",
            font=('Arial', 16, 'bold')
        ).pack(side=tk.LEFT)
        
        # API Status indicator
        api_frame = tk.Frame(header_frame)
        api_frame.pack(side=tk.RIGHT)
        
        api_color = 'green' if self.api_running else 'red'
        api_text = "● API Online" if self.api_running else "● API Offline"
        self.api_status_label = tk.Label(
            api_frame,
            text=api_text,
            fg=api_color,
            font=('Arial', 9, 'bold')
        )
        self.api_status_label.pack(side=tk.RIGHT)
        
        # API URL display
        if self.api_running:
            self.api_url_label = tk.Label(
                api_frame,
                text=f"http://localhost:{self.API_PORT}",
                fg='gray',
                font=('Arial', 8)
            )
            self.api_url_label.pack(side=tk.RIGHT, padx=(0, 10))
        
        # Stats label
        stats_frame = tk.Frame(self.window)
        stats_frame.pack(fill=tk.X, padx=10, pady=(0, 5))
        
        stats = self.store.get_stats()
        self.stats_label = tk.Label(
            stats_frame, 
            text=f"Total: {stats['total']} | Active: {stats['active']} | Overdue: {stats['overdue']} | Due Today: {stats['due_today']}",
            fg='gray',
            font=('Arial', 10)
        )
        self.stats_label.pack(side=tk.LEFT)
        
        # Settings buttons frame
        settings_frame = tk.Frame(stats_frame)
        settings_frame.pack(side=tk.RIGHT)
        
        if NOTIFICATIONS_AVAILABLE:
            tk.Button(
                settings_frame,
                text="🔔 Notification Settings",
                command=self._show_notification_settings,
                font=('Arial', 9)
            ).pack(side=tk.RIGHT, padx=2)
        
        tk.Button(
            settings_frame,
            text="API Info",
            command=self._show_api_info,
            font=('Arial', 9)
        ).pack(side=tk.RIGHT, padx=2)
        
        # Search bar
        search_frame = tk.Frame(self.window)
        search_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(search_frame, text="🔍 Search:", font=('Arial', 10)).pack(side=tk.LEFT)
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', lambda *args: self._refresh_list())
        search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            search_frame,
            text="Clear",
            command=lambda: self.search_var.set(""),
            font=('Arial', 9)
        ).pack(side=tk.LEFT)
        
        # Toolbar with action buttons
        toolbar = tk.Frame(self.window)
        toolbar.pack(fill=tk.X, padx=10, pady=5)
        
        btn_style = {'font': ('Arial', 10), 'padx': 10, 'pady': 3}
        
        tk.Button(
            toolbar,
            text="➕ New Notice",
            command=self._add_notice,
            bg='#4a90d9',
            fg='white',
            **btn_style
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        tk.Button(
            toolbar,
            text="✏️ Edit",
            command=self._edit_selected_notice,
            **btn_style
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            toolbar,
            text="✓ Complete",
            command=self._complete_selected_notice,
            bg='#5cb85c',
            fg='white',
            **btn_style
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            toolbar,
            text="🗑️ Delete",
            command=self._delete_selected_notice,
            fg='red',
            **btn_style
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            toolbar,
            text="🔄 Refresh",
            command=self._refresh_list,
            **btn_style
        ).pack(side=tk.LEFT, padx=5)
        
        # Filter and Sort frame
        control_frame = tk.Frame(self.window)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Filter options
        tk.Label(control_frame, text="Filter:", font=('Arial', 10)).pack(side=tk.LEFT)
        
        self.filter_var = tk.StringVar(value="all")
        self.filter_var.trace('w', lambda *args: self._refresh_list())
        
        filter_options = [
            ("All", "all"),
            ("Active", "active"),
            ("Completed", "completed"),
            ("Overdue", "overdue"),
            ("Due Today", "due_today")
        ]
        
        for text, value in filter_options:
            tk.Radiobutton(
                control_frame,
                text=text,
                variable=self.filter_var,
                value=value,
                font=('Arial', 9)
            ).pack(side=tk.LEFT, padx=5)
        
        # Sort options
        tk.Label(control_frame, text="Sort by:", font=('Arial', 10)).pack(side=tk.LEFT, padx=(20, 5))
        
        self.sort_var = tk.StringVar(value="due_date")
        self.sort_var.trace('w', lambda *args: self._refresh_list())
        
        sort_options = [
            ("Due Date", "due_date"),
            ("Priority", "priority"),
            ("Created Date", "created_date"),
            ("Title", "title")
        ]
        
        for text, value in sort_options:
            tk.Radiobutton(
                control_frame,
                text=text,
                variable=self.sort_var,
                value=value,
                font=('Arial', 9)
            ).pack(side=tk.LEFT, padx=5)
        
        # Treeview for notices list
        tree_frame = tk.Frame(self.window)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Create treeview with scrollbars
        columns = ('title', 'due_date', 'priority', 'status')
        self.tree = ttk.Treeview(
            tree_frame,
            columns=columns,
            show='headings',
            selectmode='browse'
        )
        
        # Define column headings
        self.tree.heading('title', text='Title')
        self.tree.heading('due_date', text='Due Date')
        self.tree.heading('priority', text='Priority')
        self.tree.heading('status', text='Status')
        
        # Define column widths
        self.tree.column('title', width=350, minwidth=200)
        self.tree.column('due_date', width=150, minwidth=100)
        self.tree.column('priority', width=80, minwidth=60)
        self.tree.column('status', width=100, minwidth=80)
        
        # Add scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        self.tree.grid(column=0, row=0, sticky='nsew')
        vsb.grid(column=1, row=0, sticky='ns')
        hsb.grid(column=0, row=1, sticky='ew')
        
        tree_frame.grid_columnconfigure(0, weight=1)
        tree_frame.grid_rowconfigure(0, weight=1)
        
        # Bind double-click to edit
        self.tree.bind('<Double-1>', lambda e: self._edit_selected_notice())
        
        # Bind selection change
        self.tree.bind('<<TreeviewSelect>>', self._on_select)
        
        # Status bar
        self.status_bar = tk.Label(
            self.window,
            text="Ready",
            bd=1,
            relief=tk.SUNKEN,
            anchor=tk.W,
            font=('Arial', 9)
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        self._refresh_list()
    
    def _on_select(self, event=None):
        """Handle treeview selection change."""
        selected = self.tree.selection()
        if selected:
            item = self.tree.item(selected[0])
            self.status_bar.config(text=f"Selected: {item['values'][0]}")
    
    def _get_filtered_and_sorted_notices(self) -> list:
        """Get notices based on current filter, search, and sort."""
        if not self.store:
            return []
            
        # Get base list based on filter
        filter_val = self.filter_var.get() if self.filter_var else "all"
        
        if filter_val == "all":
            notices = self.store.get_all()
        elif filter_val == "active":
            notices = self.store.get_active()
        elif filter_val == "completed":
            notices = self.store.get_completed()
        elif filter_val == "overdue":
            notices = self.store.get_overdue()
        elif filter_val == "due_today":
            notices = self.store.get_due_today()
        else:
            notices = self.store.get_all()
        
        # Apply search filter
        search_text = self.search_var.get().lower() if self.search_var else ""
        if search_text:
            notices = [
                n for n in notices 
                if search_text in n.title.lower() 
                or search_text in n.content.lower()
            ]
        
        # Apply sorting
        sort_val = self.sort_var.get() if self.sort_var else "due_date"
        
        if sort_val == "due_date":
            notices.sort(key=lambda n: (n.due_date is None, n.due_date or datetime.max))
        elif sort_val == "priority":
            priority_order = {"high": 0, "medium": 1, "low": 2}
            notices.sort(key=lambda n: priority_order.get(n.priority, 1))
        elif sort_val == "created_date":
            notices.sort(key=lambda n: n.created_date, reverse=True)
        elif sort_val == "title":
            notices.sort(key=lambda n: n.title.lower())
        
        return notices
    
    def _get_status_text(self, notice) -> str:
        """Get status text for a notice."""
        if notice.completed:
            return "Completed"
        elif hasattr(notice, 'is_overdue') and notice.is_overdue():
            return "Overdue"
        elif hasattr(notice, 'is_due_today') and notice.is_due_today():
            return "Due Today"
        elif notice.due_date:
            days = (notice.due_date - datetime.now()).days
            return f"In {days} days"
        return "No Due Date"
    
    def _get_priority_text(self, notice) -> str:
        """Get priority text with indicator."""
        indicators = {"high": "🔴 High", "medium": "🟡 Medium", "low": "🟢 Low"}
        return indicators.get(notice.priority, notice.priority.capitalize())
    
    def _get_due_date_text(self, notice) -> str:
        """Get formatted due date text."""
        if not notice.due_date:
            return "-"
        
        days_until = (notice.due_date - datetime.now()).days
        date_str = notice.due_date.strftime('%Y-%m-%d')
        
        if days_until < 0:
            return f"{date_str} ({abs(days_until)} days ago)"
        elif days_until == 0:
            return f"{date_str} (Today)"
        elif days_until == 1:
            return f"{date_str} (Tomorrow)"
        else:
            return f"{date_str} (in {days_until} days)"
    
    def _refresh_list(self):
        """Refresh the notices treeview."""
        if not self.tree or not self.store:
            return
        
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        notices = self._get_filtered_and_sorted_notices()
        
        # Insert notices with color tags
        for notice in notices:
            status = self._get_status_text(notice)
            
            values = (
                notice.title,
                self._get_due_date_text(notice),
                self._get_priority_text(notice),
                status
            )
            
            # Determine tag based on status
            if notice.completed:
                tag = 'completed'
            elif hasattr(notice, 'is_overdue') and notice.is_overdue():
                tag = 'overdue'
            elif hasattr(notice, 'is_due_today') and notice.is_due_today():
                tag = 'due_today'
            else:
                tag = 'normal'
            
            self.tree.insert('', tk.END, iid=notice.id, values=values, tags=(tag,))
        
        # Configure tags for color coding
        self.tree.tag_configure('completed', foreground='gray')
        self.tree.tag_configure('overdue', foreground='#cc0000', font=('Arial', 9, 'bold'))
        self.tree.tag_configure('due_today', foreground='#cc6600', font=('Arial', 9, 'bold'))
        self.tree.tag_configure('normal', foreground='black')
        
        # Update stats
        stats = self.store.get_stats()
        if hasattr(self, 'stats_label'):
            self.stats_label.config(
                text=f"Total: {stats['total']} | Active: {stats['active']} | Overdue: {stats['overdue']} | Due Today: {stats['due_today']}"
            )
        
        # Update status bar
        if hasattr(self, 'status_bar'):
            self.status_bar.config(text=f"Showing {len(notices)} notices")
    
    def _get_selected_notice_id(self) -> str:
        """Get the ID of the selected notice."""
        selected = self.tree.selection()
        if selected:
            return selected[0]
        return None
    
    def _edit_selected_notice(self):
        """Edit the selected notice."""
        notice_id = self._get_selected_notice_id()
        if not notice_id:
            messagebox.showinfo("Select Notice", "Please select a notice to edit.")
            return
        
        notice = self.store.get(notice_id)
        if notice:
            dialog = NoticeDialog(self.window, self.store, notice)
            if dialog.result:
                self._refresh_list()
    
    def _complete_selected_notice(self):
        """Mark the selected notice as completed."""
        notice_id = self._get_selected_notice_id()
        if not notice_id:
            messagebox.showinfo("Select Notice", "Please select a notice to complete.")
            return
        
        notice = self.store.get(notice_id)
        if notice:
            if notice.completed:
                messagebox.showinfo("Already Completed", "This notice is already completed.")
            else:
                self.store.mark_completed(notice_id, True)
                self._refresh_list()
                self.status_bar.config(text=f"Marked '{notice.title}' as completed")
    
    def _delete_selected_notice(self):
        """Delete the selected notice."""
        notice_id = self._get_selected_notice_id()
        if not notice_id:
            messagebox.showinfo("Select Notice", "Please select a notice to delete.")
            return
        
        notice = self.store.get(notice_id)
        if notice:
            if messagebox.askyesno(
                "Confirm Delete",
                f"Are you sure you want to delete '{notice.title}'?",
                icon='warning'
            ):
                self.store.delete(notice_id)
                self._refresh_list()
                self.status_bar.config(text=f"Deleted '{notice.title}'")
    
    def _show_api_info(self):
        """Show API information dialog."""
        info = tk.Toplevel(self.window)
        info.title("API Information")
        info.geometry("450x350")
        info.resizable(False, False)
        info.transient(self.window)
        
        tk.Label(
            info,
            text="Notices HTTP API",
            font=('Arial', 14, 'bold')
        ).pack(pady=15)
        
        status_frame = tk.Frame(info)
        status_frame.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(status_frame, text="Status:", font=('Arial', 10)).pack(side=tk.LEFT)
        status_text = "Running" if self.api_running else "Stopped"
        status_color = "green" if self.api_running else "red"
        tk.Label(status_frame, text=status_text, fg=status_color, 
                font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        
        tk.Label(info, text=f"Port: {self.API_PORT}", font=('Arial', 10)).pack(anchor='w', padx=20)
        tk.Label(info, text=f"Base URL: http://localhost:{self.API_PORT}", 
                font=('Arial', 10)).pack(anchor='w', padx=20)
        
        tk.Label(info, text="Available Endpoints:", 
                font=('Arial', 11, 'bold')).pack(anchor='w', padx=20, pady=(20, 10))
        
        endpoints_frame = tk.Frame(info)
        endpoints_frame.pack(fill=tk.X, padx=20)
        
        endpoints = [
            ("GET", "/api/notices", "List all notices"),
            ("GET", "/api/notices/<id>", "Get single notice"),
            ("POST", "/api/notices", "Create new notice"),
            ("PUT", "/api/notices/<id>", "Update notice"),
            ("DELETE", "/api/notices/<id>", "Delete notice"),
            ("POST", "/api/notices/<id>/complete", "Mark complete"),
            ("GET", "/api/notices/stats", "Get statistics")
        ]
        
        for method, path, desc in endpoints:
            row = tk.Frame(endpoints_frame)
            row.pack(fill=tk.X, pady=1)
            tk.Label(row, text=method, fg='#4a90d9', 
                    font=('Arial', 9, 'bold'), width=6).pack(side=tk.LEFT)
            tk.Label(row, text=path, font=('Courier', 9), width=25).pack(side=tk.LEFT)
            tk.Label(row, text=desc, font=('Arial', 9), fg='gray').pack(side=tk.LEFT)
        
        tk.Button(info, text="Close", command=info.destroy, width=10).pack(pady=20)
    
    def _show_notification_settings(self):
        """Show notification settings dialog."""
        if not NOTIFICATIONS_AVAILABLE:
            messagebox.showinfo("Not Available", "Notification system not available.")
            return
            
        dialog = NotificationSettingsDialog(self.window, self.reminder_settings)
        if dialog.result:
            # Restart reminder thread with new settings
            self._stop_reminder_thread()
            self._start_reminder_thread()
    
    def _add_notice(self):
        """Open dialog to add new notice."""
        dialog = NoticeDialog(self.window, self.store)
        if dialog.result:
            self._refresh_list()
    
    def _edit_notice(self, notice_id: str):
        """Open dialog to edit notice."""
        notice = self.store.get(notice_id)
        if notice:
            dialog = NoticeDialog(self.window, self.store, notice)
            if dialog.result:
                self._refresh_list()
    
    def _delete_notice(self, notice_id: str):
        """Delete a notice after confirmation."""
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this notice?"):
            self.store.delete(notice_id)
            self._refresh_list()
    
    def _complete_notice(self, notice_id: str):
        """Mark notice as completed."""
        self.store.mark_completed(notice_id, True)
        self._refresh_list()


class NoticeDialog:
    """Dialog for adding/editing notices with comprehensive form."""
    
    def __init__(self, parent, store, notice=None):
        self.store = store
        self.notice = notice
        self.result = False
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Edit Notice" if notice else "New Notice")
        self.dialog.geometry("450x450")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self._create_form()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (450 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (450 // 2)
        self.dialog.geometry(f'+{x}+{y}')
        
        # Wait for dialog to close
        parent.wait_window(self.dialog)
    
    def _create_form(self):
        """Create the form fields."""
        pad = {'padx': 20, 'pady': 8}
        
        # Title
        tk.Label(self.dialog, text="Title *", font=('Arial', 10, 'bold')).pack(anchor='w', **pad)
        self.title_var = tk.StringVar(value=self.notice.title if self.notice else "")
        tk.Entry(self.dialog, textvariable=self.title_var, width=50, font=('Arial', 10)).pack(fill=tk.X, **pad)
        
        # Content
        tk.Label(self.dialog, text="Content", font=('Arial', 10)).pack(anchor='w', **pad)
        content_frame = tk.Frame(self.dialog)
        content_frame.pack(fill=tk.X, **pad)
        
        self.content_text = tk.Text(content_frame, width=50, height=4, font=('Arial', 10))
        self.content_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        if self.notice and self.notice.content:
            self.content_text.insert('1.0', self.notice.content)
        
        content_scroll = tk.Scrollbar(content_frame, command=self.content_text.yview)
        content_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.content_text.config(yscrollcommand=content_scroll.set)
        
        # Due Date
        tk.Label(self.dialog, text="Due Date (YYYY-MM-DD)", font=('Arial', 10)).pack(anchor='w', **pad)
        due_date_str = ""
        if self.notice and self.notice.due_date:
            due_date_str = self.notice.due_date.strftime('%Y-%m-%d')
        self.due_date_var = tk.StringVar(value=due_date_str)
        tk.Entry(self.dialog, textvariable=self.due_date_var, width=50, font=('Arial', 10)).pack(fill=tk.X, **pad)
        
        # Reminder Time
        tk.Label(self.dialog, text="Reminder Time (YYYY-MM-DD HH:MM)", font=('Arial', 10)).pack(anchor='w', **pad)
        reminder_str = ""
        if self.notice and self.notice.reminder_time:
            reminder_str = self.notice.reminder_time.strftime('%Y-%m-%d %H:%M')
        self.reminder_var = tk.StringVar(value=reminder_str)
        tk.Entry(self.dialog, textvariable=self.reminder_var, width=50, font=('Arial', 10)).pack(fill=tk.X, **pad)
        
        # Priority
        tk.Label(self.dialog, text="Priority", font=('Arial', 10)).pack(anchor='w', **pad)
        priority_frame = tk.Frame(self.dialog)
        priority_frame.pack(anchor='w', **pad)
        
        self.priority_var = tk.StringVar(value=self.notice.priority if self.notice else "medium")
        
        priorities = [
            ("🔴 High", "high", '#ffe6e6'),
            ("🟡 Medium", "medium", '#fff3e6'),
            ("🟢 Low", "low", '#e6f7ff')
        ]
        
        for text, value, color in priorities:
            rb = tk.Radiobutton(
                priority_frame,
                text=text,
                variable=self.priority_var,
                value=value,
                font=('Arial', 10)
            )
            rb.pack(side=tk.LEFT, padx=10)
        
        # Completed checkbox (only for edit)
        if self.notice:
            self.completed_var = tk.BooleanVar(value=self.notice.completed)
            tk.Checkbutton(
                self.dialog,
                text="Mark as completed",
                variable=self.completed_var,
                font=('Arial', 10)
            ).pack(anchor='w', **pad)
        
        # Buttons
        btn_frame = tk.Frame(self.dialog)
        btn_frame.pack(fill=tk.X, pady=20)
        
        tk.Button(
            btn_frame,
            text="Cancel",
            command=self.dialog.destroy,
            width=12,
            font=('Arial', 10)
        ).pack(side=tk.RIGHT, padx=5)
        
        tk.Button(
            btn_frame,
            text="Save Notice",
            command=self._save,
            bg='#4a90d9',
            fg='white',
            width=12,
            font=('Arial', 10)
        ).pack(side=tk.RIGHT, padx=5)
    
    def _save(self):
        """Save the notice."""
        title = self.title_var.get().strip()
        if not title:
            messagebox.showerror("Error", "Title is required", parent=self.dialog)
            return
        
        content = self.content_text.get('1.0', tk.END).strip()
        
        # Parse due date
        due_date = None
        due_date_str = self.due_date_var.get().strip()
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
            except ValueError:
                messagebox.showerror("Error", "Invalid due date format. Use YYYY-MM-DD", parent=self.dialog)
                return
        
        # Parse reminder
        reminder_time = None
        reminder_str = self.reminder_var.get().strip()
        if reminder_str:
            try:
                reminder_time = datetime.strptime(reminder_str, '%Y-%m-%d %H:%M')
            except ValueError:
                messagebox.showerror("Error", "Invalid reminder format. Use YYYY-MM-DD HH:MM", parent=self.dialog)
                return
        
        priority = self.priority_var.get()
        
        try:
            if self.notice:
                # Update existing
                self.store.update(
                    self.notice.id,
                    title=title,
                    content=content,
                    due_date=due_date,
                    reminder_time=reminder_time,
                    priority=priority,
                    completed=self.completed_var.get()
                )
            else:
                # Create new
                self.store.create(
                    title=title,
                    content=content,
                    due_date=due_date,
                    reminder_time=reminder_time,
                    priority=priority
                )
            
            self.result = True
            self.dialog.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save notice: {str(e)}", parent=self.dialog)
