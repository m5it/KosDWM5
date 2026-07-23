#!/usr/bin/env python3
"""
Clear Python Cache Files
========================

Removes __pycache__ directories and .pyc files from the project.
Useful for cleaning up stale compiled Python files.

Usage:
    python clearcache.py          # Clean current directory
    python clearcache.py /path    # Clean specific directory
"""

import os
import sys
from pathlib import Path


def clear_cache(directory="."):
    """
    Remove all __pycache__ directories and .pyc files.
    
    Args:
        directory: Root directory to clean (default: current directory)
    """
    root = Path(directory).resolve()
    
    if not root.exists():
        print(f"Error: Directory not found: {root}")
        return 1
    
    print(f"Cleaning Python cache in: {root}")
    print()
    
    removed_dirs = 0
    removed_files = 0
    
    # Walk through directory tree
    for path in root.rglob("*"):
        try:
            if path.is_dir() and path.name == "__pycache__":
                # Remove __pycache__ directory
                import shutil
                shutil.rmtree(path)
                print(f"  Removed dir:  {path.relative_to(root)}")
                removed_dirs += 1
            
            elif path.is_file() and path.suffix == ".pyc":
                # Remove .pyc file
                path.unlink()
                print(f"  Removed file: {path.relative_to(root)}")
                removed_files += 1
                
        except PermissionError as e:
            print(f"  Permission denied: {path} ({e})")
        except Exception as e:
            print(f"  Error removing {path}: {e}")
    
    print()
    print(f"Summary:")
    print(f"  Directories removed: {removed_dirs}")
    print(f"  Files removed: {removed_files}")
    print(f"  Total items: {removed_dirs + removed_files}")
    
    return 0


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        # Use provided directory
        directory = sys.argv[1]
    else:
        # Use current directory
        directory = "."
    
    return clear_cache(directory)


if __name__ == "__main__":
    sys.exit(main())
