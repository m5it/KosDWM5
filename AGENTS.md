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
- Panel API: `src/panel_api_pyqt5.py`
- About Dialog: `src/about_dialog_pyqt5.py`
- Notices Gadget: `src/notices_gadget_pyqt5.py`

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

### Window Switcher
- Dropdown showing running windows (wmctrl)
- Shows desktop numbers for windows on other desktops
- Visual feedback on window activation

### Auto-Generative Menus
- Dynamic menus from directory structure
  - Folders = submenus
  - `config.json` = leaf menus (content windows)
  - `.py` files = runnable scripts with `run()` function
  - `windowScript` = looping command output

### Gadget System
- Clickable icons in panel
- **Notices Gadget**: Rich text editor with formatting (bold, italic, underline, color, font, size)
- Gadgets can register HTTP API endpoints via `panel.api.register()`

### Dark Theme
- All dialogs use dark background (#1a1a1a) with light text
- Consistent styling across all configuration dialogs

### About Window
- Accessible from Config dropdown (⚙ → About KosDWM)
- Shows version from AUTOVERSION.py
- Credits: B.K., OpenCode contributors
- System info: Python version, Qt version, Platform

## HTTP Panel API

The panel runs an HTTP API server on port 8080 (configurable) that allows gadgets to register custom endpoints.

### Default Endpoints
- `GET /api/status` - API status and endpoint count
- `GET /api/endpoints` - List all registered endpoints

### Notices Gadget Endpoints
- `GET /api/notices` - List all notices
- `POST /api/notices` - Create new notice
- `POST /api/notices/delete` - Delete notice by ID

### Creating Gadget API Endpoints

Gadgets can register HTTP endpoints by overriding `set_panel()`:

```python
class MyGadget(GadgetBase):
    def set_panel(self, panel):
        super().set_panel(panel)
        # Register endpoints when panel is set
        self.register_endpoint("/api/mygadget/status", self._api_status)
        self.register_endpoint("/api/mygadget/action", self._api_action, methods=["POST"])
    
    def _api_status(self, request_data):
        """Handle GET requests"""
        return {
            "gadget": self.get_name(),
            "status": "active",
            "method": request_data.get('method')
        }
    
    def _api_action(self, request_data):
        """Handle POST requests"""
        body = request_data.get('body', {})
        # Process body data...
        return {"result": "success"}
```

### Request Data Structure

Handler functions receive a dictionary with:
- `method`: HTTP method ("GET", "POST", etc.)
- `path`: Request path
- `query`: Query parameters dict
- `headers`: Request headers dict
- `body`: JSON body (for POST requests)

### Testing with curl

```bash
# Check API status
curl http://localhost:8080/api/status | python -m json.tool

# List all notices
curl http://localhost:8080/api/notices | python -m json.tool

# Create a notice
curl -X POST http://localhost:8080/api/notices \
  -H "Content-Type: application/json" \
  -d '{"title":"Meeting","content":"<b>Team meeting</b>","priority":"high"}' \
  | python -m json.tool

# Delete a notice
curl -X POST http://localhost:8080/api/notices/delete \
  -H "Content-Type: application/json" \
  -d '{"id":"NOTICE-UUID-HERE"}' \
  | python -m json.tool
```

## Thread Safety

The HTTP API runs in a separate thread. All gadget data access should be thread-safe:

- `NoticesStore` uses `threading.RLock()` for all operations
- UI updates should use Qt's signal/slot mechanism
- Gadgets should minimize blocking operations in API handlers

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
- Added dark theme for all dialogs
- Fixed menu freeze with Qt.QueuedConnection
- Gadget system now uses QMessageBox with styling
- **NEW**: Added About dialog with version and credits
- **NEW**: HTTP Panel API for gadget endpoints
- **NEW**: NoticesGadget with HTTP API endpoints (GET/POST/DELETE)
- **NEW**: Thread-safe data access with RLock
