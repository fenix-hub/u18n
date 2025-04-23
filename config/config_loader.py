# app/config/config_loader.py
import os
import yaml
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def update_nested_dict(d: Dict, u: Dict) -> Dict:
    """Update nested dictionary recursively."""
    for k, v in u.items():
        if isinstance(v, dict) and k in d and isinstance(d[k], dict):
            update_nested_dict(d[k], v)
        else:
            d[k] = v
    return d

def load_config(config_path: str = None) -> Dict[str, Any]:
    """
    Load configuration with the following priority:
    1. Environment variables
    2. YAML configuration file
    3. Default values
    """
    # Default configuration
    default_config = {
        "rate_limit": {
            "requests_per_minute": 60,
            "burst": 10,
            "enabled": True
        },
        "throttling": {
            "concurrent_requests": 5,
            "enabled": True
        },
        "translation": {
            "max_chars_per_request": 5000,
            "available_packages": ["en-es", "es-en", "en-fr", "fr-en", "en-de", "de-en", "it-en", "en-it"],
            "fallback_response": "Translation service unavailable"
        },
        "formats": {
            "input": ["json", "text"],
            "output": ["json", "text"]
        },
        "logging": { # Add default logging config
            "level": "INFO",
            "format": "%(asctime)s - PID:%(process)d - %(name)s - %(levelname)s - %(message)s"
        }
    }
    
    # Load from YAML file if provided
    config = default_config.copy()
    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                yaml_config = yaml.safe_load(f)
                if yaml_config:
                    config = update_nested_dict(config, yaml_config)
                    logger.info(f"Configuration loaded from {config_path}")
        except Exception as e:
            logger.error(f"Error loading configuration from {config_path}: {str(e)}")
    
    # Override with environment variables
    if os.environ.get('RATE_LIMIT_ENABLED'):
        config["rate_limit"]["enabled"] = os.environ.get('RATE_LIMIT_ENABLED').lower() == 'true'
    
    if os.environ.get('RATE_LIMIT_RPM'):
        config["rate_limit"]["requests_per_minute"] = int(os.environ.get('RATE_LIMIT_RPM'))
    
    if os.environ.get('RATE_LIMIT_BURST'):
        config["rate_limit"]["burst"] = int(os.environ.get('RATE_LIMIT_BURST'))
    
    if os.environ.get('THROTTLING_ENABLED'):
        config["throttling"]["enabled"] = os.environ.get('THROTTLING_ENABLED').lower() == 'true'
    
    if os.environ.get('THROTTLING_CONCURRENT'):
        config["throttling"]["concurrent_requests"] = int(os.environ.get('THROTTLING_CONCURRENT'))
    
    if os.environ.get('MAX_CHARS_PER_REQUEST'):
        config["translation"]["max_chars_per_request"] = int(os.environ.get('MAX_CHARS_PER_REQUEST'))
    
    if os.environ.get('AVAILABLE_PACKAGES'):
        config["translation"]["available_packages"] = os.environ.get('AVAILABLE_PACKAGES').split(',')
    
    if os.environ.get('LOGGING_LEVEL'):
        config["logging"]["level"] = os.environ.get('LOGGING_LEVEL').upper()

    if os.environ.get('LOGGING_FORMAT'):
        config["logging"]["format"] = os.environ.get('LOGGING_FORMAT')

    logger.info("Configuration loaded successfully")
    return config