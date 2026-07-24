#!/usr/bin/env python3
"""
Diagnose gadget configuration issue
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

print("=" * 60)
print("GADGET CONFIGURATION DIAGNOSTIC")
print("=" * 60)

# Test 1: GadgetManager standalone
print("\n1. Testing GadgetManager standalone...")
try:
    from gadgets_pyqt5 import GadgetManager
    
    gm = GadgetManager()
    print(f"   Gadgets dict: {list(gm.gadgets.keys())}")
    print(f"   Enabled list: {gm.enabled_gadgets}")
    
    all_gadgets = gm.get_all_gadgets()
    print(f"   get_all_gadgets() returned: {len(all_gadgets)} gadgets")
    
    for gadget in all_gadgets:
        name = gadget.get_name()
        info = gm.get_gadget_info(name)
        print(f"   - {name}: info={info}")
        
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Check config file
print("\n2. Checking config file...")
try:
    import json
    from pathlib import Path
    
    config_file = Path.home() / ".config" / "KosDWM" / "gadgets.json"
    print(f"   Config file path: {config_file}")
    print(f"   Exists: {config_file.exists()}")
    
    if config_file.exists():
        with open(config_file) as f:
            content = f.read()
            print(f"   Content: {content}")
            config = json.loads(content)
            print(f"   Parsed: {config}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 3: Simulate what Panel does
print("\n3. Simulating Panel flow...")
try:
    from gadgets_pyqt5 import GadgetManager
    
    # This is what Panel.__init__ does
    gm = GadgetManager()
    print(f"   Panel's gadget_manager has {len(gm.gadgets)} gadgets")
    print(f"   Enabled: {gm.enabled_gadgets}")
    
    # This is what open_gadget_config does
    all_gadgets = gm.get_all_gadgets()
    print(f"   Passing {len(all_gadgets)} gadgets to dialog")
    
    # This is what GadgetConfigDialog does
    for gadget in all_gadgets:
        info = gm.get_gadget_info(gadget.get_name())
        print(f"   Dialog would add: {info}")
        
except Exception as e:
    print(f"   ✗ Error: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Check for import issues
print("\n4. Checking for import issues...")
try:
    # Check if notices_gadget loads
    try:
        from notices_gadget_pyqt5 import NoticesGadget
        print("   ✓ NoticesGadget imports successfully")
    except ImportError as e:
        print(f"   ✗ NoticesGadget import failed: {e}")
        
    # Check gadget_config_pyqt5
    try:
        from gadget_config_pyqt5 import GadgetConfigDialog
        print("   ✓ GadgetConfigDialog imports successfully")
    except ImportError as e:
        print(f"   ✗ GadgetConfigDialog import failed: {e}")
        
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n" + "=" * 60)
print("DIAGNOSTIC COMPLETE")
print("=" * 60)
print("""
If you see gadgets above but not in the UI, the issue is in the dialog.

Next steps:
1. Run: python main_pyqt5.py -d
2. Open Config → Manage Gadgets
3. Check console output for [GadgetConfig] messages
""")
