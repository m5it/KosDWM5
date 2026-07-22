#!/usr/bin/env python3
"""
Notices System Test Suite
==========================

Comprehensive tests for the notices gadget, API, and notification system.
"""

import json
import sys
import time
import threading
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.notices_store import NoticesStore, Notice

# Try to import optional dependencies
try:
    from src.notices_api import NoticesAPIServer
    API_AVAILABLE = True
except ImportError as e:
    print(f"Warning: API server not available: {e}")
    API_AVAILABLE = False

try:
    from src.notifications import ReminderThread, ReminderSettings
    NOTIFICATIONS_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Notifications not available: {e}")
    NOTIFICATIONS_AVAILABLE = False


class Colors:
    """Terminal colors for test output."""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'


def print_header(text):
    """Print a test section header."""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BLUE}{'='*60}{Colors.RESET}")


def print_test(name, passed, details=""):
    """Print test result."""
    status = f"{Colors.GREEN}PASS" if passed else f"{Colors.RED}FAIL"
    print(f"  [{status}{Colors.RESET}] {name}")
    if details and not passed:
        print(f"       {Colors.YELLOW}→ {details}{Colors.RESET}")


def http_get(url):
    """Simple HTTP GET using urllib."""
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            return response.status, json.loads(response.read().decode())
    except Exception as e:
        return None, str(e)


def http_post(url, data):
    """Simple HTTP POST using urllib."""
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode(),
            headers={'Content-Type': 'application/json'},
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.status, json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())
    except Exception as e:
        return None, str(e)


def http_put(url, data):
    """Simple HTTP PUT using urllib."""
    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode(),
            headers={'Content-Type': 'application/json'},
            method='PUT'
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.status, json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())
    except Exception as e:
        return None, str(e)


def http_delete(url):
    """Simple HTTP DELETE using urllib."""
    try:
        req = urllib.request.Request(url, method='DELETE')
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.status, json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read().decode())
    except Exception as e:
        return None, str(e)


def test_data_model():
    """Test 1: Data model and storage."""
    print_header("TEST 1: Data Model and Storage")
    
    passed = 0
    failed = 0
    
    # Test 1.1: Create notice
    try:
        store = NoticesStore()
        notice = store.create(
            title="Test Notice",
            content="Test content",
            due_date=datetime.now() + timedelta(days=1),
            priority="high"
        )
        print_test("Create notice", True)
        passed += 1
    except Exception as e:
        print_test("Create notice", False, str(e))
        failed += 1
        return passed, failed
    
    # Test 1.2: Read notice
    try:
        retrieved = store.get(notice.id)
        assert retrieved.title == "Test Notice"
        print_test("Read notice", True)
        passed += 1
    except Exception as e:
        print_test("Read notice", False, str(e))
        failed += 1
    
    # Test 1.3: Update notice
    try:
        store.update(notice.id, title="Updated Title")
        updated = store.get(notice.id)
        assert updated.title == "Updated Title"
        print_test("Update notice", True)
        passed += 1
    except Exception as e:
        print_test("Update notice", False, str(e))
        failed += 1
    
    # Test 1.4: Mark complete
    try:
        store.mark_completed(notice.id, True)
        completed = store.get(notice.id)
        assert completed.completed == True
        print_test("Mark complete", True)
        passed += 1
    except Exception as e:
        print_test("Mark complete", False, str(e))
        failed += 1
    
    # Test 1.5: Delete notice
    try:
        store.delete(notice.id)
        deleted = store.get(notice.id)
        assert deleted is None
        print_test("Delete notice", True)
        passed += 1
    except Exception as e:
        print_test("Delete notice", False, str(e))
        failed += 1
    
    # Test 1.6: Query operations
    try:
        # Create test data
        store.create("Overdue Notice", due_date=datetime.now() - timedelta(days=1))
        store.create("Due Today", due_date=datetime.now())
        store.create("Future Notice", due_date=datetime.now() + timedelta(days=7))
        store.create("High Priority", priority="high")
        
        overdue = store.get_overdue()
        due_today = store.get_due_today()
        high = store.get_by_priority("high")
        
        assert len(overdue) >= 1, "Should have overdue notices"
        assert len(due_today) >= 1, "Should have due today notices"
        assert len(high) >= 1, "Should have high priority notices"
        print_test("Query operations", True)
        passed += 1
    except Exception as e:
        print_test("Query operations", False, str(e))
        failed += 1
    
    # Test 1.7: Search
    try:
        results = store.search("Future")
        assert len(results) >= 1
        print_test("Search notices", True)
        passed += 1
    except Exception as e:
        print_test("Search notices", False, str(e))
        failed += 1
    
    # Test 1.8: Statistics
    try:
        stats = store.get_stats()
        assert "total" in stats
        assert "active" in stats
        assert "overdue" in stats
        print_test("Get statistics", True)
        passed += 1
    except Exception as e:
        print_test("Get statistics", False, str(e))
        failed += 1
    
    return passed, failed


