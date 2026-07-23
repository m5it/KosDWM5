#!/usr/bin/env python3
"""
KosDWM PyQt5 Installer
======================

Installs KosDWM window manager with PyQt5.
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


def check_dependencies():
    """Check if required dependencies are installed."""
    deps_ok = True
    
    # Check Python version
    if sys.version_info < (3, 7):
        print_status("Python 3.7+ required", "error")
        deps_ok = False
    else:
        print_status(f"Python {sys.version_info.major}.{sys.version_info.minor}", "success")
    
    # Check PyQt5
    try:
        import PyQt5
        print_status("PyQt5 available", "success")
    except ImportError:
        print_status("PyQt5 not installed", "warning")
        print("  Install with: pip install PyQt5")
        deps_ok = False
    
    # Check wmctrl
    try:
        subprocess.run(["wmctrl", "--version"], capture_output=True, check=True)
        print_status("wmctrl available", "success")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print_status("wmctrl not found (required for window management)", "warning")
        print("  Install with: sudo apt-get install wmctrl")
    
    return deps_ok


def install_dependencies():
    """Install Python dependencies."""
    print_status("Installing Python dependencies...", "info")
    
    deps = ["PyQt5", "flask", "flask-cors"]
    
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install"] + deps,
            check=True
        )
        print_status("Dependencies installed", "success")
        return True
    except subprocess.CalledProcessError as e:
        print_status(f"Failed to install dependencies: {e}", "error")
        return False


def create_launcher_script(source_path, install_bin):
    """Create the kosdwm launcher script."""
    launcher = install_bin / "kosdwm-pyqt5"
    
    script_content = f'''#!/usr/bin/env python3
"""
KosDWM PyQt5 Launcher
=====================

Generated launcher script for KosDWM PyQt5.
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
    from main_pyqt5 import main
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


def create_desktop_entry(source_path, install_share):
    """Create desktop entry for GUI launch."""
    apps_dir = Path.home() / ".local" / "share" / "applications"
    apps_dir.mkdir(parents=True, exist_ok=True)
    
    desktop_file = apps_dir / "kosdwm-pyqt5.desktop"
    
    desktop_content = f'''[Desktop Entry]
Name=KosDWM (PyQt5)
Comment=Simple Window Manager with PyQt5
Exec={USER_BIN / "kosdwm-pyqt5"}
Type=Application
Terminal=false
Categories=System;WindowManager;
'''
    
    desktop_file.write_text(desktop_content)
    print_status(f"Created desktop entry: {desktop_file}", "success")


def add_to_path(install_bin):
    """Add install_bin to PATH in shell config."""
    shell_rc = Path.home() / ".bashrc"
    
    if not shell_rc.exists():
        shell_rc = Path.home() / ".zshrc"
    
    if shell_rc.exists():
        with open(shell_rc, 'r') as f:
            content = f.read()
        
        path_line = f'export PATH="$PATH:{install_bin}"'
        
        if path_line not in content:
            with open(shell_rc, 'a') as f:
                f.write(f'\n# KosDWM PyQt5\n{path_line}\n')
            print_status(f"Added {install_bin} to PATH in {shell_rc}", "success")
            print(f"  Run 'source {shell_rc}' or restart terminal to apply")
            return True
    
    return False


def install(user_install=True):
    """Install KosDWM."""
    source_path = Path(__file__).parent.resolve()
    
    if user_install:
        install_bin = USER_BIN
        install_share = USER_SHARE
    else:
        install_bin = SYSTEM_BIN
        install_share = SYSTEM_SHARE
    
    print_status("Installing KosDWM PyQt5...", "info")
    print(f"Source: {source_path}")
    print(f"Install binaries to: {install_bin}")
    print(f"Install data to: {install_share}")
    
    # Create directories
    install_bin.mkdir(parents=True, exist_ok=True)
    install_share.mkdir(parents=True, exist_ok=True)
    
    # Check dependencies
    if not check_dependencies():
        print()
        response = input("Install dependencies now? [Y/n]: ")
        if response.lower() in ('', 'y', 'yes'):
            if not install_dependencies():
                return 1
    
    # Create launcher
    print_status("Creating launcher scripts...", "info")
    create_launcher_script(source_path, install_bin)
    
    # Create desktop entry
    print_status("Creating desktop entry...", "info")
    create_desktop_entry(source_path, install_share)
    
    # Add to PATH
    add_to_path(install_bin)
    
    print()
    print_status("Installation complete!", "success")
    print()
    print("You can now run KosDWM PyQt5 with:")
    print(f"  {Colors.BLUE}kosdwm-pyqt5{Colors.RESET}")
    print()
    print("Or from GUI applications menu.")
    
    return 0


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Install KosDWM PyQt5")
    parser.add_argument(
        "--user",
        action="store_true",
        default=True,
        help="Install to user directories (default)"
    )
    parser.add_argument(
        "--system",
        action="store_true",
        help="Install system-wide (requires sudo)"
    )
    
    args = parser.parse_args()
    
    user_install = not args.system
    
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}  KosDWM PyQt5 Installer{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")
    print()
    
    return install(user_install)


if __name__ == "__main__":
    sys.exit(main())
