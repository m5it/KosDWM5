# KosDWM PyQt5 Version

This is a complete port of KosDWM from Tkinter to PyQt5.

## Files Created

### Main Application
- `main_pyqt5.py` - Main entry point with QApplication
- `requirements-pyqt5.txt` - Dependencies (PyQt5, flask, flask-cors)
- `install_kosdwm_pyqt5.py` - Installation script

### Core Modules (src/)
- `gadgets_pyqt5.py` - GadgetManager, GadgetBase, HelloWorldGadget, TestGadget
- `panel_pyqt5.py` - Panel widget with gadgets, clock, desktop buttons, menus
- `desktop_manager_pyqt5.py` - Desktop switching with wmctrl
- `menus_pyqt5.py` - Dynamic menu system from ~/.config/KosDWM/Menus
- `gadget_config_pyqt5.py` - Configuration dialog with QScrollArea
- `notices_gadget_pyqt5.py` - Notices gadget with QTimer

### Test Scripts
- `test_pyqt5.py` - Test suite to verify installation
- `run.sh` / `run-debug.sh` - Startup scripts

## Installation

### 1. Install Dependencies
```bash
.venv/bin/pip install -r requirements-pyqt5.txt
```

Or use the installer:
```bash
python install_kosdwm_pyqt5.py --user
```

### 2. Test Installation
```bash
python test_pyqt5.py
```

### 3. Run KosDWM
```bash
python main_pyqt5.py
```

Or if installed:
```bash
kosdwm-pyqt5
```

## Features

### Gadget System
- **Hello World Gadget** (👋) - Example gadget with message dialog
- **Test Gadget** (🧪) - Verifies loading system
- **Notices Gadget** (📝) - Manages notices/reminders (if PyQt5 available)

### Panel Features
- Desktop switching buttons (1, 2, 3, 4)
- Dynamic gadget loading with QPushButton
- Clock with QTimer updates
- Config button (⚙️) opens gadget dialog
- Dynamic menus from ~/.config/KosDWM/Menus

### Config Window
- QScrollArea for all gadgets
- QCheckBox for enable/disable
- Save/Cancel/Reload buttons
- Shows all 5 gadgets (3 built-in + discovered)

### Desktop Management
- wmctrl integration for desktop switching
- Window list tracking
- QTimer for periodic updates

## Differences from Tkinter Version

| Feature | Tkinter | PyQt5 |
|---------|---------|-------|
| Widgets | Tk.Button | QPushButton |
| Layout | pack/grid | QHBoxLayout/QVBoxLayout |
| Scrolling | Canvas (broken) | QScrollArea (working) |
| Dialogs | Toplevel | QDialog |
| Timers | after() | QTimer |
| Signals | callbacks | pyqtSignal |

## Troubleshooting

### "No module named 'PyQt5'"
Install PyQt5: `.venv/bin/pip install PyQt5`

### Gadgets not visible
Check `~/.config/KosDWM/gadgets.json`:
```json
{
  "enabled": ["hello_world", "test_gadget", "notices"]
}
```

### Desktop switching not working
Install wmctrl: `sudo apt-get install wmctrl`

## Architecture

```
main_pyqt5.py
    └── KosDWM (QMainWindow)
        └── Panel (QFrame)
            ├── MenuManager (QMenu)
            ├── DesktopManager (wmctrl)
            ├── GadgetManager (dynamic loading)
            │   └── Gadgets (QPushButton)
            └── GadgetConfigDialog (QDialog)
                └── QScrollArea with QCheckBox
```

## Next Steps

1. Install PyQt5 dependencies
2. Run test_pyqt5.py to verify
3. Run main_pyqt5.py to start
4. Open config window to see all gadgets
5. Test desktop switching and menus
# KosDWM PyQt5 Version

This is a complete port of KosDWM from Tkinter to PyQt5.

## Files Created

### Main Application
- `main_pyqt5.py` - Main entry point with QApplication
- `requirements-pyqt5.txt` - Dependencies (PyQt5, flask, flask-cors)
- `install_kosdwm_pyqt5.py` - Installation script

