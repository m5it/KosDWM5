# Changelog

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


All notable changes to KosDWM will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Auto-versioning system with AUTOVERSION.py
- Pre-commit git hook for automatic version increment
- Version display in gadget configuration dialog

## [1.0.0] - 2025-01-21

### Added
- Initial release of KosDWM
- Dynamic window management with Python
- Pluggable gadget system for panel
- HTTP API for notices management
- Notification system with reminders
- Auto-installer for KosDWM and gadgets
# Changelog

## [1.0.8] - 2026-07-23

### Changed
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


All notable changes to KosDWM will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Auto-versioning system with AUTOVERSION.py
- Pre-commit git hook for automatic version increment
- Version display in gadget configuration dialog

## [1.0.0] - 2025-01-21

### Added
- Initial release of KosDWM
- Dynamic window management with Python
- Pluggable gadget system for panel
- HTTP API for notices management
- Notification system with reminders
- Auto-installer for KosDWM and gadgets



## [2.0.0] - 2025-07-23

### Added
- **PyQt5 Panel Implementation** - Complete rewrite of panel using PyQt5
- **Window Switcher Dropdown** - Shows running windows using wmctrl
- **Auto-Generative Menus** - Dynamic menus from directory structure
- **Light Theme** - All dialogs and menus now use light theme
- **Qt.QueuedConnection** - Prevents menu freeze when opening dialogs

### Changed
- Panel now uses QComboBox for window switching
- Menus now auto-generate from ~/.config/KosDWM/Menus/ structure
- Gadget dialogs use light theme with blue buttons
- Menu system supports leaf menus with config.json
- Menu system supports looping scripts (lsof, etc.)

### Fixed
- Menu freeze when clicking leaf menu items
- Window activation via wmctrl
- Dialog styling for better visibility

### Technical
- Migrated from TkInter to PyQt5
- Added WindowManager class using wmctrl
- Added MenuManager with directory scanning
- Added proper signal/slot connections
