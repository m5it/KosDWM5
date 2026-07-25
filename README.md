# KosDWM

A dynamic window manager with Python-based gadget system. Now with PyQt5!

## Features
- **Dynamic Window Management** - Tiling window manager for X11
- **PyQt5 Panel** - Modern Qt-based panel with gadgets and menus
- **Auto-Generative Menus** - Dynamic menus from `~/.config/KosDWM/Menus/` directory structure
  - **Branch** (folders) = submenus containing other menus
  - **Leaf** (`config.json`) = content windows with HTML or looping command output
  - **Script** (`config.json` with `type: "script"`) = executable Python scripts with optional venv
  - **xdgmenumaker** (`config.json` with `type: "xdgmenumaker"`) = auto-generated XDG application menu
- **Menu Configuration Dialog** - GUI for creating and managing menus
- **Gadget System** - Pluggable Python gadgets for the panel
  - **Notices Gadget** - Rich text editor with formatting (bold, italic, underline, font, size, color)
  - Double-click to edit notices
  - HTML content persistence
- **Window Switcher** - Dropdown to switch between running windows (wmctrl)
- **Notices & Reminders** - Built-in notification system with HTTP API
- **Dark Theme** - Consistent dark styling across all dialogs
- **Auto-Versioning** - Automatic version increment on commits

## Quick Start

```bash
# Install PyQt5 version
python install_kosdwm_pyqt5.py

# Run
python main_pyqt5.py

# Run with debug mode
python main_pyqt5.py -d
```

## Menu Types

### 1. Branch Menu (Submenu)
Folder containing other folders. Creates a cascading submenu.

### 2. Leaf Menu (Content Window)
Folder with `config.json` showing HTML content or command output:
```json
{
    "title": "System Info",
    "windowContent": "content.html",
    "windowScript": "lsof -i",
    "loop": 5,
    "looptype": "second"
}
```

### 3. Script Menu
Folder with `config.json` for running Python scripts:
```json
{
    "type": "script",
    "scriptPath": "/home/user/scripts/myapp.py",
    "venvPath": "/home/user/.venv/myapp"
}
```

### 4. xdgmenumaker Menu
Folder with `config.json` for auto-generated XDG application menu:
```json
{
    "type": "xdgmenumaker",
    "icon": "applications-other",
    "terminal": false
}
```
- Automatically populated from system `.desktop` files
- Organized by categories (Accessories, Development, Games, Graphics, Network, Office, etc.)

## Configuration

### Panel Config (`~/.config/KosDWM/config.json`):
```json
{
    "active_button_bg": "#4a90d9",
    "inactive_button_bg": "#606060",
    "bar_height": 30,
    "layout_mode": "comboboxes"
}
```

### Menu Structure (`~/.config/KosDWM/Menus/`):
```
Menus/
├── Home/                      # Branch menu (submenu)
│   ├── About/                 # Leaf menu
│   │   ├── config.json        # {"title": "About", "windowContent": "content.html"}
│   │   ├── content.html       # Static content
│   │   └── ok.py              # Optional: run() function called on OK
│   └── System/                # Leaf menu with script
│       ├── config.json        # {"windowScript": "df -h", "loop": 5}
│       └── ok.py
├── KosPrograms/               # Branch menu
│   └── KosFM/                 # Script menu
│       └── config.json        # {"type": "script", "scriptPath": "...", "venvPath": "..."}
└── OtherPrograms/             # xdgmenumaker menu
    └── config.json            # {"type": "xdgmenumaker"}
```

### Gadget Config (`~/.config/KosDWM/gadgets.json`):
```json
{
    "enabled": ["hello_world", "test_gadget", "notices"]
}
```

## Menu Configuration

Access the Menu Configuration dialog from the panel:
1. Click **⚙ Config** dropdown
2. Select **Menu Settings**
3. Use the GUI to:
   - Create new menus and folders
   - Set menu type (Branch, Leaf, Script, xdgmenumaker)
   - Configure type-specific options
   - Delete menus
   - Preview Leaf menu content

## Documentation

- [Agent Guide](AGENTS.md) - Developer and agent documentation
- [Notices API](NOTICES_API_DOCUMENTATION.md) - HTTP API for notices
- [PyQt5 Readme](PYQT5_README.md) - PyQt5 specific documentation
- [Changelog](CHANGELOG.md) - Version history

## Version

Current version: See `AUTOVERSION.py` or run `python main_pyqt5.py --version`

To install git hooks for auto-versioning:
```bash
python install_hooks.py
```

## License

MIT License - Created with love by B.K. and OpenCode (editor + BigPickle) and ollama models.
