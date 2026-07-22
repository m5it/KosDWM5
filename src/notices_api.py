"""
Notices HTTP API Server
=======================

Flask-based REST API for managing notices via HTTP.
Provides endpoints for CRUD operations and statistics.

Usage:
    from notices_api import NoticesAPIServer
    server = NoticesAPIServer(port=5000)
    server.start()  # Starts in background thread
    server.stop()   # Stops the server
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

# Flask imports
try:
    from flask import Flask, request, jsonify, Response
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("Warning: Flask not installed. API server will not be available.")
    print("Install with: pip install flask flask-cors")

from notices_store import NoticesStore, Notice


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('NoticesAPI')


class NoticesAPIServer:
    """
    HTTP API server for notices management.
    """
    
    def __init__(self, store: Optional[NoticesStore] = None, port: int = 5000):
        """
        Initialize the API server.
        
        Args:
            store: NoticesStore instance (creates new one if None)
            port: Port number to listen on
        """
        if not FLASK_AVAILABLE:
            raise RuntimeError("Flask is not installed. Cannot create API server.")
        
        self.store = store or NoticesStore()
        self.port = port
        self.app = Flask(__name__)
        self._setup_cors()
        self._register_routes()
        self._server_thread = None
        self._shutdown = False
    
    def _setup_cors(self):
        """Configure CORS for cross-origin requests."""
        CORS(self.app, resources={
            r"/api/*": {
                "origins": "*",
                "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization"]
            }
        })
    
    def _register_routes(self):
        """Register API endpoints."""
        
        @self.app.route('/api/notices', methods=['GET'])
        def list_notices():
            """
            GET /api/notices - List all notices with optional filters.
            
            Query Parameters:
                - completed: 'true' or 'false'
                - overdue: 'true' to get overdue notices
                - due_today: 'true' to get notices due today
                - priority: 'low', 'medium', or 'high'
                - search: search string for title/content
            """
            try:
                notices = self.store.get_all()
                
                # Apply filters
                completed = request.args.get('completed')
                if completed is not None:
                    is_completed = completed.lower() == 'true'
                    notices = [n for n in notices if n.completed == is_completed]
                
                if request.args.get('overdue') == 'true':
                    notices = [n for n in notices if n.is_overdue()]
                
                if request.args.get('due_today') == 'true':
                    notices = [n for n in notices if n.is_due_today()]
                
                priority = request.args.get('priority')
                if priority:
                    notices = [n for n in notices if n.priority == priority]
                
                search = request.args.get('search')
                if search:
                    notices = [n for n in notices 
                              if search.lower() in n.title.lower() 
                              or search.lower() in n.content.lower()]
                
                # Sort by due date, then priority
                priority_order = {"high": 0, "medium": 1, "low": 2}
                notices.sort(key=lambda n: (
                    n.due_date is None,
                    n.due_date or datetime.max,
                    priority_order.get(n.priority, 1)
                ))
                
                return jsonify({
                    "success": True,
                    "count": len(notices),
                    "notices": [n.to_dict() for n in notices]
                })
                
            except Exception as e:
                logger.error(f"Error listing notices: {e}")
                return jsonify({
                    "success": False,
                    "error": "Internal server error",
                    "message": str(e)
                }), 500
        
        @self.app.route('/api/notices/<notice_id>', methods=['GET'])
        def get_notice(notice_id: str):
            """GET /api/notices/<id> - Get a single notice by ID."""
            try:
                notice = self.store.get(notice_id)
                
                if not notice:
                    return jsonify({
                        "success": False,
                        "error": "Not found",
                        "message": f"Notice with ID '{notice_id}' not found"
                    }), 404
                
                return jsonify({
                    "success": True,
                    "notice": notice.to_dict()
                })
                
            except Exception as e:
                logger.error(f"Error getting notice {notice_id}: {e}")
                return jsonify({
                    "success": False,
                    "error": "Internal server error",
                    "message": str(e)
                }), 500
        
        @self.app.route('/api/notices', methods=['POST'])
        def create_notice():
            """
            POST /api/notices - Create a new notice.
            
            Request Body (JSON):
                - title: required string
                - content: optional string
                - due_date: optional string (YYYY-MM-DD)
                - reminder_time: optional string (YYYY-MM-DD HH:MM)
                - priority: optional string ('low', 'medium', 'high')
            """
            try:
                data = request.get_json()
                
                if not data:
                    return jsonify({
                        "success": False,
                        "error": "Bad request",
                        "message": "Request body must be JSON"
                    }), 400
                
                title = data.get('title', '').strip()
                if not title:
                    return jsonify({
                        "success": False,
                        "error": "Bad request",
                        "message": "Title is required"
                    }), 400
                
                # Parse optional fields
                kwargs = {}
                
                if 'content' in data:
                    kwargs['content'] = data['content']
                
                if 'due_date' in data and data['due_date']:
                    try:
                        kwargs['due_date'] = datetime.strptime(
                            data['due_date'], '%Y-%m-%d'
                        )
                    except ValueError:
                        return jsonify({
                            "success": False,
                            "error": "Bad request",
                            "message": "Invalid due_date format. Use YYYY-MM-DD"
                        }), 400
                
                if 'reminder_time' in data and data['reminder_time']:
                    try:
                        kwargs['reminder_time'] = datetime.strptime(
                            data['reminder_time'], '%Y-%m-%d %H:%M'
                        )
                    except ValueError:
                        return jsonify({
                            "success": False,
                            "error": "Bad request",
                            "message": "Invalid reminder_time format. Use YYYY-MM-DD HH:MM"
                        }), 400
                
                if 'priority' in data:
                    if data['priority'] not in ('low', 'medium', 'high'):
                        return jsonify({
                            "success": False,
                            "error": "Bad request",
                            "message": "Priority must be 'low', 'medium', or 'high'"
                        }), 400
                    kwargs['priority'] = data['priority']
                
                # Create notice
                notice = self.store.create(title, **kwargs)
                
                logger.info(f"Created notice: {notice.id}")
                
                return jsonify({
                    "success": True,
                    "message": "Notice created successfully",
                    "notice": notice.to_dict()
                }), 201
                
            except Exception as e:
                logger.error(f"Error creating notice: {e}")
                return jsonify({
                    "success": False,
                    "error": "Internal server error",
                    "message": str(e)
                }), 500
        
        @self.app.route('/api/notices/<notice_id>', methods=['PUT'])
        def update_notice(notice_id: str):
            """
            PUT /api/notices/<id> - Update an existing notice.
            
            Request Body (JSON): Same as POST, all fields optional
            """
            try:
                notice = self.store.get(notice_id)
                
                if not notice:
                    return jsonify({
                        "success": False,
                        "error": "Not found",
                        "message": f"Notice with ID '{notice_id}' not found"
                    }), 404
                
                data = request.get_json()
                
                if not data:
                    return jsonify({
                        "success": False,
                        "error": "Bad request",
                        "message": "Request body must be JSON"
                    }), 400
                
                kwargs = {}
                
                if 'title' in data:
                    title = data['title'].strip()
                    if not title:
                        return jsonify({
                            "success": False,
                            "error": "Bad request",
                            "message": "Title cannot be empty"
                        }), 400
                    kwargs['title'] = title
                
                if 'content' in data:
                    kwargs['content'] = data['content']
                
                if 'due_date' in data:
                    if data['due_date']:
                        try:
                            kwargs['due_date'] = datetime.strptime(
                                data['due_date'], '%Y-%m-%d'
                            )
                        except ValueError:
                            return jsonify({
                                "success": False,
                                "error": "Bad request",
                                "message": "Invalid due_date format. Use YYYY-MM-DD"
                            }), 400
                    else:
                        kwargs['due_date'] = None
                
                if 'reminder_time' in data:
                    if data['reminder_time']:
                        try:
                            kwargs['reminder_time'] = datetime.strptime(
                                data['reminder_time'], '%Y-%m-%d %H:%M'
                            )
                        except ValueError:
                            return jsonify({
                                "success": False,
                                "error": "Bad request",
                                "message": "Invalid reminder_time format. Use YYYY-MM-DD HH:MM"
                            }), 400
                    else:
                        kwargs['reminder_time'] = None
                
                if 'priority' in data:
                    if data['priority'] not in ('low', 'medium', 'high'):
                        return jsonify({
                            "success": False,
                            "error": "Bad request",
                            "message": "Priority must be 'low', 'medium', or 'high'"
                        }), 400
                    kwargs['priority'] = data['priority']
                
                if 'completed' in data:
                    kwargs['completed'] = bool(data['completed'])
                
                # Update notice
                updated = self.store.update(notice_id, **kwargs)
                
                logger.info(f"Updated notice: {notice_id}")
                
                return jsonify({
                    "success": True,
                    "message": "Notice updated successfully",
                    "notice": updated.to_dict()
                })
                
            except Exception as e:
                logger.error(f"Error updating notice {notice_id}: {e}")
                return jsonify({
                    "success": False,
                    "error": "Internal server error",
                    "message": str(e)
                }), 500
        
        @self.app.route('/api/notices/<notice_id>', methods=['DELETE'])
        def delete_notice(notice_id: str):
            """DELETE /api/notices/<id> - Delete a notice."""
            try:
                notice = self.store.get(notice_id)
                
                if not notice:
                    return jsonify({
                        "success": False,
                        "error": "Not found",
                        "message": f"Notice with ID '{notice_id}' not found"
                    }), 404
                
                self.store.delete(notice_id)
                
                logger.info(f"Deleted notice: {notice_id}")
                
                return jsonify({
                    "success": True,
                    "message": "Notice deleted successfully"
                })
                
            except Exception as e:
                logger.error(f"Error deleting notice {notice_id}: {e}")
                return jsonify({
                    "success": False,
                    "error": "Internal server error",
                    "message": str(e)
                }), 500
        
        @self.app.route('/api/notices/<notice_id>/complete', methods=['POST'])
        def complete_notice(notice_id: str):
            """
            POST /api/notices/<id>/complete - Mark a notice as completed.
            
            Request Body (JSON, optional):
                - completed: boolean (default: true)
            """
            try:
                notice = self.store.get(notice_id)
                
                if not notice:
                    return jsonify({
                        "success": False,
                        "error": "Not found",
                        "message": f"Notice with ID '{notice_id}' not found"
                    }), 404
                
                data = request.get_json() or {}
                completed = data.get('completed', True)
                
                self.store.mark_completed(notice_id, completed)
                
                logger.info(f"Marked notice {notice_id} as completed={completed}")
                
                return jsonify({
                    "success": True,
                    "message": f"Notice marked as {'completed' if completed else 'active'}",
                    "completed": completed
                })
                
            except Exception as e:
                logger.error(f"Error completing notice {notice_id}: {e}")
                return jsonify({
                    "success": False,
                    "error": "Internal server error",
                    "message": str(e)
                }), 500
        
        @self.app.route('/api/notices/stats', methods=['GET'])
        def get_stats():
            """GET /api/notices/stats - Get statistics about notices."""
            try:
                stats = self.store.get_stats()
                
                return jsonify({
                    "success": True,
                    "stats": stats
                })
                
            except Exception as e:
                logger.error(f"Error getting stats: {e}")
                return jsonify({
                    "success": False,
                    "error": "Internal server error",
                    "message": str(e)
                }), 500
        
        @self.app.route('/api/health', methods=['GET'])
        def health_check():
            """GET /api/health - Health check endpoint."""
            return jsonify({
                "success": True,
                "status": "healthy",
                "timestamp": datetime.now().isoformat()
            })
        
        # Error handlers
        @self.app.errorhandler(404)
        def not_found(error):
            return jsonify({
                "success": False,
                "error": "Not found",
                "message": "The requested resource was not found"
            }), 404
        
        @self.app.errorhandler(405)
        def method_not_allowed(error):
            return jsonify({
                "success": False,
                "error": "Method not allowed",
                "message": "The HTTP method is not allowed for this endpoint"
            }), 405
        
        @self.app.errorhandler(500)
        def internal_error(error):
            logger.error(f"Internal server error: {error}")
            return jsonify({
                "success": False,
                "error": "Internal server error",
                "message": "An unexpected error occurred"
            }), 500
    
    def start(self, threaded: bool = True):
        """
        Start the API server.
        
        Args:
            threaded: If True, start in a background thread
        """
        if not FLASK_AVAILABLE:
            logger.error("Cannot start API server: Flask not installed")
            return False
        
        if threaded:
            import threading
            self._server_thread = threading.Thread(
                target=self._run_server,
                daemon=True
            )
            self._server_thread.start()
            logger.info(f"API server started on port {self.port} (background thread)")
        else:
            self._run_server()
        
        return True
    
    def _run_server(self):
        """Run the Flask server."""
        try:
            # Disable Flask's default logging to keep output clean
            import logging as flask_logging
            flask_logging.getLogger('werkzeug').setLevel(flask_logging.ERROR)
            
            self.app.run(
                host='0.0.0.0',
                port=self.port,
                debug=False,
                threaded=True
            )
        except Exception as e:
            logger.error(f"Server error: {e}")
    
    def stop(self):
        """Stop the API server."""
        # Note: Flask's development server doesn't support clean shutdown
        # In production, use a proper WSGI server with shutdown support
        logger.info("API server stop requested (may not take effect until next request)")
    
    def get_url(self) -> str:
        """Get the base URL for the API."""
        return f"http://localhost:{self.port}"


# Example usage
if __name__ == '__main__':
    if not FLASK_AVAILABLE:
        print("Flask is required to run the API server.")
        print("Install it with: pip install flask flask-cors")
        exit(1)
    
    print("Starting Notices API Server...")
    print("Endpoints:")
    print("  GET    /api/notices         - List all notices")
    print("  GET    /api/notices/<id>    - Get single notice")
    print("  POST   /api/notices         - Create new notice")
    print("  PUT    /api/notices/<id>    - Update notice")
    print("  DELETE /api/notices/<id>    - Delete notice")
    print("  POST   /api/notices/<id>/complete - Mark as completed")
    print("  GET    /api/notices/stats   - Get statistics")
    print("  GET    /api/health          - Health check")
    print()
    
    server = NoticesAPIServer(port=5000)
    server.start(threaded=False)  # Run in main thread for direct execution
