# Notices HTTP API Documentation

## Overview

The Notices HTTP API provides RESTful endpoints for managing notices/reminders programmatically. The API server runs on `localhost:5000` by default and supports CORS for cross-origin requests.

## Base URL

```
http://localhost:5000/api
```

## Authentication

Currently, the API does not require authentication. It is intended for local use only.

## Content Type

All requests and responses use JSON format:
- Request: `Content-Type: application/json`
- Response: `application/json`

## Endpoints

### 1. Health Check

**GET** `/api/health`

Check if the API server is running.

**Response:**
```json
{
  "success": true,
  "status": "healthy",
  "timestamp": "2025-01-21T10:30:00"
}
```

**Example:**
```bash
curl http://localhost:5000/api/health
```

---

### 2. List All Notices

**GET** `/api/notices`

Retrieve all notices with optional filtering and sorting.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `completed` | boolean | Filter by completion status (`true` or `false`) |
| `overdue` | boolean | Get only overdue notices (`true`) |
| `due_today` | boolean | Get notices due today (`true`) |
| `priority` | string | Filter by priority (`low`, `medium`, `high`) |
| `search` | string | Search in title and content |

**Response:**
```json
{
  "success": true,
  "count": 3,
  "notices": [
    {
      "id": "uuid-here",
      "title": "Team Meeting",
      "content": "Weekly sync",
      "created_date": "2025-01-20T09:00:00",
      "due_date": "2025-01-21T14:00:00",
      "reminder_time": "2025-01-21T13:30:00",
      "priority": "high",
      "completed": false
    }
  ]
}
```

**Examples:**

```bash
# Get all notices
curl http://localhost:5000/api/notices

# Get active (non-completed) notices
curl "http://localhost:5000/api/notices?completed=false"

# Get overdue notices
curl "http://localhost:5000/api/notices?overdue=true"

# Get high priority notices
curl "http://localhost:5000/api/notices?priority=high"

# Search notices
curl "http://localhost:5000/api/notices?search=meeting"

# Combined filters
curl "http://localhost:5000/api/notices?completed=false&priority=high"
```

---

### 3. Get Single Notice

**GET** `/api/notices/{id}`

Retrieve a specific notice by ID.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | string | The notice UUID |

**Response:**
```json
{
  "success": true,
  "notice": {
    "id": "uuid-here",
    "title": "Team Meeting",
    "content": "Weekly sync",
    "created_date": "2025-01-20T09:00:00",
    "due_date": "2025-01-21T14:00:00",
    "reminder_time": "2025-01-21T13:30:00",
    "priority": "high",
    "completed": false
  }
}
```

**Example:**
```bash
curl http://localhost:5000/api/notices/123e4567-e89b-12d3-a456-426614174000
```

**Error Response (404):**
```json
{
  "success": false,
  "error": "Not found",
  "message": "Notice with ID 'xxx' not found"
}
```

---

### 4. Create Notice

**POST** `/api/notices`

Create a new notice.

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | Yes | Notice title (1-200 characters) |
| `content` | string | No | Detailed content |
| `due_date` | string | No | Due date in `YYYY-MM-DD` format |
| `reminder_time` | string | No | Reminder in `YYYY-MM-DD HH:MM` format |
| `priority` | string | No | Priority level: `low`, `medium` (default), `high` |

**Request Example:**
```json
{
  "title": "Submit Report",
  "content": "Quarterly sales report",
  "due_date": "2025-01-25",
  "reminder_time": "2025-01-25 09:00",
  "priority": "high"
}
```

**Response (201 Created):**
```json
{
  "success": true,
  "message": "Notice created successfully",
  "notice": {
    "id": "new-uuid-here",
    "title": "Submit Report",
    "content": "Quarterly sales report",
    "created_date": "2025-01-21T10:30:00",
    "due_date": "2025-01-25T00:00:00",
    "reminder_time": "2025-01-25T09:00:00",
    "priority": "high",
    "completed": false
  }
}
```

**Examples:**

```bash
# Simple notice
curl -X POST http://localhost:5000/api/notices \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy groceries"}'

# Full notice with all fields
curl -X POST http://localhost:5000/api/notices \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Doctor Appointment",
    "content": "Annual checkup",
    "due_date": "2025-02-15",
    "reminder_time": "2025-02-15 08:00",
    "priority": "high"
  }'
```

**Error Response (400):**
```json
{
  "success": false,
  "error": "Bad request",
  "message": "Title is required"
}
```

---

### 5. Update Notice

**PUT** `/api/notices/{id}`

Update an existing notice. All fields are optional - only provided fields are updated.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | string | The notice UUID |

**Request Body:**

Same as Create Notice, but all fields are optional.

**Request Example:**
```json
{
  "title": "Updated Title",
  "priority": "medium",
  "completed": true
}
```

**Response:**
```json
{
  "success": true,
  "message": "Notice updated successfully",
  "notice": {
    "id": "uuid-here",
    "title": "Updated Title",
    "content": "Original content",
    "created_date": "2025-01-20T09:00:00",
    "due_date": "2025-01-21T14:00:00",
    "reminder_time": "2025-01-21T13:30:00",
    "priority": "medium",
    "completed": true
  }
}
```

**Examples:**

```bash
# Update title
curl -X PUT http://localhost:5000/api/notices/123e4567-e89b-12d3-a456-426614174000 \
  -H "Content-Type: application/json" \
  -d '{"title": "New Title"}'

# Mark as completed
curl -X PUT http://localhost:5000/api/notices/123e4567-e89b-12d3-a456-426614174000 \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'

# Update due date
curl -X PUT http://localhost:5000/api/notices/123e4567-e89b-12d3-a456-426614174000 \
  -H "Content-Type: application/json" \
  -d '{"due_date": "2025-03-01"}'

# Clear due date
curl -X PUT http://localhost:5000/api/notices/123e4567-e89b-12d3-a456-426614174000 \
  -H "Content-Type: application/json" \
  -d '{"due_date": null}'
```

