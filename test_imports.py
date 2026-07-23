#!/usr/bin/env python3
"""
Simple import test for KosDWM PyQt5
"""

import sys
import ast

def check_file_syntax(filepath):
    """Check if a Python file has valid syntax"""
    try:
        with open(filepath) as f:
            ast.parse(f.read())
        return True, None
    except SyntaxError as e:
        return False, str(e)

def main():
    print("="*60)
    print("KosDWM PyQt5 Import Test")
    print("="*60)
    print()
    
    files_to_check = [
        "main_pyqt5.py",
        "src/gadgets_pyqt5.py",
        "src/panel_pyqt5.py",
        "src/desktop_manager_pyqt5.py",
        "src/menus_pyqt5.py",
        "src/gadget_config_pyqt5.py",
        "src/notices_gadget_pyqt5.py",
    ]
    
    all_ok = True
    for filepath in files_to_check:
        ok, error = check_file_syntax(filepath)
        if ok:
            print(f"✓ {filepath} - syntax OK")
        else:
            print(f"✗ {filepath} - syntax error: {error}")
            all_ok = False
    
    print()
    if all_ok:
        print("All files have valid syntax!")
        print()
        print("To test with GUI, run on a system with X11/Wayland:")
        print("  python test_pyqt5.py")
        print()
        print("To run KosDWM PyQt5:")
        print("  python main_pyqt5.py")
    else:
        print("Some files have syntax errors. Please fix them.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
