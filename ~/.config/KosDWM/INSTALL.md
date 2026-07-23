# KosDWM Installation Guide

## Quick Start

### Method 1: Using the Installer Script (Recommended)

```bash
# From inside the KosDWM directory
cd /path/to/KosDWM
python install_kosdwm.py

# Or specify the source path
python install_kosdwm.py --source /path/to/KosDWM
```

This will:
- Install `kosdwm` and `kosdwm-panel` commands to `~/.local/bin`
- Create a desktop entry for application menus
- Set up proper Python paths so gadgets can find KosDWM modules

### Method 2: Using pip

```bash
# From inside the KosDWM directory
pip install .

# Or in development mode (editable)
pip install -e .
```

### Method 3: Manual Installation

```bash
# 1. Set environment variable (add to ~/.bashrc)
export KOSDWM_HOME=/path/to/KosDWM
export PATH="$PATH:$HOME/.local/bin"

# 2. Create symlink
ln -s /path/to/KosDWM/src/kosdwm.py ~/.local/bin/kosdwm

# 3. Run
kosdwm
```

## Dependencies

### Required
- Python 3.7+
- tkinter (usually comes with Python)
- X11 display server (Linux)

### Optional
- `flask` and `flask-cors` for HTTP API features
- `plyer` for cross-platform notifications

Install optional dependencies:
```bash
pip install flask flask-cors plyer
```

Or on Debian/Ubuntu:
```bash
sudo apt-get install python3-tk python3-flask
```

## Post-Installation

### 1. Reload your shell or run:
```bash
source ~/.bashrc  # or ~/.zshrc
```

### 2. Verify installation:
```bash
which kosdwm
kosdwm --help
```

### 3. Start KosDWM:
```bash
kosdwm
```

## Gadget Installation

After KosDWM is installed, gadgets can find KosDWM modules using:

```python
import sys
from pathlib import Path
import os

# Method 1: Environment variable (recommended)
if 'KOSDWM_HOME' in os.environ:
    KOSDWM_PATH = Path(os.environ['KOSDWM_HOME'])
else:
    # Method 2: Common paths
    KOSDWM_PATH = Path.home() / ".local" / "share" / "kosdwm"

sys.path.insert(0, str(KOSDWM_PATH / "src"))

from gadgets import GadgetBase
```

## Uninstallation

```bash
# Remove user installation
python uninstall_kosdwm.py

# Or with pip
pip uninstall kosdwm
```

## Troubleshooting

### "kosdwm: command not found"
Add `~/.local/bin` to your PATH:
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

### "Module not found" errors
Ensure `KOSDWM_HOME` environment variable is set:
```bash
export KOSDWM_HOME=/path/to/KosDWM
```

### Gadgets not loading
1. Check the KosDWM path in `~/.config/KosDWM/notices_gadget.conf`
2. Ensure gadgets are in `~/.config/KosDWM/gadgets/`
3. Run `kosdwm` from terminal to see error messages

## File Locations

After installation:

| File/Directory | Location |
|----------------|----------|
| Launcher scripts | `~/.local/bin/kosdwm` |
| Desktop entry | `~/.local/share/applications/kosdwm.desktop` |
| User config | `~/.config/KosDWM/` |
| Gadgets | `~/.config/KosDWM/gadgets/` |
