#!/usr/bin/env python3
"""
KosDWM Installer
================

Installs KosDWM window manager with proper Python path configuration.
Can be run from any location - will detect the KosDWM source directory.

Usage:
    python install_kosdwm.py          # Interactive install
    python install_kosdwm.py --user   # Install to user directories (default)
    python install_kosdwm.py --system # Install system-wide (requires sudo)
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
from datetime import datetime


# Installation paths
USER_BIN = Path.home() / ".local" / "bin"
USER_SHARE = Path.home() / ".local" / "share" / "kosdwm"
USER_CONFIG = Path.home() / ".config" / "KosDWM"
SYSTEM_BIN = Path("/usr/local/bin")
SYSTEM_SHARE = Path("/usr/local/share/kosdwm")
SYSTEM_CONFIG = Path("/etc/kosdwm")


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'


def print_status(msg, status="info"):
    """Print colored status message."""
    color = {
        "success": Colors.GREEN,
        "error": Colors.RED,
        "warning": Colors.YELLOW,
        "info": Colors.BLUE
    }.get(status, "")
    symbol = {"success": "✓", "error": "✗", "warning": "⚠", "info": "ℹ"}.get(status, "•")
    print(f"{color}{symbol}{Colors.RESET} {msg}")


def find_kosdwm_source():
    """
    Find KosDWM source directory.
    Checks in order:
    1. Same directory as this script
    2. Parent of script directory
    3. Current working directory
    4. Common clone locations
    """
    script_dir = Path(__file__).parent.resolve()
    
    # Check if we're running from inside KosDWM source
    check_paths = [
        script_dir,  # install_kosdwm.py in kosdwm root
        script_dir.parent,  # install_kosdwm.py in kosdwm/install_kosdwm.py
    ]
    
    for path in check_paths:
        if (path / "src" / "kosdwm.py").exists() or (path / "src" / "gadgets.py").exists():
            return path
    
    # Check current directory
    cwd = Path.cwd().resolve()
    if (cwd / "src" / "kosdwm.py").exists():
        return cwd
    
    # Check common locations
    home = Path.home()
    common = [
        home / "KosDWM",
        home / "kosdwm",
        home / "projects" / "KosDWM",
        home / "src" / "KosDWM",
        Path("/opt/KosDWM"),
        Path("/usr/local/src/KosDWM"),
    ]
    
    for path in common:
        if (path / "src" / "kosdwm.py").exists():
            return path
    
    return None


def check_dependencies():
    """Check if required dependencies are installed."""
    deps_ok = True
    
    # Check Python version
    if sys.version_info < (3, 7):
        print_status("Python 3.7+ required", "error")
        deps_ok = False
    else:
        print_status(f"Python {sys.version_info.major}.{sys.version_info.minor}", "success")
    
    # Check tkinter
    try:
        import tkinter
        print_status(f"tkinter available", "success")
    except ImportError:
        print_status("tkinter not found - install with: sudo apt-get install python3-tk", "error")
        deps_ok = False
    
    # Check for X11 (Linux)
    if os.environ.get('DISPLAY'):
        print_status("X11 display available", "success")
    else:
        print_status("No X11 display detected", "warning")
    
    return deps_ok


def create_launcher_script(source_path, install_bin, install_share, user_install=True):
    """
    Create the kosdwm launcher script that sets up Python path correctly.
    """
    launcher = install_bin / "kosdwm"
    
    python_path = str(source_path / "src")
    config_path = USER_CONFIG if user_install else Path.home() / ".config" / "KosDWM"
    
    script_content = f'''#!/usr/bin/env python3
"""
KosDWM Launcher
===============

