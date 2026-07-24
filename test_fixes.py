#!/usr/bin/env python3
"""
Test script to verify fixes for gadget configuration and debug mode
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

print("=" * 60)
print("Testing KosDWM Fixes")
print("=" * 60)

# Test 1: GadgetManager has reload_gadgets
print("\n1. Testing GadgetManager.reload_gadgets()...")
try:
    from gadgets_pyqt5 import GadgetManager
    gm = GadgetManager()
    assert hasattr(gm, 'reload_gadgets'), "Missing reload_gadgets method"
    print("   ✓ reload_gadgets method exists")
    
    # Test calling it
    gm.reload_gadgets()
    print("   ✓ reload_gadgets() executes successfully")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 2: GadgetConfigDialog can be imported
print("\n2. Testing GadgetConfigDialog import...")
try:
    from gadget_config_pyqt5 import GadgetConfigDialog
    print("   ✓ GadgetConfigDialog imports successfully")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 3: Panel has gadget_manager attribute
print("\n3. Testing Panel gadget_manager...")
try:
    from panel_pyqt5 import Panel
    # Check that load_gadgets sets gadget_manager
    import inspect
    source = inspect.getsource(Panel.load_gadgets)
    assert 'self.gadget_manager' in source, "gadget_manager not set in load_gadgets"
    print("   ✓ Panel sets self.gadget_manager")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 4: Debug flag parsing
print("\n4. Testing debug flag (-d)...")
try:
    # Just check the code exists
    with open('main_pyqt5.py') as f:
        content = f.read()
        assert 'argparse' in content, "argparse not imported"
        assert '--debug' in content or "-d" in content, "debug flag not defined"
        assert 'DEBUG' in content, "DEBUG variable not used"
    print("   ✓ Debug flag (-d) implemented in main_pyqt5.py")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 5: Verify no duplicate class definitions
print("\n5. Checking for duplicate class definitions...")
try:
    with open('src/gadgets_pyqt5.py') as f:
        content = f.read()
        # Count class definitions
        class_count = content.count('class GadgetBase')
        if class_count > 1:
            print(f"   ✗ Found {class_count} GadgetBase definitions - should be 1!")
        else:
            print(f"   ✓ GadgetBase defined once")
        
        # Check for duplicate method definitions in GadgetBase
        method_counts = {}
        for line in content.split('\n'):
            if line.strip().startswith('def ') and 'GadgetBase' not in line:
                method_name = line.split('(')[0].replace('def ', '').strip()
                if method_name in method_counts:
                    method_counts[method_name] += 1
                else:
                    method_counts[method_name] = 1
        
        duplicates = [m for m, c in method_counts.items() if c > 1]
        if duplicates:
            print(f"   ⚠ Duplicate methods found: {duplicates}")
        else:
            print("   ✓ No duplicate method definitions")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n" + "=" * 60)
print("Fix verification complete!")
print("=" * 60)
print("""
Usage:
  python main_pyqt5.py -d    # Run with debug output
  python main_pyqt5.py       # Run normally
  
In Config → Manage Gadgets:
  - Gadgets should now be visible
  - Reload button should work without error
""")