### Core Modules (src/)
- `gadgets_pyqt5.py` - GadgetManager, GadgetBase, HelloWorldGadget, TestGadget
- `panel_pyqt5.py` - Panel widget with gadgets, clock, desktop buttons, menus
- `desktop_manager_pyqt5.py` - Desktop switching with wmctrl
- `menus_pyqt5.py` - Dynamic menu system from ~/.config/KosDWM/Menus
- `gadget_config_pyqt5.py` - Configuration dialog with QScrollArea
- `notices_gadget_pyqt5.py` - Notices gadget with QTimer

### Test Scripts
- `test_pyqt5.py` - Test suite to verify installation
- `run.sh` / `run-debug.sh` - Startup scripts

## Installation

### 1. Install Dependencies
```bash
.venv/bin/pip install -r requirements-pyqt5.txt
```

Or use the installer:
```bash
python install_kosdwm_pyqt5.py --user
```

### 2. Test Installation
```bash
python test_pyqt5.py
```

### 3. Run KosDWM
```bash
python main_pyqt5.py
```

Or if installed:
```bash
kosdwm-pyqt5
```

## Features

### Gadget System
- **Hello World Gadget** (👋) - Example gadget with message dialog
- **Test Gadget** (🧪) - Verifies loading system
- **Notices Gadget** (📝) - Manages notices/reminders (if PyQt5 available)

### Panel Features
- Desktop switching buttons (1, 2, 3, 4)
- Dynamic gadget loading with QPushButton
- Clock with QTimer updates
- Config button (⚙️) opens gadget dialog
- Dynamic menus from ~/.config/KosDWM/Menus

### Config Window
- QScrollArea for all gadgets
- QCheckBox for enable/disable
- Save/Cancel/Reload buttons
- Shows all 5 gadgets (3 built-in + discovered)

### Desktop Management
- wmctrl integration for desktop switching
- Window list tracking
- QTimer for periodic updates

## Differences from Tkinter Version

| Feature | Tkinter | PyQt5 |
|---------|---------|-------|
| Widgets | Tk.Button | QPushButton |
| Layout | pack/grid | QHBoxLayout/QVBoxLayout |
| Scrolling | Canvas (broken) | QScrollArea (working) |
| Dialogs | Toplevel | QDialog |
| Timers | after() | QTimer |
| Signals | callbacks | pyqtSignal |

## Troubleshooting

### "No module named 'PyQt5'"
Install PyQt5: `.venv/bin/pip install PyQt5`

### Gadgets not visible
Check `~/.config/KosDWM/gadgets.json`:
```json
{
  "enabled": ["hello_world", "test_gadget", "notices"]
}
```

### Desktop switching not working
Install wmctrl: `sudo apt-get install wmctrl`

## Architecture

```
main_pyqt5.py
    └── KosDWM (QMainWindow)
        └── Panel (QFrame)
            ├── MenuManager (QMenu)
            ├── DesktopManager (wmctrl)
            ├── GadgetManager (dynamic loading)
            │   └── Gadgets (QPushButton)
            └── GadgetConfigDialog (QDialog)
                └── QScrollArea with QCheckBox
```

## Next Steps

1. Install PyQt5 dependencies
2. Run test_pyqt5.py to verify
3. Run main_pyqt5.py to start
4. Open config window to see all gadgets
5. Test desktop switching and menus



## Updates (July 2025)

### Menu System Improvements
- Fixed menu freeze when opening leaf menus using `Qt.QueuedConnection`
- Added support for `windowScript` with looping (e.g., `lsof -i` updating every 5 seconds)
- Added support for `ok.py` scripts with `run(window)` function
- Menu items now use light theme with proper styling

### Documentation Updates
- Updated README.md with PyQt5 features and menu structure
- Updated CHANGELOG.md with version 2.0.0 changes
- Updated AGENTS.md with PyQt5 specific information
