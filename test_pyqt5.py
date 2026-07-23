#!/usr/bin/env python3
"""
Test script for KosDWM PyQt5
Run this after installing PyQt5 to verify everything works.
"""

import sys
import os

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        from PyQt5.QtWidgets import QApplication
        print("✓ PyQt5 available")
    except ImportError as e:
        print(f"✗ PyQt5 not available: {e}")
        print("Install with: pip install PyQt5")
        return False
    
    sys.path.insert(0, 'src')
    
    try:
        from gadgets_pyqt5 import GadgetManager, GadgetBase
        print("✓ gadgets_pyqt5 imported")
    except Exception as e:
        print(f"✗ gadgets_pyqt5 error: {e}")
        return False
    
    try:
        from panel_pyqt5 import Panel
        print("✓ panel_pyqt5 imported")
    except Exception as e:
        print(f"✗ panel_pyqt5 error: {e}")
        return False
    
    try:
        from desktop_manager_pyqt5 import DesktopManager
        print("✓ desktop_manager_pyqt5 imported")
    except Exception as e:
        print(f"✗ desktop_manager_pyqt5 error: {e}")
        return False
    
    try:
        from menus_pyqt5 import MenuManager
        print("✓ menus_pyqt5 imported")
    except Exception as e:
        print(f"✗ menus_pyqt5 error: {e}")
        return False
    
    try:
        from gadget_config_pyqt5 import GadgetConfigDialog
        print("✓ gadget_config_pyqt5 imported")
    except Exception as e:
        print(f"✗ gadget_config_pyqt5 error: {e}")
        return False
    
    return True


def test_gadgets():
    """Test gadget manager"""
    print("\nTesting GadgetManager...")
    
    sys.path.insert(0, 'src')
    from gadgets_pyqt5 import GadgetManager
    
    gm = GadgetManager()
    
    available = gm.get_available_gadgets()
    print(f"Available gadgets: {available}")
    
    enabled = gm.get_enabled_gadgets()
    print(f"Enabled gadgets: {[g.get_name() for g in enabled]}")
    
    # Check that we have at least hello_world and test_gadget
    assert "hello_world" in available, "hello_world not found"
    assert "test_gadget" in available, "test_gadget not found"
    
    print("✓ GadgetManager working")
    return True


def test_desktop_manager():
    """Test desktop manager"""
    print("\nTesting DesktopManager...")
    
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    
    sys.path.insert(0, 'src')
    from desktop_manager_pyqt5 import DesktopManager
    
    dm = DesktopManager()
    print(f"Current desktop: {dm.current_desktop}")
    print(f"Total desktops: {dm.total_desktops}")
    
    print("✓ DesktopManager working")
    return True


def main():
    """Run all tests"""
    print("="*60)
    print("KosDWM PyQt5 Test Suite")
    print("="*60)
    print()
    
    # Test imports
    if not test_imports():
        print("\n✗ Import tests failed")
        return 1
    
    # Test gadgets
    if not test_gadgets():
        print("\n✗ Gadget tests failed")
        return 1
    
    # Test desktop manager
    if not test_desktop_manager():
        print("\n✗ Desktop manager tests failed")
        return 1
    
    print("\n" + "="*60)
    print("All tests passed! ✓")
    print("="*60)
    print()
    print("To run KosDWM PyQt5:")
    print("  python main_pyqt5.py")
    print()
    print("Or install with:")
    print("  python install_kosdwm_pyqt5.py --user")
    print("  kosdwm-pyqt5")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
