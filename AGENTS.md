# KosDWM Agent Guide

## Key Commands
- **TkInter Version**: `python run.py`
- **PyQt5 Version**: `python main_pyqt5.py`
- Config: Edit `~/.config/KosDWM/config.json`
- Menus: Create folders in `~/.config/KosDWM/Menus/`

## Important Files

### PyQt5 Version (Current)
- Entry point: `main_pyqt5.py`
- Panel: `src/panel_pyqt5.py`
- Menus: `src/menus_pyqt5.py`
- Gadgets: `src/gadgets_pyqt5.py`
- Window Manager: `src/window_manager_pyqt5.py`
- Desktop Manager: `src/desktop_manager_pyqt5.py`

### Legacy TkInter Version
- Entry point: `run.py`
- Config manager: `src/config.py`
- Helper functions: `src/functions.py`

## Configuration Locations
- Main config: `~/.config/KosDWM/config.json`
- Gadgets config: `~/.config/KosDWM/gadgets.json`
- Menus directory: `~/.config/KosDWM/Menus/`
- Notices data: `~/.config/KosDWM/notices.json`

## PyQt5 Features
- **Window Switcher**: Dropdown showing running windows (wmctrl)
- **Auto-Generative Menus**: Dynamic menus from directory structure
  - Folders = submenus
  - `config.json` = leaf menus (content windows)
  - `.py` files = runnable scripts with `run()` function
  - `windowScript` = looping command output
- **Gadget System**: Clickable icons in panel
  - **Notices Gadget**: Rich text editor with formatting (bold, italic, underline, color, font, size)
- **Dark Theme**: All dialogs use dark background with light text
  - `windowScript` = looping command output
- **Gadget System**: Clickable icons in panel
- **Light Theme**: All dialogs use light background with blue buttons

## External Dependencies
- Requires `wmctrl` command for window management
- Requires `PyQt5` Python package (`pip install PyQt5`)
- For TkInter version: requires `screeninfo` and standard Tkinter

## Menu Structure Example
```
~/.config/KosDWM/Menus/
├── Home/
│   ├── About/
│   │   ├── config.json       # {"title": "About", "windowContent": "about.html"}
│   │   ├── about.html        # Static content
│   │   └── ok.py             # Optional: def run(window): ...
│   └── Test/
│       ├── config.json       # {"windowScript": "lsof -i", "loop": 5}
│       └── ok.py
└── Scripts/
    └── my_tool.py            # def run(parent): ...
```

## Recent Changes (PyQt5)
- Complete migration from TkInter to PyQt5
- Added window switcher dropdown using wmctrl
- Added auto-generative menu system
- Added light theme for all dialogs
- Fixed menu freeze with Qt.QueuedConnection
- Gadget system now uses QMessageBox with styling
