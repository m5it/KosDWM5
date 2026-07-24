#!/usr/bin/env python3
"""
Complete HTTP Panel API Test Suite
Tests: About dialog, Notices API, Multiple gadget endpoints
"""

import sys
import time
import json
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

def test_about_dialog():
    """Test About dialog imports and structure"""
    print("=" * 60)
    print("TEST 1: About Dialog")
    print("=" * 60)
    
    try:
        from about_dialog_pyqt5 import AboutDialog
        print("✓ AboutDialog imports successfully")
        
        # Check required methods
        assert hasattr(AboutDialog, 'get_version'), "Missing get_version"
        assert hasattr(AboutDialog, 'get_system_info'), "Missing get_system_info"
        assert hasattr(AboutDialog, 'apply_dark_theme'), "Missing apply_dark_theme"
        print("✓ All required methods present")
        
        # Test version retrieval
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('VERSION = "1.0.0-test"')
            temp_version = f.name
        
        # Mock the version file path
        import about_dialog_pyqt5
        original_path = about_dialog_pyqt5.__file__
        
        print("✓ About dialog structure verified")
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def test_panel_api():
    """Test PanelAPI initialization"""
    print("\n" + "=" * 60)
    print("TEST 2: Panel API Initialization")
    print("=" * 60)
    
    try:
        from panel_api_pyqt5 import PanelAPI
        
        # Create API on test port
        api = PanelAPI(port=8082)
        print("✓ PanelAPI created")
        
        # Check default endpoints
        endpoints = api.get_endpoints()
        assert '/api/status' in endpoints, "Missing /api/status"
        assert '/api/endpoints' in endpoints, "Missing /api/endpoints"
        print("✓ Default endpoints registered")
        
        # Test custom endpoint registration
        def test_handler(request):
            return {"test": "ok"}
        
        api.register("/api/test", test_handler, methods=["GET"])
        assert '/api/test' in api.get_endpoints(), "Custom endpoint not registered"
        print("✓ Custom endpoint registration works")
        
        # Start server
        api.start()
        time.sleep(0.3)
        assert api.is_running(), "Server not running"
        print("✓ Server started successfully")
        
        # Stop server
        api.stop()
        print("✓ Server stopped successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_notices_gadget():
    """Test NoticesGadget with HTTP endpoints"""
    print("\n" + "=" * 60)
    print("TEST 3: NoticesGadget HTTP Endpoints")
    print("=" * 60)
    
    try:
        from notices_gadget_pyqt5 import NoticesGadget, NoticesStore, Notice
        from panel_api_pyqt5 import PanelAPI
        
        # Create API server
        api = PanelAPI(port=8083)
        api.start()
        time.sleep(0.3)
        print("✓ Panel API server started on port 8083")
        
        # Create gadget and set panel
        gadget = NoticesGadget()
        
        # Mock panel with API
        class MockPanel:
            def __init__(self):
                self.api = api
        
        panel = MockPanel()
        gadget.set_panel(panel)
        time.sleep(0.5)
        print("✓ Gadget registered endpoints with panel")
        
        # Test using urllib
        from urllib.request import urlopen, Request
        
        # Test GET /api/notices
        response = urlopen("http://localhost:8083/api/notices")
        data = json.loads(response.read().decode())
        assert 'notices' in data, "Missing notices in response"
        assert 'count' in data, "Missing count in response"
        print(f"✓ GET /api/notices works (count: {data['count']})")
        
        # Test POST /api/notices
        notice_data = json.dumps({
            "title": "Test Notice",
            "content": "Test content",
            "priority": "high"
        }).encode()
        
        req = Request(
            "http://localhost:8083/api/notices",
            data=notice_data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
        response = urlopen(req)
        data = json.loads(response.read().decode())
        assert data.get('status') == 'success', "Failed to create notice"
        notice_id = data['notice']['id']
        print(f"✓ POST /api/notices works (created: {notice_id[:8]}...)")
        
        # Verify notice exists
        response = urlopen("http://localhost:8083/api/notices")
        data = json.loads(response.read().decode())
        assert data['count'] == 1, "Notice not found"
        print(f"✓ Notice persisted (count: {data['count']})")
        
        # Test POST /api/notices/delete
        delete_data = json.dumps({"id": notice_id}).encode()
        req = Request(
            "http://localhost:8083/api/notices/delete",
            data=delete_data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
        response = urlopen(req)
        data = json.loads(response.read().decode())
        assert data.get('status') == 'success', "Failed to delete notice"
        print("✓ POST /api/notices/delete works")
        
        # Verify deletion
        response = urlopen("http://localhost:8083/api/notices")
        data = json.loads(response.read().decode())
        assert data['count'] == 0, "Notice still exists"
        print("✓ Deletion verified")
        
        api.stop()
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multiple_gadgets():
    """Test multiple gadgets registering endpoints"""
    print("\n" + "=" * 60)
    print("TEST 4: Multiple Gadget Endpoints")
    print("=" * 60)
    
    try:
        from gadgets_pyqt5 import GadgetBase
        from panel_api_pyqt5 import PanelAPI
        
        # Create API server
        api = PanelAPI(port=8084)
        api.start()
        time.sleep(0.3)
        
        # Create multiple test gadgets
        class TestGadget1(GadgetBase):
            def get_name(self): return "test1"
            def get_icon(self): return "🔹"
            def get_tooltip(self): return "Test 1"
            def on_click(self): pass
            def set_panel(self, panel):
                super().set_panel(panel)
                self.register_endpoint("/api/test1", lambda r: {"gadget": "test1"})
        
        class TestGadget2(GadgetBase):
            def get_name(self): return "test2"
            def get_icon(self): return "🔸"
            def get_tooltip(self): return "Test 2"
            def on_click(self): pass
            def set_panel(self, panel):
                super().set_panel(panel)
                self.register_endpoint("/api/test2", lambda r: {"gadget": "test2"})
        
        class MockPanel:
            def __init__(self):
                self.api = api
        
        panel = MockPanel()
        
        # Register both gadgets
        gadget1 = TestGadget1()
        gadget1.set_panel(panel)
        
        gadget2 = TestGadget2()
        gadget2.set_panel(panel)
        
        time.sleep(0.3)
        
        # Verify both endpoints work
        from urllib.request import urlopen
        
        response = urlopen("http://localhost:8084/api/test1")
        data = json.loads(response.read().decode())
        assert data.get('gadget') == 'test1', "TestGadget1 endpoint failed"
        print("✓ Gadget 1 endpoint works")
        
        response = urlopen("http://localhost:8084/api/test2")
        data = json.loads(response.read().decode())
        assert data.get('gadget') == 'test2', "TestGadget2 endpoint failed"
        print("✓ Gadget 2 endpoint works")
        
        # Check all registered endpoints
        endpoints = api.get_endpoints()
        assert '/api/test1' in endpoints, "Test1 endpoint not registered"
        assert '/api/test2' in endpoints, "Test2 endpoint not registered"
        print(f"✓ All endpoints registered: {list(endpoints.keys())}")
        
        api.stop()
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def print_curl_examples():
    """Print curl commands for manual testing"""
    print("\n" + "=" * 60)
    print("CURL TEST COMMANDS")
    print("=" * 60)
    print("""
# Start KosDWM first, then test:

# 1. Check API status
curl http://localhost:8080/api/status | python -m json.tool

# 2. List all notices
curl http://localhost:8080/api/notices | python -m json.tool

# 3. Create a notice
curl -X POST http://localhost:8080/api/notices \\
  -H "Content-Type: application/json" \\
  -d '{"title":"Meeting","content":"<b>Team meeting</b>","priority":"high","due_date":"2024-12-31T10:00:00"}' \\
  | python -m json.tool

# 4. Delete a notice (replace ID)
curl -X POST http://localhost:8080/api/notices/delete \\
  -H "Content-Type: application/json" \\
  -d '{"id":"YOUR-NOTICE-ID-HERE"}' \\
  | python -m json.tool

# 5. List all registered endpoints
curl http://localhost:8080/api/endpoints | python -m json.tool
""")


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("KOSDWM COMPLETE API TEST SUITE")
    print("=" * 60)
    
    results = []
    
    results.append(("About Dialog", test_about_dialog()))
    results.append(("Panel API", test_panel_api()))
    results.append(("Notices Gadget", test_notices_gadget()))
    results.append(("Multiple Gadgets", test_multiple_gadgets()))
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    print_curl_examples()
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
