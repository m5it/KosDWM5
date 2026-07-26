# Changelog

## [1.2.11] - 2026-07-26

### Changed
- Auto-incremented from 1.2.10
- Files: HISTORY.md, __pycache__/AUTOVERSION.cpython-313.pyc, background.log, src/__pycache__/about_dialog_pyqt5.cpython-313.pyc, src/about_dialog_pyqt5.py +1


## [1.2.10] - 2026-07-26

### Changed
- Auto-incremented from 1.2.9
- Files: HISTORY.md, PLAN.md, __pycache__/AUTOVERSION.cpython-313.pyc, background.log, current_task.txt +6


## [1.2.9] - 2026-07-25

### Changed
- Auto-incremented from 1.2.8
- Files: AGENTS.md, AUTOVERSION.py, CHANGELOG.md, HISTORY.md, README.md +2


All notable changes to KosDWM will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.2.0] - 2025-01-22

### Added
- **Menu Configuration Dialog** (`src/menu_config_pyqt5.py`) - GUI for managing menus
  - Tree view of all menus with create/delete/rename
  - Support for 4 menu types: Branch, Leaf, Script, xdgmenumaker
  - Type-specific configuration fields
  - Live preview for Leaf menus
  - Auto-reload panel menu after saving (via `menus_changed` signal)
- **Script Menu Type** - Execute Python scripts with optional virtual environment
  - `scriptPath`: Path to Python script
  - `venvPath`: Path to virtual environment (auto-detects Linux/Windows)
  - Runs with `subprocess.Popen()` for independent execution
- **xdgmenumaker Menu Type** - Auto-generate menu from XDG .desktop files
  - Scans `/usr/share/applications`, `/usr/local/share/applications`, `~/.local/share/applications`
  - Organizes apps by categories (Accessories, Development, Games, Graphics, Network, Office, etc.)
  - Parses .desktop files for Name, Exec, Categories, Terminal, NoDisplay
  - Handles field codes (%f, %F, %u, %U, etc.)
  - Supports Terminal=true apps (runs in xterm)
- **Enhanced MenuManager** (`src/menus_pyqt5.py`)
  - `_run_script()` with venv support
  - `_generate_xdg_menu()` for xdgmenumaker
  - `_parse_desktop_file()` for .desktop parsing
  - `_launch_xdg_app()` with terminal detection
  - Comprehensive debug logging

### Changed
- **Panel Menu Building** - Now handles all menu types at top level
- **Menu Type Detection** - Top-level directories with config.json are now treated as menu items
- **Leaf Menu Type** - Now properly detected via `type: "leaf"` in config.json

### Fixed
- **Menu Reload** - Panel now reloads menus after configuration changes via signal connection

## [1.1.0] - 2026-07-23

### Added
- **Rich Text Editor for Notices** - Full formatting support (bold, italic, underline, font, size, color)
- **Double-click to Edit Notices** - Quick edit by double-clicking any notice
- **HTML Content Persistence** - Rich text survives save/load cycles

### Fixed
- **Notices Disappearing** - Fixed dialog freezing issue when clicking notices
- **Dark Theme Consistency** - All notices dialogs now use proper dark theme

### Changed
- Notices list now shows content preview (HTML stripped for display)
- Notice detail view renders HTML with full formatting

## [1.0.8] - 2026-07-23
- Auto-incremented version from 1.0.7
- Files changed: HISTORY.md, PLAN.md, __pycache__/kosdwm_diagnose.cpython-314.pyc, background.log, current_task.txt and 13 more


## [1.0.7] - 2026-07-23

### Changed
- Auto-incremented version from 1.0.6
- Files changed: README.md


## [1.0.6] - 2026-07-23

### Changed
- Auto-incremented version from 1.0.5
- Files changed: HISTORY.md, README.md, __pycache__/remove_from_history.cpython-314.pyc, background.log, current_task.txt and 4 more


## [1.0.5] - 2026-07-23

### Changed
- Auto-incremented version from 1.0.4
- Files changed: .gitignore


## [1.0.4] - 2026-07-23

### Changed
- Auto-incremented version from 1.0.3
- Files changed: __pycache__/remove_from_history.cpython-314.pyc, remove_from_history.py


## [1.0.3] - 2026-07-23

### Changed
- Auto-incremented version from 1.0.2
- Files changed: run.out


## [1.0.2] - 2026-07-23

### Changed
- Auto-incremented version from 1.0.1
- Files changed: HISTORY.md, __pycache__/AUTOVERSION.cpython-314.pyc, __pycache__/install_hooks.cpython-314.pyc, __pycache__/run.cpython-313.pyc, __pycache__/run.cpython-314.pyc and 24 more


## [1.0.1] - 2026-07-23

### Changed
- Auto-incremented version from 1.0.0
- Files changed: AUTOVERSION.py, CHANGELOG.md, HISTORY.md, PLAN.md, PROJECT.md and 40 more


## [1.0.0] - 2025-01-21

### Added
- Initial release of KosDWM
- Dynamic window management with Python
- Pluggable gadget system for panel
- HTTP API for notices management
- Notification system with reminders
- Auto-installer for KosDWM and gadgets
- Auto-versioning system with AUTOVERSION.py
- Pre-commit git hook for automatic version increment
- Version display in gadget configuration dialog
