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
- Menu Config Dialog: `src/menu_config_pyqt5.py`
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
  - **Branch** (folders with subdirectories) = submenus
  - **Leaf** (`config.json`) = content windows with HTML or command output
  - **Script** (`config.json` with `scriptPath`) = executable Python scripts with optional venv
  - **xdgmenumaker** (`config.json` with `type: "xdgmenumaker"`) = auto-generated XDG application menu
  - Legacy `.py` files = runnable scripts with `run()` function

### Menu Types

#### 1. Branch Menu (Submenu)
Empty folder containing other folders. Creates a cascading submenu.

#### 2. Leaf Menu (Content Window)
Folder with `config.json`:
```json
{
    "title": "System Info",
    "windowContent": "content.html",
    "windowScript": "lsof -i",
    "loop": 5,
    "looptype": "second"
}
```

#### 3. Script Menu
Folder with `config.json`:
```json
{
    "type": "script",
    "scriptPath": "/path/to/script.py",
    "venvPath": "/home/user/.venv/myenv"
}
```
- Runs script with specified Python interpreter
- Supports virtual environments (auto-detects `bin/python` or `Scripts/python.exe`)

#### 4. xdgmenumaker Menu
Folder with `config.json`:
```json
{
    "type": "xdgmenumaker",
    "icon": "applications-other",
    "terminal": false
}
```
- Auto-generates menu from XDG `.desktop` files
- Organized by categories (Accessories, Development, Games, Graphics, Network, Office, etc.)
- Scans: `/usr/share/applications`, `/usr/local/share/applications`, `~/.local/share/applications`

### Menu Configuration Dialog
Access via: Panel → ⚙ Config → Menu Settings

Features:
- Tree view of all menus
- Edit menu properties (Name, Type)
- Type-specific configuration:
  - **Leaf**: Window Title, Content File, Window Script, Loop Interval
  - **Script**: Script Path, Virtual Environment Path
  - **xdgmenumaker**: Icon, Terminal checkbox
- Create new menus/folders
- Delete menus
- Live preview for Leaf menus
- Auto-reload panel menu after saving

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

## Menu Structure Examples

### Example 1: Mixed Menu Types
```
Menus/
├── Home/                      # Branch menu (submenu)
│   ├── About/                 # Leaf menu
│   │   ├── config.json
│   │   └── content.html
│   └── System/                # Leaf menu with script
│       ├── config.json        # {"windowScript": "df -h", "loop": 5}
│       └── ok.py
├── KosPrograms/               # Branch menu
│   └── KosFM/                 # Script menu
│       └── config.json        # {"type": "script", "scriptPath": "...", "venvPath": "..."}
└── OtherPrograms/             # xdgmenumaker menu
    └── config.json            # {"type": "xdgmenumaker"}
```

## Debugging

Run with debug mode to see detailed logs:
```bash
python main_pyqt5.py -d
```

Look for `[MenuManager]` and `[Panel]` debug messages to trace menu loading.
