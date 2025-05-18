from flask import Flask
from flask_cors import CORS
import os
import tempfile

# Import your modularized logic (routes, etc.)
try:
    from app.routes import register_routes  # If you have a routes.py with a register_routes function
except ImportError:
    register_routes = None


def create_app() -> Flask:
    """
    Create and configure the Flask application.
    """
    app = Flask(__name__,
                static_folder='static',
                template_folder='templates')
    
    # Configure CORS to allow requests from frontend
    CORS(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:8080", "http://127.0.0.1:8080"],
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

    # Register routes/blueprints
    if register_routes:
        register_routes(app)
    else:
        # Fallback: define a root route
        @app.route('/')
        def index():
            return '10-K Financial Analysis API is running.'

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