Generated launcher script for KosDWM.
Do not edit - regenerate with: python install_kosdwm.py
"""

import sys
import os
from pathlib import Path

# KosDWM source location
KOSDWM_SOURCE = Path("{source_path}")

# Add KosDWM src to Python path
sys.path.insert(0, str(KOSDWM_SOURCE / "src"))

# Set environment variable for gadgets to find KosDWM
os.environ['KOSDWM_HOME'] = str(KOSDWM_SOURCE)

# Ensure config directory exists
CONFIG_DIR = Path.home() / ".config" / "KosDWM"
CONFIG_DIR.mkdir(parents=True, exist_ok=True)

# Import and run KosDWM
try:
    from kosdwm import main
    sys.exit(main())
except ImportError as e:
    print(f"Error: Cannot import KosDWM from {{KOSDWM_SOURCE}}")
    print(f"Python path: {{sys.path}}")
    print(f"Import error: {{e}}")
    sys.exit(1)
'''
    
    launcher.write_text(script_content)
    launcher.chmod(0o755)
    
    print_status(f"Created launcher: {launcher}", "success")
    return True


def create_panel_launcher(source_path, install_bin):
    """Create kosdwm-panel launcher."""
    launcher = install_bin / "kosdwm-panel"
    
    script_content = f'''#!/usr/bin/env python3
"""
KosDWM Panel Launcher
=====================

Launches only the panel (for testing or separate use).
"""

import sys
import os
from pathlib import Path

KOSDWM_SOURCE = Path("{source_path}")
sys.path.insert(0, str(KOSDWM_SOURCE / "src"))
os.environ['KOSDWM_HOME'] = str(KOSDWM_SOURCE)

try:
    from panel import PanelWindow
    import tkinter as tk
    
    root = tk.Tk()
    root.withdraw()
    panel = PanelWindow(root)
    root.mainloop()
except ImportError as e:
    print(f"Error: {{e}}")
    sys.exit(1)
'''
    
    launcher.write_text(script_content)
    launcher.chmod(0o755)
    
    print_status(f"Created panel launcher: {launcher}", "success")
    return True


def create_desktop_entry(source_path, install_share):
    """Create .desktop file for application menu."""
    apps_dir = Path.home() / ".local" / "share" / "applications"
    apps_dir.mkdir(parents=True, exist_ok=True)
    
    desktop_file = apps_dir / "kosdwm.desktop"
    
    content = f'''[Desktop Entry]
Name=KosDWM
Comment=Dynamic Window Manager with Python Gadgets
Exec={USER_BIN / "kosdwm"}
Type=Application
Terminal=false
Categories=System;WindowManager;
Icon=preferences-system-windows
StartupNotify=false
X-GNOME-Autostart-enabled=true
'''
    
    desktop_file.write_text(content)
    
    print_status(f"Created desktop entry: {desktop_file}", "success")
    return True


def create_gadget_loader_template(source_path):
    """
    Create a template that gadgets can use to reliably import KosDWM modules.
    This file will be saved in the KosDWM source for gadgets to reference.
    """
    loader_file = source_path / "gadget_loader.py"
    
    content = '''#!/usr/bin/env python3
"""
KosDWM Gadget Loader Template
=============================

Copy this at the top of your gadget to ensure it can find KosDWM modules
regardless of where KosDWM is installed.

Usage:
    Copy the sys.path setup from below into your gadget file.
