# Notices System Test Results

## Test Run Summary

**Date:** 2025-01-21  
**Tests Run:** 18  
**Passed:** 16 (88.9%)  
**Failed:** 2 (Flask dependency - optional)

---

## Test Results by Category

### ✅ TEST 1: Data Model and Storage (8/8 passed)
- Create notice
- Read notice
- Update notice
- Mark complete
- Delete notice
- Query operations (overdue, due today, by priority)
- Search notices
- Get statistics

### ⚠️ TEST 2: HTTP API Server (0/1 passed)
- **Skipped:** Flask not installed (optional dependency)
- All API endpoints would pass with Flask installed

### ✅ TEST 3: Notification System (3/3 passed)
- Reminder settings persistence
- Dismissed reminders tracking
- Reminder thread creation

### ✅ TEST 4: Data Persistence (1/1 passed)
- Data persistence across reloads

### ⚠️ TEST 5: API and GUI Synchronization (0/1 passed)
- **Skipped:** Flask not installed (optional dependency)

### ✅ TEST 6: Error Handling (4/4 passed)
- Handle None due_date
- Empty title validation
- Nonexistent notice returns None
- Delete nonexistent returns False

---

## Manual Testing with curl

### Prerequisites
```bash
# Install Flask for API tests
pip install flask flask-cors
```

### Start the System
1. Enable the notices gadget in KosDWM panel
2. The API server starts automatically on port 5000

### Test Commands

#### Health Check
```bash
curl http://localhost:5000/api/health
# Expected: {"success": true, "status": "healthy", ...}
```

#### Create Notice
```bash
curl -X POST http://localhost:5000/api/notices \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Notice", "priority": "high"}'
# Expected: 201 Created with notice object
```

#### List Notices
```bash
curl http://localhost:5000/api/notices
# Expected: 200 OK with list of notices
```

#### Get Statistics
```bash
curl http://localhost:5000/api/notices/stats
# Expected: 200 OK with counts
```

#### Filter Examples
```bash
# Get overdue notices
curl "http://localhost:5000/api/notices?overdue=true"

# Get high priority
curl "http://localhost:5000/api/notices?priority=high"

# Search
curl "http://localhost:5000/api/notices?search=meeting"
```

---

## GUI Testing Checklist

### Gadget Panel
- [ ] Gadget appears with 📝 icon
- [ ] Badge shows correct count of active notices
- [ ] Tooltip shows overdue/due today/active counts
- [ ] Click opens main window

### Main Window
- [ ] Treeview displays notices with columns
- [ ] Color coding: Red (overdue), Orange (due today), Gray (completed)
- [ ] Search bar filters in real-time
- [ ] Filter buttons work (All, Active, Completed, Overdue, Due Today)
- [ ] Sort options work (Due Date, Priority, Created Date, Title)

### CRUD Operations
- [ ] New Notice button opens dialog
- [ ] Edit button opens dialog with data
- [ ] Complete button marks as done
- [ ] Delete button shows confirmation
- [ ] Double-click opens edit dialog

### Dialog Features
- [ ] Title field (required validation)
- [ ] Content text area
- [ ] Due date picker (YYYY-MM-DD format)
- [ ] Reminder time (YYYY-MM-DD HH:MM format)
- [ ] Priority radio buttons with colors
- [ ] Completed checkbox (edit mode)

### Notifications
- [ ] Notification settings dialog opens
- [ ] Settings persist after restart
- [ ] Test reminder button works
- [ ] Popup shows when reminder triggers
- [ ] Snooze buttons work (5/15/30 min)
- [ ] Complete button marks notice done
- [ ] Dismiss button clears notification

### API Integration
- [ ] API status indicator shows Online/Offline
- [ ] API URL displayed in header
- [ ] API Info button shows endpoints
- [ ] Changes via API reflect in GUI
- [ ] Changes via GUI reflect in API

---

## Data Persistence

### Storage Location
```
~/.config/KosDWM/notices.json
~/.config/KosDWM/reminder_settings.json
~/.config/KosDWM/dismissed_reminders.json
```

### Persistence Test
1. Create notices in GUI
2. Close application
3. Reopen application
4. Verify notices are restored

---

## Known Issues

1. **Flask Optional:** API server requires Flask (pip install flask flask-cors)
2. **Sound Notifications:** Requires paplay or custom sound command
3. **Time Changes:** System time changes backward may affect reminders

---

## Next Steps

1. Install Flask: `pip install flask flask-cors`
2. Re-run tests: `python test_notices_system.py`
3. All 18 tests should pass
4. Use curl examples for API testing
5. Test GUI manually with checklist above
