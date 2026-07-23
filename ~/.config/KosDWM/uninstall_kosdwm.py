#!/usr/bin/env python3
"""
KosDWM Uninstaller
==================

Removes KosDWM installation files.

Usage:
    python uninstall_kosdwm.py          # Remove user installation
    python uninstall_kosdwm.py --system   # Remove system installation (requires sudo)
"""

import os
import sys
import argparse
from pathlib import Path


USER_BIN = Path.home() / ".local" / "bin"
USER_SHARE = Path.home() / ".local" / "share" / "kosdwm"
USER_CONFIG = Path.home() / ".config" / "KosDWM"
SYSTEM_BIN = Path("/usr/local/bin")
SYSTEM_SHARE = Path("/usr/local/share/kosdwm")


def remove_file(path, dry_run=False):
    """Remove a file, optionally dry-run."""
    if not path.exists():
        return False
    
    if dry_run:
        print(f"Would remove: {path}")
    else:
        path.unlink()
        print(f"Removed: {path}")
    return True


def remove_dir(path, dry_run=False):
    """Remove a directory if empty, optionally dry-run."""
    if not path.exists():
        return False
    
    try:
        if dry_run:
            print(f"Would remove dir: {path}")
        else:
            path.rmdir()
            print(f"Removed dir: {path}")
        return True
    except OSError:
        # Directory not empty
        return False


def uninstall(user_install=True, dry_run=False):
    """Uninstall KosDWM."""
    
    if user_install:
        install_bin = USER_BIN
        install_share = USER_SHARE
    else:
        install_bin = SYSTEM_BIN
        install_share = SYSTEM_SHARE
    
    print("KosDWM Uninstaller")
    print("=" * 60)
    print()
    
    if dry_run:
        print("DRY RUN - No files will be deleted")
        print()
    
    # Files to remove
    files_to_remove = [
        install_bin / "kosdwm",
        install_bin / "kosdwm-panel",
        install_share / "config",
        Path.home() / ".local" / "share" / "applications" / "kosdwm.desktop",
    ]
    
    removed = 0
    for f in files_to_remove:
        if remove_file(f, dry_run):
            removed += 1
    
    # Try to remove directories
    dirs_to_remove = [
        install_share,
    ]
    
    for d in dirs_to_remove:
        if remove_dir(d, dry_run):
            removed += 1
    
    print()
    print(f"{'Would remove' if dry_run else 'Removed'} {removed} items")
    print()
    
    # Note about config
    if USER_CONFIG.exists():
        print(f"Note: Configuration directory not removed: {USER_CONFIG}")
        print("      (Contains your settings and gadgets)")
        print("      To remove it manually: rm -rf ~/.config/KosDWM")
    
    return 0


def main():
    parser = argparse.ArgumentParser(description="Uninstall KosDWM")
    parser.add_argument("--system", action="store_true", help="Remove system installation")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be removed")
    
    args = parser.parse_args()
    
    user_install = not args.system
    
    if args.system and os.geteuid() != 0:
        print("Error: System uninstall requires sudo")
        print("       sudo python uninstall_kosdwm.py --system")
        return 1
    
    return uninstall(user_install, args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
