# app/main.py
import os
from flask import Flask
from flask_cors import CORS

from app.api.routes import register_routes
from app.services.rate_limiter import RateLimiter
from app.services.request_throttler import RequestThrottler
from app.services.translation_service import TranslationPackageManager
from config.config_loader import load_config
from app import setup_logging # Import the setup function

# Global service instances
config = None
rate_limiter = None
request_throttler = None
translation_manager = None

def create_app(test_config=None):
    """Create and configure the Flask application"""
    app = Flask(__name__, instance_relative_config=True)
    CORS(app)  # Enable CORS for all routes
    
    # Initialize services
    initialize_services(test_config)
    
    # Register routes
    register_routes(app, config, rate_limiter, request_throttler, translation_manager)
    
    return app

def initialize_services(test_config=None):
    """Initialize all service components"""
    global config, rate_limiter, request_throttler, translation_manager
    
    # Load configuration
    if test_config is None:
        config_path = os.environ.get('CONFIG_PATH')
        config = load_config(config_path)
    else:
        config = test_config
    
    # Setup logging
    setup_logging(config)

    # Initialize rate limiter
    rate_limiter = RateLimiter(
        config["rate_limit"]["requests_per_minute"],
        config["rate_limit"]["burst"]
    )
    
    # Initialize request throttler
    request_throttler = RequestThrottler(
        config["throttling"]["concurrent_requests"]
    )
    
    # Initialize translation service
    translation_manager = TranslationPackageManager()
    translation_manager.install_configured_packages(config["translation"]["available_packages"])

# Create the application instance
app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)