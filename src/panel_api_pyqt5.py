#!/usr/bin/env python3
"""
Panel API Service for KosDWM PyQt5

Provides a centralized HTTP API server that allows gadgets to register
custom endpoints for external communication.
"""

import json
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs


class PanelAPI:
    """
    Centralized HTTP API service for the KosDWM panel.
    
    Gadgets can register endpoints using:
        panel.api.register("/endpoint", handler_func, methods=["GET", "POST"])
    
    The server runs in a separate thread to avoid blocking the UI.
    """
    
    def __init__(self, port=8080):
        self.port = port
        self.endpoints = {}  # {path: (handler_func, methods)}
        self.server = None
        self.server_thread = None
        self._running = False
        
        # Register default endpoints
        self._register_defaults()
    
    def _register_defaults(self):
        """Register default API endpoints"""
        self.register("/api/status", self._handle_status, methods=["GET"])
        self.register("/api/endpoints", self._handle_endpoints_list, methods=["GET"])
    
    def register(self, path, handler, methods=None):
        """
        Register an endpoint with a handler function.
        
        Args:
            path: URL path (e.g., "/api/myendpoint")
            handler: Callable that receives request data and returns response
            methods: List of HTTP methods allowed (default: ["GET", "POST"])
        
        Returns:
            True if registration successful, False otherwise
        """
        if methods is None:
            methods = ["GET", "POST"]
        
        # Normalize path
        path = path if path.startswith("/") else "/" + path
        
        # Validate handler is callable
        if not callable(handler):
            print(f"[PanelAPI] Error: Handler for {path} is not callable")
            return False
        
        # Store endpoint
        self.endpoints[path] = {
            'handler': handler,
            'methods': [m.upper() for m in methods]
        }
        
        print(f"[PanelAPI] Registered endpoint: {path} [{', '.join(methods)}]")
        return True
    
    def unregister(self, path):
        """
        Unregister an endpoint.
        
        Args:
            path: URL path to unregister
        
        Returns:
            True if unregistered, False if not found
        """
        path = path if path.startswith("/") else "/" + path
        
        if path in self.endpoints:
            del self.endpoints[path]
            print(f"[PanelAPI] Unregistered endpoint: {path}")
            return True
        return False
    
    def start(self):
        """Start the HTTP server in a separate thread"""
        if self._running:
            print(f"[PanelAPI] Server already running on port {self.port}")
            return
        
        try:
            self.server = ThreadedHTTPServer(('localhost', self.port), self._create_handler())
            self.server.panel_api = self  # Give handler access to API
            
            self.server_thread = threading.Thread(target=self._serve, daemon=True)
            self.server_thread.start()
            self._running = True
            
            print(f"[PanelAPI] HTTP server started on http://localhost:{self.port}")
        except Exception as e:
            print(f"[PanelAPI] Failed to start server: {e}")
    
    def _serve(self):
        """Server thread target"""
        try:
            self.server.serve_forever()
        except Exception as e:
            print(f"[PanelAPI] Server error: {e}")
    
    def stop(self):
        """Stop the HTTP server"""
        if not self._running or not self.server:
            return
        
        self.server.shutdown()
        self.server.server_close()
        self._running = False
        print(f"[PanelAPI] HTTP server stopped")
    
    def is_running(self):
        """Check if server is running"""
        return self._running
    
    def get_endpoints(self):
        """Get list of registered endpoints"""
        return {
            path: {'methods': info['methods']}
            for path, info in self.endpoints.items()
        }
    
    def _handle_status(self, request_data):
        """Default status endpoint handler"""
        return {
            'status': 'ok',
            'service': 'KosDWM Panel API',
            'endpoints_registered': len(self.endpoints)
        }
    
    def _handle_endpoints_list(self, request_data):
        """List all registered endpoints"""
        return {
            'endpoints': self.get_endpoints()
        }
    
    def _create_handler(self):
        """Factory to create request handler class with access to PanelAPI"""
        panel_api = self
        
        class PanelAPIHandler(BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                """Suppress default logging"""
                pass
            
            def do_GET(self):
                self._handle_request("GET")
            
            def do_POST(self):
                self._handle_request("POST")
            
            def do_OPTIONS(self):
                """Handle CORS preflight requests"""
                self.send_response(200)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                self.end_headers()
            
            def _handle_request(self, method):
                parsed = urlparse(self.path)
                path = parsed.path
                
                # Find matching endpoint
                endpoint = panel_api.endpoints.get(path)
                
                if not endpoint:
                    self._send_error(404, f"Endpoint not found: {path}")
                    return
                
                # Check method is allowed
                if method not in endpoint['methods']:
                    self._send_error(405, f"Method {method} not allowed for {path}")
                    return
                
                # Parse request data
                request_data = {
                    'method': method,
                    'path': path,
                    'query': parse_qs(parsed.query),
                    'headers': dict(self.headers)
                }
                
                # Read body for POST requests
                if method == "POST":
                    content_length = self.headers.get('Content-Length')
                    if content_length:
                        body = self.rfile.read(int(content_length))
                        try:
                            request_data['body'] = json.loads(body.decode('utf-8'))
                        except json.JSONDecodeError:
                            request_data['body'] = body.decode('utf-8')
                
                # Call handler
                try:
                    response = endpoint['handler'](request_data)
                    
                    # Ensure response is dict or string
                    if not isinstance(response, (dict, list, str)):
                        response = {'result': str(response)}
                    
                    self._send_json(200, response)
                    
                except Exception as e:
                    print(f"[PanelAPI] Handler error for {path}: {e}")
                    self._send_error(500, f"Handler error: {str(e)}")
            
            def _send_json(self, status_code, data):
                """Send JSON response"""
                self.send_response(status_code)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                if isinstance(data, str):
                    self.wfile.write(data.encode('utf-8'))
                else:
                    self.wfile.write(json.dumps(data).encode('utf-8'))
            
            def _send_error(self, status_code, message):
                """Send error response"""
                self.send_response(status_code)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                
                error_response = {
                    'error': message,
                    'status': status_code
                }
                self.wfile.write(json.dumps(error_response).encode('utf-8'))
        
        return PanelAPIHandler


class ThreadedHTTPServer(HTTPServer):
    """Threaded HTTP server to handle multiple concurrent requests"""
    allow_reuse_address = True


# Example usage and testing
if __name__ == "__main__":
    import time
    
    # Create API instance
    api = PanelAPI(port=8080)
    
    # Register example endpoints
    def hello_handler(request):
        return {'message': 'Hello from KosDWM!', 'method': request['method']}
    
    def echo_handler(request):
        return {
            'echo': request.get('body', {}),
            'query': request.get('query', {})
        }
    
    api.register("/api/hello", hello_handler, methods=["GET"])
    api.register("/api/echo", echo_handler, methods=["POST"])
    
    # Start server
    api.start()
    
    print("\nTest with:")
    print("  curl http://localhost:8080/api/status")
    print("  curl http://localhost:8080/api/hello")
    print("  curl -X POST -d '{\"test\":\"data\"}' http://localhost:8080/api/echo")
    print("\nPress Ctrl+C to stop...")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        api.stop()
        print("\nServer stopped")
