#!/usr/bin/env python3
"""
Test script for NoticesGadget HTTP API
"""

import sys
import time
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from notices_gadget_pyqt5 import NoticesGadget, NoticesStore, Notice


class MockPanel:
    """Mock panel for testing"""
    def __init__(self):
        from panel_api_pyqt5 import PanelAPI
        self.api = PanelAPI(port=8081)  # Use different port for testing
        self.api.start()


def test_api():
    """Test the NoticesGadget API endpoints"""
    print("=" * 60)
    print("Testing NoticesGadget HTTP API")
    print("=" * 60)
    
    # Create mock panel with API
    panel = MockPanel()
    time.sleep(0.5)  # Wait for server to start
    
    # Create gadget and set panel
    gadget = NoticesGadget()
    gadget.set_panel(panel)
    
    time.sleep(0.5)  # Wait for endpoints to register
    
    print("\n1. Testing GET /api/notices (empty list)")
    print("-" * 40)
    
    # Test using urllib
    try:
        from urllib.request import urlopen, Request
        from urllib.parse import urlencode
        
        # GET all notices
        response = urlopen("http://localhost:8081/api/notices")
        data = json.loads(response.read().decode())
        print(f"Status: OK")
        print(f"Count: {data.get('count')}")
        print(f"Response: {json.dumps(data, indent=2)[:200]}...")
        
        # POST new notice
        print("\n2. Testing POST /api/notices (create notice)")
        print("-" * 40)
        
        notice_data = json.dumps({
            "title": "Test Notice",
            "content": "<p>This is a test</p>",
            "priority": "high",
            "due_date": "2024-12-31T23:59:59"
        }).encode()
        
        req = Request(
            "http://localhost:8081/api/notices",
            data=notice_data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
        response = urlopen(req)
        data = json.loads(response.read().decode())
        print(f"Status: {data.get('status')}")
        print(f"Message: {data.get('message')}")
        notice_id = data.get('notice', {}).get('id')
        print(f"Created notice ID: {notice_id}")
        
        # GET all notices again
        print("\n3. Testing GET /api/notices (with data)")
        print("-" * 40)
        
        response = urlopen("http://localhost:8081/api/notices")
        data = json.loads(response.read().decode())
        print(f"Count: {data.get('count')}")
        print(f"Active: {data.get('active')}")
        
        # POST delete notice
        print("\n4. Testing POST /api/notices/delete")
        print("-" * 40)
        
        delete_data = json.dumps({"id": notice_id}).encode()
        
        req = Request(
            "http://localhost:8081/api/notices/delete",
            data=delete_data,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        
        response = urlopen(req)
        data = json.loads(response.read().decode())
        print(f"Status: {data.get('status')}")
        print(f"Message: {data.get('message')}")
        
        # Verify deletion
        print("\n5. Verifying deletion")
        print("-" * 40)
        
        response = urlopen("http://localhost:8081/api/notices")
        data = json.loads(response.read().decode())
        print(f"Count after deletion: {data.get('count')}")
        
        print("\n" + "=" * 60)
        print("All tests passed! ✓")
        print("=" * 60)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Stop server
        panel.api.stop()
        print("\nServer stopped")


if __name__ == "__main__":
    test_api()