def test_api_server():
    """Test 2: HTTP API server."""
    print_header("TEST 2: HTTP API Server")
    
    if not API_AVAILABLE:
        print_test("API module available", False, "NoticesAPIServer not importable")
        return 0, 1
    
    passed = 0
    failed = 0
    
    # Start API server
    try:
        store = NoticesStore()
        server = NoticesAPIServer(store=store, port=5001)
        server.start(threaded=True)
        time.sleep(1)  # Wait for server to start
        base_url = "http://localhost:5001"
        print_test("Start API server", True)
        passed += 1
    except Exception as e:
        print_test("Start API server", False, str(e))
        return passed, failed
    
    # Test 2.1: Health check
    try:
        status, data = http_get(f"{base_url}/api/health")
        assert status == 200
        assert data["success"] == True
        print_test("Health check endpoint", True)
        passed += 1
    except Exception as e:
        print_test("Health check endpoint", False, str(e))
        failed += 1
    
    # Test 2.2: Create notice via API
    try:
        status, data = http_post(
            f"{base_url}/api/notices",
            {
                "title": "API Test Notice",
                "content": "Created via API",
                "due_date": (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
                "priority": "medium"
            }
        )
        assert status == 201, f"Expected 201, got {status}: {data}"
        assert data["success"] == True
        created_id = data["notice"]["id"]
        print_test("Create notice via API", True)
        passed += 1
    except Exception as e:
        print_test("Create notice via API", False, str(e))
        failed += 1
        return passed, failed
    
    # Test 2.3: Get notice via API
    try:
        status, data = http_get(f"{base_url}/api/notices/{created_id}")
        assert status == 200
        assert data["notice"]["title"] == "API Test Notice"
        print_test("Get notice via API", True)
        passed += 1
    except Exception as e:
        print_test("Get notice via API", False, str(e))
        failed += 1
    
    # Test 2.4: List notices via API
    try:
        status, data = http_get(f"{base_url}/api/notices")
        assert status == 200
        assert "notices" in data
        assert len(data["notices"]) >= 1
        print_test("List notices via API", True)
        passed += 1
    except Exception as e:
        print_test("List notices via API", False, str(e))
        failed += 1
    
    # Test 2.5: Update notice via API
    try:
        status, data = http_put(
            f"{base_url}/api/notices/{created_id}",
            {"title": "Updated API Notice"}
        )
        assert status == 200
        assert data["notice"]["title"] == "Updated API Notice"
        print_test("Update notice via API", True)
        passed += 1
    except Exception as e:
        print_test("Update notice via API", False, str(e))
        failed += 1
    
    # Test 2.6: Complete notice via API
    try:
        status, data = http_post(
            f"{base_url}/api/notices/{created_id}/complete",
            {"completed": True}
        )
        assert status == 200
        assert data["completed"] == True
        print_test("Complete notice via API", True)
        passed += 1
    except Exception as e:
        print_test("Complete notice via API", False, str(e))
        failed += 1
    
    # Test 2.7: Get stats via API
    try:
        status, data = http_get(f"{base_url}/api/notices/stats")
        assert status == 200
        assert "stats" in data
        print_test("Get stats via API", True)
        passed += 1
    except Exception as e:
        print_test("Get stats via API", False, str(e))
        failed += 1
    
    # Test 2.8: Delete notice via API
    try:
        status, data = http_delete(f"{base_url}/api/notices/{created_id}")
        assert status == 200
        print_test("Delete notice via API", True)
        passed += 1
    except Exception as e:
        print_test("Delete notice via API", False, str(e))
        failed += 1
    
    # Test 2.9: Error handling - 404
    try:
        status, data = http_get(f"{base_url}/api/notices/nonexistent-id")
        assert status == 404
        print_test("404 error handling", True)
        passed += 1
    except Exception as e:
        print_test("404 error handling", False, str(e))
        failed += 1
    
    # Test 2.10: Error handling - 400
    try:
        status, data = http_post(
            f"{base_url}/api/notices",
            {}  # Missing title
        )
        assert status == 400
        print_test("400 error handling", True)
        passed += 1
    except Exception as e:
        print_test("400 error handling", False, str(e))
        failed += 1
    
    # Stop server
    server.stop()
    
    return passed, failed


def test_notification_system():
    """Test 3: Notification system."""
    print_header("TEST 3: Notification System")
    
    if not NOTIFICATIONS_AVAILABLE:
        print_test("Notifications module available", False, "Notifications not importable")
        return 0, 1
    
    passed = 0
    failed = 0
    
    # Test 3.1: Reminder settings
    try:
        from src.notifications import ReminderSettings
        settings = ReminderSettings()
        settings.set("test_key", "test_value")
        assert settings.get("test_key") == "test_value"
        print_test("Reminder settings persistence", True)
        passed += 1
    except Exception as e:
        print_test("Reminder settings persistence", False, str(e))
        failed += 1
    
    # Test 3.2: Dismissed reminders
    try:
        from src.notifications import DismissedReminders
        dismissed = DismissedReminders()
        dismissed.dismiss("test-notice-123")
        assert dismissed.is_dismissed("test-notice-123") == True
        dismissed.clear("test-notice-123")
        assert dismissed.is_dismissed("test-notice-123") == False
        print_test("Dismissed reminders tracking", True)
        passed += 1
    except Exception as e:
        print_test("Dismissed reminders tracking", False, str(e))
        failed += 1
    
    # Test 3.3: Reminder thread creation
    try:
        store = NoticesStore()
        settings = ReminderSettings()
        settings.set("enabled", False)  # Disable to avoid actual notifications
        
        thread = ReminderThread(store, settings=settings)
        assert thread._running == False  # Not started yet
        print_test("Reminder thread creation", True)
        passed += 1
    except Exception as e:
        print_test("Reminder thread creation", False, str(e))
        failed += 1
    
    return passed, failed


def test_data_persistence():
    """Test 4: Data persistence across reloads."""
    print_header("TEST 4: Data Persistence")
    
    passed = 0
    failed = 0
    
    # Create notice and reload store
    try:
        store1 = NoticesStore()
        test_id = f"persistence-test-{int(time.time())}"
        
        # Create with specific ID by manipulating store directly
        notice = Notice(
            title="Persistence Test",
            content="Testing persistence",
            notice_id=test_id
        )
        
        # Access private store to add notice
        with store1._lock:
            store1._notices[test_id] = notice
        store1._save()
        
        # Create new store instance (simulates reload)
        store2 = NoticesStore()
        retrieved = store2.get(test_id)
        
        assert retrieved is not None, "Notice should persist"
        assert retrieved.title == "Persistence Test"
        
        # Cleanup
        store2.delete(test_id)
        
        print_test("Data persistence across reloads", True)
        passed += 1
    except Exception as e:
        print_test("Data persistence across reloads", False, str(e))
        failed += 1
    
    return passed, failed


def test_api_gui_sync():
    """Test 5: API and GUI synchronization."""
    print_header("TEST 5: API and GUI Synchronization")
    
    if not API_AVAILABLE:
        print_test("API available for sync test", False, "API not available")
        return 0, 1
    
    passed = 0
    failed = 0
    
    try:
        # Create shared store
        store = NoticesStore()
        
        # Start API server with shared store
        server = NoticesAPIServer(store=store, port=5002)
        server.start(threaded=True)
        time.sleep(1)
        
        base_url = "http://localhost:5002"
        
        # Create notice via API
        status, data = http_post(
            f"{base_url}/api/notices",
            {"title": "Sync Test Notice", "priority": "high"}
        )
        created_id = data["notice"]["id"]
        
        # Verify it's in the shared store (simulating GUI access)
        notice_in_store = store.get(created_id)
        assert notice_in_store is not None, "Notice should be in shared store"
        assert notice_in_store.title == "Sync Test Notice"
        
        # Update via store (simulating GUI edit)
        store.update(created_id, title="Updated via GUI")
        
        # Verify via API
        status, data = http_get(f"{base_url}/api/notices/{created_id}")
        api_notice = data["notice"]
        assert api_notice["title"] == "Updated via GUI"
        
        # Cleanup
        store.delete(created_id)
        server.stop()
        
        print_test("API and GUI synchronization", True)
        passed += 1
    except Exception as e:
        print_test("API and GUI synchronization", False, str(e))
        failed += 1
    
    return passed, failed


def test_error_handling():
    """Test 6: Error handling and edge cases."""
    print_header("TEST 6: Error Handling")
    
    passed = 0
    failed = 0
    
    store = NoticesStore()
    
    # Test 6.1: Invalid date format
    try:
        # This should be handled gracefully
        notice = store.create("Test")
        # Try to update with invalid date - should not crash
        store.update(notice.id, due_date=None)  # None is valid
        print_test("Handle None due_date", True)
        passed += 1
    except Exception as e:
        print_test("Handle None due_date", False, str(e))
        failed += 1
    
    # Test 6.2: Empty title validation
    try:
        try:
            store.create("")  # Empty title
            print_test("Empty title validation", False, "Should have raised error")
            failed += 1
        except ValueError:
            print_test("Empty title validation", True)
            passed += 1
    except Exception as e:
        print_test("Empty title validation", False, str(e))
        failed += 1
    
    # Test 6.3: Nonexistent notice
    try:
        result = store.get("nonexistent-id-12345")
        assert result is None
        print_test("Nonexistent notice returns None", True)
        passed += 1
    except Exception as e:
        print_test("Nonexistent notice returns None", False, str(e))
        failed += 1
    
    # Test 6.4: Delete nonexistent notice
    try:
        result = store.delete("nonexistent-id-12345")
        assert result == False
        print_test("Delete nonexistent returns False", True)
        passed += 1
    except Exception as e:
        print_test("Delete nonexistent returns False", False, str(e))
        failed += 1
    
    return passed, failed


def print_curl_examples():
    """Print curl examples for manual testing."""
    print_header("CURL EXAMPLES FOR MANUAL TESTING")
    
    examples = """
# Health check
curl http://localhost:5000/api/health

# Create a notice
curl -X POST http://localhost:5000/api/notices \\
  -H "Content-Type: application/json" \\
  -d '{"title": "Test Notice", "priority": "high"}'

# List all notices
curl http://localhost:5000/api/notices

# Get specific notice (replace ID)
curl http://localhost:5000/api/notices/YOUR-NOTICE-ID

# Update notice
curl -X PUT http://localhost:5000/api/notices/YOUR-NOTICE-ID \\
  -H "Content-Type: application/json" \\
  -d '{"title": "Updated Title"}'

# Mark as complete
curl -X POST http://localhost:5000/api/notices/YOUR-NOTICE-ID/complete

# Delete notice
curl -X DELETE http://localhost:5000/api/notices/YOUR-NOTICE-ID

# Get statistics
curl http://localhost:5000/api/notices/stats

# Filter examples
curl "http://localhost:5000/api/notices?overdue=true"
curl "http://localhost:5000/api/notices?priority=high"
curl "http://localhost:5000/api/notices?completed=false"
"""
    print(examples)


def run_all_tests():
    """Run all tests and print summary."""
    print(f"\n{Colors.BLUE}╔══════════════════════════════════════════════════════════════╗{Colors.RESET}")
    print(f"{Colors.BLUE}║         NOTICES SYSTEM TEST SUITE                            ║{Colors.RESET}")
    print(f"{Colors.BLUE}╚══════════════════════════════════════════════════════════════╝{Colors.RESET}")
    
    total_passed = 0
    total_failed = 0
    
    # Run tests
    tests = [
        test_data_model,
        test_api_server,
        test_notification_system,
        test_data_persistence,
        test_api_gui_sync,
        test_error_handling,
    ]
    
    for test_func in tests:
        p, f = test_func()
        total_passed += p
        total_failed += f
    
    # Summary
    print_header("TEST SUMMARY")
    total = total_passed + total_failed
    
    print(f"\n  Total Tests: {total}")
    print(f"  {Colors.GREEN}Passed: {total_passed}{Colors.RESET}")
    print(f"  {Colors.RED}Failed: {total_failed}{Colors.RESET}")
    if total > 0:
        print(f"  Success Rate: {(total_passed/total)*100:.1f}%")
    
    if total_failed == 0:
        print(f"\n{Colors.GREEN}✓ All tests passed!{Colors.RESET}")
    else:
        print(f"\n{Colors.YELLOW}⚠ Some tests failed or were skipped.{Colors.RESET}")
    
    # Print curl examples
    print_curl_examples()
    
    return total_failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
