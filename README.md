# KosDWM

A dynamic window manager with Python-based gadget system. Now with PyQt5!

## Features

- **Dynamic Window Management** - Tiling window manager for X11
- **PyQt5 Panel** - Modern Qt-based panel with gadgets and menus
- **Auto-Generative Menus** - Dynamic menus from `~/.config/KosDWM/Menus/` directory structure
  - Folders = submenus
  - `config.json` = leaf menus with content windows
  - `.py` scripts = runnable with `run()` function
  - `windowScript` = looping command output (like `lsof`)
- **Gadget System** - Pluggable Python gadgets for the panel
- **Window Switcher** - Dropdown to switch between running windows (wmctrl)
- **Notices & Reminders** - Built-in notification system with HTTP API
- **Auto-Versioning** - Automatic version increment on commits

## Quick Start

```bash
# Install PyQt5 version
python install_kosdwm_pyqt5.py

# Run
python main_pyqt5.py
```

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
├── Home/
│   ├── About/              # Leaf menu (config.json + content.html)
│   │   ├── config.json     # {"title": "About", "windowContent": "content.html"}
│   │   ├── content.html    # Static content
│   │   └── ok.py           # Optional: run() function called on OK
│   └── Test/               # Another leaf menu
│       ├── config.json     # {"windowScript": "lsof -i", "loop": 5}
│       └── ok.py
└── Scripts/
    └── myscript.py         # Runnable script with run() function
```

### Gadget Config (`~/.config/KosDWM/gadgets.json`):
```json
{
    "enabled": ["hello_world", "test_gadget", "notices"]
}
```

## Documentation

- [Notices API](NOTICES_API_DOCUMENTATION.md) - HTTP API for notices
- [PyQt5 Readme](PYQT5_README.md) - PyQt5 specific documentation
- [Changelog](CHANGELOG.md) - Version history

## License

MIT License - Created with love by B.K. and OpenCode ( editor + BigPickle ) and ollama models.