---

### 6. Delete Notice

**DELETE** `/api/notices/{id}`

Delete a notice permanently.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | string | The notice UUID |

**Response:**
```json
{
  "success": true,
  "message": "Notice deleted successfully"
}
```

**Example:**
```bash
curl -X DELETE http://localhost:5000/api/notices/123e4567-e89b-12d3-a456-426614174000
```

---

### 7. Mark Notice as Complete

**POST** `/api/notices/{id}/complete`

Toggle or set the completion status of a notice.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | string | The notice UUID |

**Request Body (optional):**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `completed` | boolean | `true` | Set completion status |

**Response:**
```json
{
  "success": true,
  "message": "Notice marked as completed",
  "completed": true
}
```

**Examples:**

```bash
# Mark as completed (default)
curl -X POST http://localhost:5000/api/notices/123e4567-e89b-12d3-a456-426614174000/complete

# Mark as completed explicitly
curl -X POST http://localhost:5000/api/notices/123e4567-e89b-12d3-a456-426614174000/complete \
  -H "Content-Type: application/json" \
  -d '{"completed": true}'

# Mark as not completed (reopen)
curl -X POST http://localhost:5000/api/notices/123e4567-e89b-12d3-a456-426614174000/complete \
  -H "Content-Type: application/json" \
  -d '{"completed": false}'
```

---

### 8. Get Statistics

**GET** `/api/notices/stats`

Get statistics about notices.

**Response:**
```json
{
  "success": true,
  "stats": {
    "total": 10,
    "active": 7,
    "completed": 3,
    "overdue": 2,
    "due_today": 1,
    "high_priority": 3
  }
}
```

**Example:**
```bash
curl http://localhost:5000/api/notices/stats
```

---

## Error Responses

### HTTP Status Codes

| Code | Meaning | Description |
|------|---------|-------------|
| 200 | OK | Request successful |
| 201 | Created | Resource created successfully |
| 400 | Bad Request | Invalid request data |
| 404 | Not Found | Resource not found |
| 405 | Method Not Allowed | HTTP method not supported |
| 500 | Internal Server Error | Server error |

### Error Response Format

```json
{
  "success": false,
  "error": "Error type",
  "message": "Human-readable error description"
}
```

---

## Common Use Cases

### Create a Quick Todo

```bash
curl -X POST http://localhost:5000/api/notices \
  -H "Content-Type: application/json" \
  -d '{"title": "Call mom"}'
```

### Create a Notice with Reminder

```bash
curl -X POST http://localhost:5000/api/notices \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Team Meeting",
    "content": "Discuss Q1 roadmap",
    "due_date": "2025-01-22",
    "reminder_time": "2025-01-22 09:30",
    "priority": "high"
  }'
```

### Get All Overdue Notices

```bash
curl "http://localhost:5000/api/notices?overdue=true"
```

### Complete All Notices from API

```bash
# Get all active notices
curl -s "http://localhost:5000/api/notices?completed=false" | \
  jq -r '.notices[].id' | \
  while read id; do
    curl -X POST "http://localhost:5000/api/notices/$id/complete"
  done
```

### Export Notices

```bash
curl -s http://localhost:5000/api/notices | jq '.notices' > notices_backup.json
```

### Import Notices (using store directly)

See `src/notices_store.py` `import_from_json()` method.

---

## Integration Examples

### Python Script

```python
import requests

BASE_URL = "http://localhost:5000/api"

def create_notice(title, **kwargs):
    data = {"title": title, **kwargs}
    response = requests.post(f"{BASE_URL}/notices", json=data)
    return response.json()

def get_overdue():
    response = requests.get(f"{BASE_URL}/notices?overdue=true")
    return response.json()["notices"]

# Create a notice
result = create_notice(
    "Project Deadline",
    due_date="2025-02-01",
    priority="high"
)
print(f"Created: {result['notice']['id']}")

# Get overdue notices
overdue = get_overdue()
print(f"Overdue count: {len(overdue)}")
```

### JavaScript/Fetch

```javascript
const API_URL = 'http://localhost:5000/api';

async function createNotice(title, priority = 'medium') {
  const response = await fetch(`${API_URL}/notices`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ title, priority }),
  });
  return response.json();
}

async function getNotices() {
  const response = await fetch(`${API_URL}/notices`);
  return response.json();
}

// Usage
createNotice('Buy milk', 'low')
  .then(data => console.log('Created:', data));
```

---

## Notes

- The API server runs in a background thread and shares the same data store as the GUI
- Changes made via API are immediately visible in the GUI
- The API is designed for local use and does not implement authentication
- CORS is enabled for all origins (`*`) to allow browser-based clients
- Date formats: `YYYY-MM-DD` for dates, `YYYY-MM-DD HH:MM` for reminder times (24-hour format)

## Troubleshooting

### Connection Refused

```bash
# Check if server is running
curl http://localhost:5000/api/health

# If not running, check the gadget is enabled
```

### Invalid Date Format

```bash
# Correct
"2025-01-21"
"2025-01-21 14:30"

# Incorrect
"01/21/2025"
"Jan 21, 2025"
"2025-1-1"
```

### Port Already in Use

The default port is 5000. If it's in use, you can modify `NoticesGadget.API_PORT` in the gadget code.
