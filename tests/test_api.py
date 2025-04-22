# tests/test_api.py
import json
import pytest
from flask import Flask
from app.main import create_app

@pytest.fixture
def app():
    """Create application for testing"""
    test_config = {
        "rate_limit": {
            "requests_per_minute": 100,
            "burst": 20,
            "enabled": False
        },
        "throttling": {
            "concurrent_requests": 10,
            "enabled": False
        },
        "translation": {
            "max_chars_per_request": 5000,
            "available_packages": ["en-es", "es-en", "en-fr", "fr-en"],
            "fallback_response": "Test fallback response"
        },
        "formats": {
            "input": ["json", "text"],
            "output": ["json", "text"]
        }
    }
    app = create_app(test_config)
    return app

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "status" in data
    assert data["status"] == "ok"
    assert "installedPackages" in data
    assert "serviceInfo" in data

def test_translate_json(client, monkeypatch):
    """Test translation with JSON input"""
    # Mock the translation function to return a known response
    from app.main import translation_manager
    
    def mock_translate(text, from_code, to_code, fallback_response):
        return f"Translated: {text}"
    
    monkeypatch.setattr(translation_manager, "translate", mock_translate)
    
    # Test with JSON payload
    payload = {
        "text": "Hello world",
        "source": "en",
        "target": "es",
        "outputFormat": "json"
    }
    
    response = client.post(
        '/translate',
        data=json.dumps(payload),
        content_type='application/json'
    )
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data["translated"] == "Translated: Hello world"
    assert data["source"] == "en"
    assert data["target"] == "es"
    assert data["original"] == "Hello world"
    assert "X-Translation-Characters" in response.headers

def test_translate_form_data(client, monkeypatch):
    """Test translation with form data input"""
    # Mock the translation function
    from app.main import translation_manager
    
    def mock_translate(text, from_code, to_code, fallback_response):
        return f"Translated: {text}"
    
    monkeypatch.setattr(translation_manager, "translate", mock_translate)
    
    # Test with form data
    response = client.post(
        '/translate',
        data={
            "text": "Hello world",
            "source": "en",
            "target": "es",
            "outputFormat": "text"
        }
    )
    
    assert response.status_code == 200
    assert response.data.decode('utf-8') == "Translated: Hello world"
    assert "X-Translation-Characters" in response.headers

def test_translate_missing_fields(client):
    """Test translation with missing required fields"""
    # Test with missing fields
    payload = {
        "text": "Hello world",
        "source": "en",
        # Missing "target" field
    }
    
    response = client.post(
        '/translate',
        data=json.dumps(payload),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data

def test_translate_unsupported_language(client):
    """Test translation with unsupported language pair"""
    # Test with unsupported language pair
    payload = {
        "text": "Hello world",
        "source": "en",
        "target": "ja",  # Japanese not in available_packages
    }
    
    response = client.post(
        '/translate',
        data=json.dumps(payload),
        content_type='application/json'
    )
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert "error" in data
    assert "Unsupported language pair" in data["error"]

def test_config_endpoint(client):
    """Test config endpoint"""
    response = client.get('/config')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert "rate_limit" in data
    assert "throttling" in data
    assert "translation" in data
    assert "formats" in data