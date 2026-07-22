"""
Notifications System for Notices
================================

Handles reminder notifications with:
- Periodic checking for due reminders
- Popup notifications with tkinter
- Sound alerts and visual indicators
- Snooze functionality
- Dismissed reminder tracking
- Configurable settings
"""

import threading
import time
import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
from typing import Optional, Set, Dict, Any, Callable
from pathlib import Path
import json
import os

# Try to import sound playing capability
try:
    import subprocess
    SOUND_AVAILABLE = True
except ImportError:
    SOUND_AVAILABLE = False


class ReminderSettings:
    """
    Manages notification settings with persistence.
    """
    
    SETTINGS_FILE = Path.home() / ".config" / "KosDWM" / "reminder_settings.json"
    
    DEFAULTS = {
        "enabled": True,
        "play_sound": True,
        "sound_command": "paplay /usr/share/sounds/freedesktop/stereo/message.oga",
        "notification_duration": 10,  # seconds
        "snooze_times": [5, 15, 30],  # minutes
        "max_notifications": 5,  # max simultaneous popups
        "check_interval": 60,  # seconds
    }
    
    def __init__(self):
        self._settings = {}
        self._lock = threading.Lock()
        self._ensure_directory()
        self._load()
    
    def _ensure_directory(self):
        """Ensure the config directory exists."""
        self.SETTINGS_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    def _load(self):
        """Load settings from file."""
        if self.SETTINGS_FILE.exists():
            try:
                with open(self.SETTINGS_FILE, 'r') as f:
                    self._settings = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading reminder settings: {e}")
                self._settings = self.DEFAULTS.copy()
        else:
            self._settings = self.DEFAULTS.copy()
            self._save()
    
    def _save(self):
        """Save settings to file."""
        try:
            with open(self.SETTINGS_FILE, 'w') as f:
                json.dump(self._settings, f, indent=2)
        except IOError as e:
            print(f"Error saving reminder settings: {e}")
    
    def get(self, key: str, default=None):
        """Get a setting value."""
        with self._lock:
            return self._settings.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set a setting value."""
        with self._lock:
            self._settings[key] = value
            self._save()
    
    def update(self, **kwargs):
        """Update multiple settings."""
        with self._lock:
            self._settings.update(kwargs)
            self._save()
    
    def get_all(self) -> Dict[str, Any]:
        """Get all settings."""
        with self._lock:
            return self._settings.copy()


class NotificationPopup:
    """
    A popup notification window for reminders.
    """
    
    def __init__(self, notice_id: str, title: str, message: str, 
                 settings: ReminderSettings,
                 on_complete: Optional[Callable] = None,
                 on_snooze: Optional[Callable] = None,
                 on_dismiss: Optional[Callable] = None):
        self.notice_id = notice_id
        self.title = title
        self.message = message
        self.settings = settings
        self.on_complete = on_complete
        self.on_snooze = on_snooze
        self.on_dismiss = on_dismiss
        
        self.window = None
        self.remaining_time = settings.get("notification_duration", 10)
        self.timer_id = None
        
        self._create_window()
    
    def _create_window(self):
        """Create the notification popup window."""
        self.window = tk.Toplevel()
        self.window.title("Reminder")
        self.window.geometry("400x200")
        self.window.resizable(False, False)
        
        # Make window stay on top
        self.window.attributes('-topmost', True)
        
        # Center on screen
        self.window.update_idletasks()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        x = (self.window.winfo_screenwidth() // 2) - (width // 2)
        y = (self.window.winfo_screenheight() // 2) - (height // 2)
        self.window.geometry(f'+{x}+{y}')
        
        # Header with icon
        header = tk.Frame(self.window, bg='#4a90d9', padx=10, pady=10)
        header.pack(fill=tk.X)
        
        tk.Label(
            header,
            text="⏰ Reminder",
            font=('Arial', 14, 'bold'),
            fg='white',
            bg='#4a90d9'
        ).pack(side=tk.LEFT)
        
        # Auto-close timer label
        self.timer_label = tk.Label(
            header,
            text=f"Auto-close in {self.remaining_time}s",
            fg='white',
            bg='#4a90d9',
            font=('Arial', 9)
        )
        self.timer_label.pack(side=tk.RIGHT)
        
        # Content
        content = tk.Frame(self.window, padx=20, pady=15)
        content.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            content,
            text=self.title,
            font=('Arial', 12, 'bold'),
            wraplength=360
        ).pack(anchor='w', pady=(0, 5))
        
        if self.message:
            tk.Label(
                content,
                text=self.message,
                font=('Arial', 10),
                wraplength=360,
                fg='gray'
            ).pack(anchor='w')
        
        # Snooze options
        snooze_frame = tk.LabelFrame(self.window, text="Snooze", padx=10, pady=5)
        snooze_frame.pack(fill=tk.X, padx=20, pady=5)
        
        snooze_times = self.settings.get("snooze_times", [5, 15, 30])
        for minutes in snooze_times:
            tk.Button(
                snooze_frame,
                text=f"{minutes} min",
                command=lambda m=minutes: self._snooze(m),
                width=8
            ).pack(side=tk.LEFT, padx=5)
        
        # Action buttons
        btn_frame = tk.Frame(self.window, pady=10)
        btn_frame.pack(fill=tk.X, padx=20)
        
        tk.Button(
            btn_frame,
            text="Dismiss",
            command=self._dismiss,
            width=10
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            btn_frame,
            text="Complete",
            command=self._complete,
            bg='#4a90d9',
            fg='white',
            width=10
        ).pack(side=tk.RIGHT, padx=5)
        
        # Handle window close
        self.window.protocol("WM_DELETE_WINDOW", self._dismiss)
        
        # Start auto-close timer
        self._start_timer()
    
    def _start_timer(self):
        """Start the auto-close countdown."""
        if self.remaining_time > 0:
            self.timer_label.config(text=f"Auto-close in {self.remaining_time}s")
            self.remaining_time -= 1
            self.timer_id = self.window.after(1000, self._start_timer)
        else:
            self._dismiss()
    
    def _snooze(self, minutes: int):
        """Snooze the reminder."""
        if self.timer_id:
            self.window.after_cancel(self.timer_id)
        
        self.window.destroy()
        
        if self.on_snooze:
            self.on_snooze(self.notice_id, minutes)
    
    def _dismiss(self):
        """Dismiss the reminder."""
        if self.timer_id:
            self.window.after_cancel(self.timer_id)
        
        self.window.destroy()
        
        if self.on_dismiss:
            self.on_dismiss(self.notice_id)
    
    def _complete(self):
        """Mark the notice as complete."""
        if self.timer_id:
            self.window.after_cancel(self.timer_id)
        
        self.window.destroy()
        
        if self.on_complete:
            self.on_complete(self.notice_id)
    
    def close(self):
        """Force close the popup."""
        if self.window and self.window.winfo_exists():
            if self.timer_id:
                self.window.after_cancel(self.timer_id)
            self.window.destroy()


class DismissedReminders:
    """
    Tracks dismissed reminders to avoid duplicates.
    """
    
    DISMISSED_FILE = Path.home() / ".config" / "KosDWM" / "dismissed_reminders.json"
    
    def __init__(self):
        self._dismissed: Dict[str, str] = {}  # notice_id -> dismissed_time
        self._lock = threading.Lock()
        self._ensure_directory()
        self._load()
        self._cleanup_old()
    
    def _ensure_directory(self):
        """Ensure the config directory exists."""
        self.DISMISSED_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    def _load(self):
        """Load dismissed reminders from file."""
        if self.DISMISSED_FILE.exists():
            try:
                with open(self.DISMISSED_FILE, 'r') as f:
                    self._dismissed = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading dismissed reminders: {e}")
                self._dismissed = {}
    
    def _save(self):
        """Save dismissed reminders to file."""
        try:
            with open(self.DISMISSED_FILE, 'w') as f:
                json.dump(self._dismissed, f, indent=2)
        except IOError as e:
            print(f"Error saving dismissed reminders: {e}")
    
    def _cleanup_old(self):
        """Remove entries older than 24 hours."""
        cutoff = (datetime.now() - timedelta(hours=24)).isoformat()
        with self._lock:
            self._dismissed = {
                k: v for k, v in self._dismissed.items() 
                if v > cutoff
            }
            self._save()
    
    def is_dismissed(self, notice_id: str) -> bool:
        """Check if a reminder has been dismissed."""
        with self._lock:
            return notice_id in self._dismissed
    
    def dismiss(self, notice_id: str):
        """Mark a reminder as dismissed."""
        with self._lock:
            self._dismissed[notice_id] = datetime.now().isoformat()
            self._save()
    
    def clear(self, notice_id: str):
        """Clear dismissed status for a reminder."""
        with self._lock:
            if notice_id in self._dismissed:
                del self._dismissed[notice_id]
                self._save()
    
    def clear_all(self):
        """Clear all dismissed reminders."""
        with self._lock:
            self._dismissed.clear()
            self._save()


class ReminderThread(threading.Thread):
    """
    Background thread that checks for due reminders.
    """
    
    def __init__(self, notices_store, 
                 on_reminder: Optional[Callable] = None,
                 settings: Optional[ReminderSettings] = None):
        """
        Initialize the reminder thread.
        
        Args:
            notices_store: NoticesStore instance
            on_reminder: Callback when reminder is due (notice_id, title, content)
            settings: ReminderSettings instance
        """
        super().__init__(daemon=True)
        self.store = notices_store
        self.on_reminder = on_reminder
        self.settings = settings or ReminderSettings()
        self.dismissed = DismissedReminders()
        
        self._running = False
        self._stop_event = threading.Event()
        self._last_check_time = None
        self._active_popups: Dict[str, NotificationPopup] = {}
        self._popup_lock = threading.Lock()
        
        # Snoozed reminders: notice_id -> wake_time
        self._snoozed: Dict[str, datetime] = {}
        self._snooze_lock = threading.Lock()
    
    def run(self):
        """Main loop - check for reminders periodically."""
        self._running = True
        print("ReminderThread started")
        
        while not self._stop_event.is_set():
            if self.settings.get("enabled", True):
                self._check_reminders()
            
            # Wait for check interval or until stopped
            check_interval = self.settings.get("check_interval", 60)
            self._stop_event.wait(timeout=check_interval)
        
        self._running = False
        print("ReminderThread stopped")
    
    def stop(self):
        """Stop the reminder thread."""
        self._stop_event.set()
        
        # Close all active popups
        with self._popup_lock:
            for popup in list(self._active_popups.values()):
                popup.close()
            self._active_popups.clear()
    
    def _check_reminders(self):
        """Check for reminders that are due."""
        now = datetime.now()
        
        # Detect system time changes (backward)
        if self._last_check_time and now < self._last_check_time:
            print("System time change detected (backward), adjusting...")
            # Clear snoozed reminders that might be in the past
            with self._snooze_lock:
                self._snoozed = {
                    k: v for k, v in self._snoozed.items() 
                    if v > now
                }
        
        self._last_check_time = now
        
        # Get active notices with reminders
        notices = self.store.get_active()
        
        for notice in notices:
            # Skip if already has active popup
            with self._popup_lock:
                if notice.id in self._active_popups:
                    continue
            
            # Skip if dismissed
            if self.dismissed.is_dismissed(notice.id):
                continue
            
            # Check if snoozed
            with self._snooze_lock:
                if notice.id in self._snoozed:
                    if now < self._snoozed[notice.id]:
                        continue
                    else:
                        # Snooze expired
                        del self._snoozed[notice.id]
            
            # Check if reminder is due
            if notice.reminder_time and now >= notice.reminder_time:
                self._trigger_reminder(notice)
    
    def _trigger_reminder(self, notice):
        """Trigger a reminder notification."""
        print(f"Reminder triggered: {notice.title}")
        
        # Play sound if enabled
        if self.settings.get("play_sound", True):
            self._play_sound()
        
        # Call callback if provided
        if self.on_reminder:
            self.on_reminder(notice.id, notice.title, notice.content)
        
        # Show visual alert in panel (callback to gadget)
        # This will be handled by the callback
    
    def _play_sound(self):
        """Play notification sound."""
        sound_cmd = self.settings.get("sound_command")
        if sound_cmd and SOUND_AVAILABLE:
            try:
                subprocess.Popen(
                    sound_cmd.split(),
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            except Exception as e:
                print(f"Error playing sound: {e}")
    
    def show_popup(self, notice_id: str, title: str, message: str, 
                   parent_window=None):
        """
        Show a notification popup for a reminder.
        
        Args:
            notice_id: The notice ID
            title: Notice title
            message: Notice content
            parent_window: Optional parent tkinter window
        """
        # Check max notifications
        with self._popup_lock:
            if len(self._active_popups) >= self.settings.get("max_notifications", 5):
                # Remove oldest popup
                oldest_id = next(iter(self._active_popups))
                self._active_popups[oldest_id].close()
                del self._active_popups[oldest_id]
        
        def on_complete(nid):
            self.store.mark_completed(nid, True)
            self.dismissed.dismiss(nid)
            with self._popup_lock:
                self._active_popups.pop(nid, None)
        
        def on_snooze(nid, minutes):
            self.dismissed.dismiss(nid)
            with self._snooze_lock:
                self._snoozed[nid] = datetime.now() + timedelta(minutes=minutes)
            with self._popup_lock:
                self._active_popups.pop(nid, None)
        
        def on_dismiss(nid):
            self.dismissed.dismiss(nid)
            with self._popup_lock:
                self._active_popups.pop(nid, None)
        
        # Create popup
        popup = NotificationPopup(
            notice_id=notice_id,
            title=title,
            message=message,
            settings=self.settings,
            on_complete=on_complete,
            on_snooze=on_snooze,
            on_dismiss=on_dismiss
        )
        
        with self._popup_lock:
            self._active_popups[notice_id] = popup
    
    def snooze(self, notice_id: str, minutes: int):
        """Manually snooze a reminder."""
        with self._snooze_lock:
            self._snoozed[notice_id] = datetime.now() + timedelta(minutes=minutes)
        self.dismissed.dismiss(notice_id)
    
    def clear_snooze(self, notice_id: str):
        """Clear snooze status for a reminder."""
        with self._snooze_lock:
            self._snoozed.pop(notice_id, None)
    
    def is_snoozed(self, notice_id: str) -> bool:
        """Check if a reminder is currently snoozed."""
        with self._snooze_lock:
            return notice_id in self._snoozed
    
    def get_snooze_time(self, notice_id: str) -> Optional[datetime]:
        """Get when a snoozed reminder will wake up."""
        with self._snooze_lock:
            return self._snoozed.get(notice_id)
    
    def get_active_popup_count(self) -> int:
        """Get number of currently active popup notifications."""
        with self._popup_lock:
            # Clean up closed popups
            self._active_popups = {
                k: v for k, v in self._active_popups.items() 
                if v.window and v.window.winfo_exists()
            }
            return len(self._active_popups)
    
    def test_reminder(self, title: str = "Test Reminder", 
                     message: str = "This is a test notification."):
        """Trigger a test reminder immediately."""
        test_id = f"test_{int(time.time())}"
        self.show_popup(test_id, title, message)
    
    def force_check(self):
        """Force an immediate reminder check."""
        self._check_reminders()


class NotificationSettingsDialog:
    """
    Dialog for configuring notification settings.
    """
    
    def __init__(self, parent, settings: ReminderSettings):
        self.settings = settings
        self.result = False
        
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Notification Settings")
        self.dialog.geometry("400x400")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self._create_form()
        
        parent.wait_window(self.dialog)
    
    def _create_form(self):
        """Create the settings form."""
        pad = {'padx': 20, 'pady': 10}
        
        # Enable notifications
        self.enabled_var = tk.BooleanVar(value=self.settings.get("enabled", True))
        tk.Checkbutton(
            self.dialog,
            text="Enable notifications",
            variable=self.enabled_var
        ).pack(anchor='w', **pad)
        
        # Play sound
        self.sound_var = tk.BooleanVar(value=self.settings.get("play_sound", True))
        tk.Checkbutton(
            self.dialog,
            text="Play sound",
            variable=self.sound_var
        ).pack(anchor='w', **pad)
        
        # Sound command
        tk.Label(self.dialog, text="Sound command:").pack(anchor='w', padx=20)
        self.sound_cmd_var = tk.StringVar(value=self.settings.get("sound_command", ""))
        tk.Entry(self.dialog, textvariable=self.sound_cmd_var, width=40).pack(fill=tk.X, **pad)
        
        # Notification duration
        duration_frame = tk.Frame(self.dialog)
        duration_frame.pack(fill=tk.X, **pad)
        
        tk.Label(duration_frame, text="Notification duration (seconds):").pack(side=tk.LEFT)
        self.duration_var = tk.IntVar(value=self.settings.get("notification_duration", 10))
        tk.Spinbox(
            duration_frame,
            from_=5,
            to=300,
            increment=5,
            textvariable=self.duration_var,
            width=5
        ).pack(side=tk.LEFT, padx=10)
        
        # Check interval
        interval_frame = tk.Frame(self.dialog)
        interval_frame.pack(fill=tk.X, **pad)
        
        tk.Label(interval_frame, text="Check interval (seconds):").pack(side=tk.LEFT)
        self.interval_var = tk.IntVar(value=self.settings.get("check_interval", 60))
        tk.Spinbox(
            interval_frame,
            from_=10,
            to=300,
            increment=10,
            textvariable=self.interval_var,
            width=5
        ).pack(side=tk.LEFT, padx=10)
        
        # Max notifications
        max_frame = tk.Frame(self.dialog)
        max_frame.pack(fill=tk.X, **pad)
        
        tk.Label(max_frame, text="Max simultaneous notifications:").pack(side=tk.LEFT)
        self.max_var = tk.IntVar(value=self.settings.get("max_notifications", 5))
        tk.Spinbox(
            max_frame,
            from_=1,
            to=10,
            textvariable=self.max_var,
            width=5
        ).pack(side=tk.LEFT, padx=10)
        
        # Buttons
        btn_frame = tk.Frame(self.dialog)
        btn_frame.pack(fill=tk.X, pady=20)
        
        tk.Button(
            btn_frame,
            text="Save",
            command=self._save,
            bg='#4a90d9',
            fg='white',
            width=10
        ).pack(side=tk.RIGHT, padx=5)
        
        tk.Button(
            btn_frame,
            text="Cancel",
            command=self.dialog.destroy,
            width=10
        ).pack(side=tk.RIGHT, padx=5)
    
    def _save(self):
        """Save the settings."""
        self.settings.update(
            enabled=self.enabled_var.get(),
            play_sound=self.sound_var.get(),
            sound_command=self.sound_cmd_var.get(),
            notification_duration=self.duration_var.get(),
            check_interval=self.interval_var.get(),
            max_notifications=self.max_var.get()
        )
        self.result = True
        self.dialog.destroy()
