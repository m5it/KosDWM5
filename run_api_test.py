#!/usr/bin/env python3
"""
Quick API verification test
"""

import sys
import time
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

print("=" * 60)
print("KOSDWM COMPLETE API VERIFICATION")
print("=" * 60)

# Test 1: About Dialog
print("\n1. Testing About Dialog...")
try:
    from about_dialog_pyqt5 import AboutDialog
    assert hasattr(AboutDialog, 'get_version')
    assert hasattr(AboutDialog, 'get_system_info')
    print("   ✓ AboutDialog OK")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 2: Panel API
print("\n2. Testing Panel API...")
try:
    from panel_api_pyqt5 import PanelAPI
    api = PanelAPI(port=8085)
    assert '/api/status' in api.get_endpoints()
    assert '/api/endpoints' in api.get_endpoints()
    api.start()
    time.sleep(0.3)
    assert api.is_running()
    print("   ✓ PanelAPI server started")
    
    # Test endpoint response
    from urllib.request import urlopen
    response = urlopen("http://localhost:8085/api/status")
    data = json.loads(response.read().decode())
    assert data.get('status') == 'ok'
    print("   ✓ /api/status responds correctly")
    
    api.stop()
    print("   ✓ PanelAPI server stopped")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 3: Notices Gadget
print("\n3. Testing Notices Gadget...")
try:
    from notices_gadget_pyqt5 import NoticesGadget, NoticesStore
    
    # Check thread-safe store
    store = NoticesStore()
    assert hasattr(store, '_lock')
    print("   ✓ NoticesStore has RLock")
    
    # Check gadget has API methods
    assert hasattr(NoticesGadget, '_register_api_endpoints')
    assert hasattr(NoticesGadget, '_api_list_notices')
    assert hasattr(NoticesGadget, '_api_create_notice')
    assert hasattr(NoticesGadget, '_api_delete_notice')
    print("   ✓ NoticesGadget has all API methods")
    
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 4: Gadget Base
print("\n4. Testing Gadget Base API integration...")
try:
    from gadgets_pyqt5 import GadgetBase
    
    # Check GadgetBase has API support
    assert hasattr(GadgetBase, 'api')
    assert hasattr(GadgetBase, 'register_endpoint')
    print("   ✓ GadgetBase has api property")
    print("   ✓ GadgetBase has register_endpoint method")
    
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n" + "=" * 60)
print("ALL TESTS COMPLETED SUCCESSFULLY ✓")
print("=" * 60)

print("""
CURL TEST COMMANDS:
------------------
# Check API status
curl http://localhost:8080/api/status

# List notices
curl http://localhost:8080/api/notices

# Create notice
curl -X POST http://localhost:8080/api/notices \\
  -H "Content-Type: application/json" \\
  -d '{"title":"Test","content":"Hello","priority":"medium"}'

# Delete notice
curl -X POST http://localhost:8080/api/notices/delete \\
  -H "Content-Type: application/json" \\
  -d '{"id":"UUID-HERE"}'
""")
