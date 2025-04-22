# tests/test_config.py
import os
import pytest
import tempfile
import yaml
from app.config.config_loader import load_config, update_nested_dict

class TestConfig:
    """Tests for configuration loading functionality"""
    
    def test_update_nested_dict(self):
        """Test recursive dictionary update"""
        # Test data
        base = {
            "a": 1,
            "b": {
                "c": 2,
                "d": 3
            },
            "e": {
                "f": 4
            }
        }
        
        update = {
            "a": 10,
            "b": {
                "c": 20
            },
            "g": 5
        }
        
        # Update dictionary
        result = update_nested_dict(base.copy(), update)
        
        # Assertions
        assert result["a"] == 10  # Value replaced
        assert result["b"]["c"] == 20  # Nested value replaced
        assert result["b"]["d"] == 3  # Nested value preserved
        assert result["e"]["f"] == 4  # Nested dict preserved
        assert result["g"] == 5  # New key added
    
    def test_load_default_config(self):
        """Test loading default configuration"""
        # Load config without any file or env vars
        config = load_config(None)
        
        # Assertions for default values
        assert config["rate_limit"]["requests_per_minute"] == 60
        assert config["rate_limit"]["burst"] == 10
        assert config["rate_limit"]["enabled"] is True
        assert config["throttling"]["concurrent_requests"] == 5
        assert len(config["translation"]["available_packages"]) > 0
        assert "en-es" in config["translation"]["available_packages"]
    
    def test_load_config_from_file(self):
        """Test loading configuration from YAML file"""
        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as tmp:
            # Write custom config
            yaml.dump({
                "rate_limit": {
                    "requests_per_minute": 100,
                    "burst": 20
                },
                "translation": {
                    "max_chars_per_request": 10000
                }
            }, tmp)
        
        try:
            # Load config from file
            config = load_config(tmp.name)
            
            # Assertions for overridden values
            assert config["rate_limit"]["requests_per_minute"] == 100
            assert config["rate_limit"]["burst"] == 20
            assert config["translation"]["max_chars_per_request"] == 10000
            
            # Default values still present
            assert config["throttling"]["concurrent_requests"] == 5
            assert config["rate_limit"]["enabled"] is True
        finally:
            # Clean up
            os.unlink(tmp.name)
    
    def test_load_config_from_env(self, monkeypatch):
        """Test loading configuration from environment variables"""
        # Set environment variables
        monkeypatch.setenv("RATE_LIMIT_ENABLED", "false")
        monkeypatch.setenv("RATE_LIMIT_RPM", "200")
        monkeypatch.setenv("THROTTLING_CONCURRENT", "15")
        monkeypatch.setenv("MAX_CHARS_PER_REQUEST", "8000")
        monkeypatch.setenv("AVAILABLE_PACKAGES", "en-es,es-en,fr-en")
        
        # Load config
        config = load_config(None)
        
        # Assertions for env var values
        assert config["rate_limit"]["enabled"] is False
        assert config["rate_limit"]["requests_per_minute"] == 200
        assert config["throttling"]["concurrent_requests"] == 15
        assert config["translation"]["max_chars_per_request"] == 8000
        assert config["translation"]["available_packages"] == ["en-es", "es-en", "fr-en"]
    
    def test_config_priority(self, monkeypatch):
        """Test configuration priority (env vars override file)"""
        # Create temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False) as tmp:
            # Write custom config
            yaml.dump({
                "rate_limit": {
                    "requests_per_minute": 100,
                    "burst": 20
                }
            }, tmp)
        
        try:
            # Set environment variables
            monkeypatch.setenv("RATE_LIMIT_RPM", "200")
            
            # Load config
            config = load_config(tmp.name)
            
            # Assertions - env var should override file
            assert config["rate_limit"]["requests_per_minute"] == 200
            assert config["rate_limit"]["burst"] == 20  # From file
        finally:
            # Clean up
            os.unlink(tmp.name)