"""

import sys
from pathlib import Path

# Method 1: Use KOSDWM_HOME environment variable (recommended)
if 'KOSDWM_HOME' in __import__('os').environ:
    KOSDWM_PATH = Path(__import__('os').environ['KOSDWM_HOME'])
else:
    # Method 2: Common installation paths
    home = Path.home()
    possible_paths = [
        home / ".local" / "share" / "kosdwm",
        home / "KosDWM",
        home / "kosdwm",
        Path("/usr/local/share/kosdwm"),
        Path("/opt/kosdwm"),
    ]
    
    # Method 3: Check if KosDWM is in parent directories
    current = Path(__file__).resolve()
    for parent in [current.parent] + list(current.parents):
        if (parent / "src" / "kosdwm.py").exists():
            KOSDWM_PATH = parent
            break
    else:
        # Use first existing path or default
        KOSDWM_PATH = next((p for p in possible_paths if p.exists()), possible_paths[0])

# Add KosDWM src to Python path
sys.path.insert(0, str(KOSDWM_PATH / "src"))

# Now you can import KosDWM modules
# from gadgets import GadgetBase
# from kosdwm import ...
'''
    
    loader_file.write_text(content)
    print_status(f"Created gadget loader template: {loader_file}", "success")


def add_to_path(bin_dir):
    """Add bin directory to PATH if not already there."""
    shell_rc = None
    
    if "bash" in os.environ.get("SHELL", ""):
        shell_rc = Path.home() / ".bashrc"
    elif "zsh" in os.environ.get("SHELL", ""):
        shell_rc = Path.home() / ".zshrc"
    
    if shell_rc and shell_rc.exists():
        with open(shell_rc, 'r') as f:
            content = f.read()
        
        path_line = f'export PATH="$PATH:{bin_dir}"'
        
        if str(bin_dir) not in content:
            with open(shell_rc, 'a') as f:
                f.write(f'\n# KosDWM path\n{path_line}\n')
            print_status(f"Added {bin_dir} to PATH in {shell_rc}", "success")
            print(f"  Run 'source {shell_rc}' or restart terminal to apply")


def install(source_path, user_install=True):
    """Main installation routine."""
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}  KosDWM Installer{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")
    print()
    
    # Determine install locations
    if user_install:
        install_bin = USER_BIN
        install_share = USER_SHARE
    else:
        install_bin = SYSTEM_BIN
        install_share = SYSTEM_SHARE
    
    print(f"Source: {source_path}")
    print(f"Install binaries to: {install_bin}")
    print(f"Install data to: {install_share}")
    print()
    
    # Check dependencies
    print_status("Checking dependencies...", "info")
    if not check_dependencies():
        print()
        print_status("Some dependencies missing. Install them and try again.", "error")
        return 1
    
    print()
    
    # Create directories
    install_bin.mkdir(parents=True, exist_ok=True)
    install_share.mkdir(parents=True, exist_ok=True)
    USER_CONFIG.mkdir(parents=True, exist_ok=True)
    
    # Install launcher scripts
    print_status("Creating launcher scripts...", "info")
    create_launcher_script(source_path, install_bin, install_share, user_install)
    create_panel_launcher(source_path, install_bin)
    
    # Create gadget loader template
    print_status("Creating gadget loader template...", "info")
    create_gadget_loader_template(source_path)
    
    # Create desktop entry
    print_status("Creating desktop entry...", "info")
    create_desktop_entry(source_path, install_share)
    
    # Add to PATH
    if user_install:
        add_to_path(install_bin)
    
    # Create config symlink or copy
    config_link = install_share / "config"
    if not config_link.exists():
        if USER_CONFIG.exists():
            config_link.symlink_to(USER_CONFIG)
    
    print()
    print(f"{Colors.GREEN}{'='*60}{Colors.RESET}")
    print(f"{Colors.GREEN}  Installation complete!{Colors.RESET}")
    print(f"{Colors.GREEN}{'='*60}{Colors.RESET}")
    print()
    print("You can now run KosDWM with:")
    print(f"  {Colors.BLUE}kosdwm{Colors.RESET}")
    print()
    print("Or just the panel:")
    print(f"  {Colors.BLUE}kosdwm-panel{Colors.RESET}")
    print()
    print("Gadgets should now be able to find KosDWM modules automatically.")
    print()
    
    if user_install and str(install_bin) not in os.environ.get("PATH", ""):
        print(f"{Colors.YELLOW}Note:{Colors.RESET} You may need to restart your terminal")
        print(f"      or run: source ~/.bashrc")
        print()
    
    return 0


def main():
    parser = argparse.ArgumentParser(description="Install KosDWM")
    parser.add_argument("--system", action="store_true", help="System-wide install (requires sudo)")
    parser.add_argument("--user", action="store_true", default=True, help="User install (default)")
    parser.add_argument("--source", type=Path, help="KosDWM source path")
    
    args = parser.parse_args()
    
    # Find source
    if args.source:
        source = args.source.resolve()
    else:
        source = find_kosdwm_source()
    
    if not source:
        print_status("Cannot find KosDWM source directory", "error")
        print()
        print("Please run this script from within the KosDWM source directory,")
        print("or specify the source path with --source /path/to/kosdwm")
        return 1
    
    if not (source / "src" / "kosdwm.py").exists():
        print_status(f"Does not appear to be KosDWM source: {source}", "error")
        return 1
    
    # Run installation
    user_install = not args.system
    
    if args.system and os.geteuid() != 0:
        print_status("System install requires sudo: sudo python install_kosdwm.py --system", "error")
        return 1
    
    return install(source, user_install)


if __name__ == "__main__":
    sys.exit(main())
