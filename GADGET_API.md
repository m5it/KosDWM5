# Gadget HTTP API Documentation

## Overview

KosDWM provides a centralized HTTP API server that allows gadgets to register custom endpoints. This enables external applications and scripts to interact with gadgets programmatically.

## How It Works

1. The Panel starts an HTTP server on port 8080 (default)
2. Gadgets register endpoints via `self.register_endpoint()`
3. External clients make HTTP requests to these endpoints
4. Handler functions process requests and return JSON responses

## Quick Start

### Basic Gadget with API

```python
from gadgets_pyqt5 import GadgetBase

class MyGadget(GadgetBase):
    def __init__(self):
        super().__init__()
        self.counter = 0
    
    def set_panel(self, panel):
        super().set_panel(panel)
        # Register API endpoints
        self.register_endpoint("/api/mygadget/stats", self._api_stats)
        self.register_endpoint("/api/mygadget/increment", self._api_increment, methods=["POST"])
    
    def _api_stats(self, request_data):
        """GET /api/mygadget/stats"""
        return {
            "gadget": "mygadget",
            "counter": self.counter,
            "status": "active"
        }
    
    def _api_increment(self, request_data):
        """POST /api/mygadget/increment"""
        self.counter += 1
        self.refresh_icon()  # Update UI
        return {
            "status": "success",
            "new_counter": self.counter
        }
    
    # Required GadgetBase methods...
    def get_name(self): return "mygadget"
    def get_icon(self): return f"🔢{self.counter}"
    def get_tooltip(self): return f"Counter: {self.counter}"
    def on_click(self): pass
```

## API Reference

### GadgetBase Methods

#### `register_endpoint(path, handler, methods=None)`
Register an HTTP endpoint for your gadget.

**Parameters:**
- `path` (str): URL path (e.g., "/api/mygadget/action")
- `handler` (callable): Function to handle requests
- `methods` (list): HTTP methods allowed (default: ["GET", "POST"])

**Returns:** `True` if registered successfully, `False` otherwise

**Example:**
```python
self.register_endpoint("/api/mygadget/data", self._api_data, methods=["GET", "POST"])
```

#### `api` (property)
Access the PanelAPI instance directly (advanced usage).

```python
if self.api:
    self.api.register("/custom/path", handler)
```

### Handler Function

Handler functions receive a `request_data` dictionary:

```python
{
    "method": "POST",           # HTTP method
    "path": "/api/mygadget/action",  # Request path
    "query": {"key": ["value"]}, # Query parameters (dict of lists)
    "headers": {"Content-Type": "application/json"},  # Request headers
    "body": {"title": "Test"}   # JSON body (POST requests only)
}
```

**Return Value:**
- Return a dict for JSON response: `return {"status": "ok"}`
- Return a string for plain text: `return "Hello"`
- Exceptions are caught and return 500 error

## Complete Example: Counter Gadget

```python
#!/usr/bin/env python3
"""
Counter Gadget with HTTP API
"""

import threading
from gadgets_pyqt5 import GadgetBase

class CounterGadget(GadgetBase):
    def __init__(self):
        super().__init__()
        self._counter = 0
        self._lock = threading.RLock()  # Thread-safe counter
    
    def set_panel(self, panel):
        super().set_panel(panel)
        # Register endpoints
        self.register_endpoint("/api/counter", self._api_get, methods=["GET"])
        self.register_endpoint("/api/counter/increment", self._api_increment, methods=["POST"])
        self.register_endpoint("/api/counter/reset", self._api_reset, methods=["POST"])
    
    def _api_get(self, request_data):
        """GET /api/counter - Get current value"""
        with self._lock:
            return {
                "counter": self._counter,
                "gadget": "counter"
            }
    
    def _api_increment(self, request_data):
        """POST /api/counter/increment - Increment counter"""
        body = request_data.get('body', {})
        amount = body.get('amount', 1)
        
        with self._lock:
            self._counter += amount
        
        self.refresh_icon()  # Update panel display
        
        return {
            "status": "success",
            "counter": self._counter,
            "incremented_by": amount
        }
    
    def _api_reset(self, request_data):
        """POST /api/counter/reset - Reset to zero"""
        with self._lock:
            old_value = self._counter
            self._counter = 0
        
        self.refresh_icon()
        
        return {
            "status": "success",
            "message": f"Reset from {old_value} to 0"
        }
    
    # Required methods
    def get_name(self): return "counter"
    def get_icon(self): return f"🔢{self._counter}"
    def get_tooltip(self): return f"Counter: {self._counter}"
    def on_click(self):
        # Optional: Show dialog or increment on click
        pass
```

## Testing with curl

```bash
# Get counter value
curl http://localhost:8080/api/counter | python -m json.tool

# Increment by 1
curl -X POST http://localhost:8080/api/counter/increment \
  -H "Content-Type: application/json" \
  -d '{"amount": 1}' | python -m json.tool

# Reset
curl -X POST http://localhost:8080/api/counter/reset
```

## Best Practices

### 1. Thread Safety
Always use locks when accessing shared data:

```python
def __init__(self):
    self._lock = threading.RLock()

def _api_handler(self, request):
    with self._lock:
        # Access shared data
        return {"data": self._data}
```

### 2. Error Handling
Return proper error responses:

```python
def _api_create(self, request):
    body = request.get('body', {})
    
    if not body.get('name'):
        return {"error": "Name is required", "status": "error"}
    
    # Process...
    return {"status": "success"}
```

### 3. UI Updates
Use `refresh_icon()` to update the panel display:

```python
def _api_update(self, request):
    self._data = request.get('body', {})
    self.refresh_icon()  # Updates gadget icon in panel
    return {"status": "updated"}
```

### 4. Path Naming
Use consistent paths: `/api/<gadgetname>/<action>`

```python
self.register_endpoint("/api/notices", self._api_list)
self.register_endpoint("/api/notices/add", self._api_add)
self.register_endpoint("/api/notices/delete", self._api_delete)
```

## Troubleshooting

### Endpoint not working?
- Check that `set_panel()` was called
- Verify the path starts with "/"
- Check console for "[PanelAPI] Registered endpoint:" message

### Handler not called?
- Verify HTTP method matches registered methods
- Check request URL is exact (no trailing slashes)
- Test with `curl -v` to see full response

### Data not persisting?
- Ensure thread-safe access with locks
- Save to file if needed (not automatic)
- Check for exceptions in handler

## Advanced Topics

### Custom HTTP Methods
```python
self.register_endpoint("/api/mygadget/data", handler, methods=["GET", "POST", "PUT", "DELETE"])
```

### Path Parameters
The API doesn't support path parameters like `/api/items/{id}`.
Use query parameters instead: `/api/items?id=123`

### CORS Support
The API includes CORS headers for browser access:
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, OPTIONS
```

## See Also

- `src/notices_gadget_pyqt5.py` - Full implementation example
- `src/panel_api_pyqt5.py` - Panel API implementation
- `src/gadgets_pyqt5.py` - GadgetBase class
