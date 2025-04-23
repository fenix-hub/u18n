# u18n - Universal Translation Microservice

A high-performance, scalable translation microservice built with Flask and ArgosTranslate, designed for ease of use and integration into any multilingual application.

The microservice provides a robust translation API built on Flask and ArgosTranslate, with features like rate limiting, request throttling, and flexible configuration. The implementation follows best practices with proper error handling, middleware design, and comprehensive testing.  

The service can handle various input and output formats, making it easy to integrate with different client applications. It's Docker-ready for easy deployment and includes health checks for monitoring.  

## 🌟 Features

- **Multiple Translation Pairs**: Support for various language pairs (en-es, es-en, en-fr, fr-en, en-de, de-en)
- **Rate Limiting**: Protect your service with configurable rate limiting
- **Request Throttling**: Control concurrent request load
- **Multiple Input/Output Formats**: JSON and plain text support
- **Docker Ready**: Easy deployment with Docker and Docker Compose
- **Configurable**: YAML config files and environment variable overrides
- **Metrics**: Request tracking with detailed headers
- **Health Checks**: Built-in monitoring endpoint
- **Comprehensive API**: Well-documented RESTful endpoints

## 📋 API Endpoints

### Health Check
```
GET /health
```
Returns service status and installed language packages.

### Translation
```
POST /translate
```
Translates text from source language to target language.

**Input Formats:**
- JSON body:
```json
{
  "text": "Hello world",
  "source": "en",
  "target": "es",
  "outputFormat": "json"
}
```
- Form data with parameters: `text`, `source`, `target`, `outputFormat`

**Output Formats:**
- JSON:
```json
{
  "translated": "Hola mundo",
  "source": "en",
  "target": "es",
  "original": "Hello world"
}
```
- Plain text: `Hola mundo`

### Configuration
```
GET /config
```
Returns current service configuration.

```
PUT /config
```
Updates service configuration.

## 🚀 Getting Started

### Prerequisites

- Docker and Docker Compose
- Python 3.9+ (for development without Docker)

### Running with Docker

1. Clone the repository:
```bash
git clone https://github.com/fenix-hub/u18n.git
cd u18n
```

2. Start the service using Docker Compose:
```bash
docker-compose up -d
```

3. The service will be available at http://localhost:5000

### Running Locally for Development

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the service:
```bash
FLASK_APP=app/main.py python -m flask run
```

## ⚙️ Configuration

Configuration can be provided through:

1. Default values (built into the application)
2. YAML configuration file (`config/default_config.yml`)
3. Environment variables (highest priority)

### Environment Variables

| Variable | Description |
|----------|-------------|
| `CONFIG_PATH` | Path to YAML config file |
| `RATE_LIMIT_ENABLED` | Enable/disable rate limiting (true/false) |
| `RATE_LIMIT_RPM` | Requests per minute limit |
| `RATE_LIMIT_BURST` | Maximum burst size |
| `THROTTLING_ENABLED` | Enable/disable request throttling (true/false) |
| `THROTTLING_CONCURRENT` | Maximum concurrent requests |
| `MAX_CHARS_PER_REQUEST` | Character limit per translation request |
| `AVAILABLE_PACKAGES` | Comma-separated list of language pairs (e.g., "en-es,es-en") | 
| `LOGGING_LEVEL` | Logging level (e.g., DEBUG, INFO, WARNING, ERROR) |
| `LOGGING_FORMAT` | Python logging format string |

### Sample Configuration

```yaml
logging:
  level: "INFO"
  format: "%(asctime)s - PID:%(process)d - %(name)s - %(levelname)s - %(message)s"

rate_limit:
  requests_per_minute: 60
  burst: 10
  enabled: true

throttling:
  concurrent_requests: 5
  enabled: true

translation:
  max_chars_per_request: 5000
  available_packages:
    - "en-es"
    - "es-en"
    - "en-fr"
    - "fr-en"
    - "en-de"
    - "de-en"
    - "it-en"
    - "en-it"
  fallback_response: "Translation service unavailable. Please try again later."

formats:
  input:
    - "json"
    - "text"
  output:
    - "json"
    - "text"
```

## 📊 Response Headers

The service adds informative headers to responses:

### Rate Limiting Headers
- `X-RateLimit-Limit`: Maximum requests per minute
- `X-RateLimit-Remaining`: Remaining tokens
- `X-RateLimit-Reset`: Seconds until full reset
- `Retry-After`: Seconds to wait when rate limited

### Throttling Headers
- `X-Throttle-Limit`: Maximum concurrent requests
- `X-Throttle-Usage`: Current usage
- `X-Throttle-Remaining`: Available slots

### Translation Headers
- `X-Translation-Characters`: Character count of original text

## 🧪 Testing

Run tests with pytest:

```bash
pytest
```

Run with coverage report:

```bash
pytest --cov=app tests/
```

## 🔧 Architecture

The project follows a modular architecture with separate components for:

- **API Layer**: RESTful endpoints and request handling
- **Service Layer**: Business logic implementation
- **Configuration Management**: Dynamic config loading
- **Middleware**: Rate limiting and request throttling
- **Utilities**: Helper functions and decorators

### Project Structure

```
translation-service/
├── Dockerfile                      # Docker image definition
├── docker-compose.yml              # Docker composition for easy deployment
├── requirements.txt                # Python dependencies
├── README.md                       # Project documentation
├── config/                         # Configuration management
│   ├── __init__.py
│   ├── default_config.yml          # Default configuration values
│   └── config_loader.py            # Configuration loading logic
├── app/                            # Application code
│   ├── __init__.py                 # Logging configuration
│   ├── main.py                     # Application entry point
│   ├── api/                        # API endpoints
│   │   ├── __init__.py
│   │   ├── routes.py               # Route definitions
│   │   └── middleware.py           # Request middleware
│   ├── services/                   # Business logic services
│   │   ├── __init__.py
│   │   ├── translation_service.py  # Translation logic
│   │   ├── rate_limiter.py         # Rate limiting service
│   │   └── request_throttler.py    # Request throttling service
│   └── utils/                      # Utility functions
│       ├── __init__.py
│       └── helpers.py              # Helper decorators and functions
└── tests/                          # Test suite
    ├── __init__.py
    ├── test_api.py                 # API tests
    ├── test_translation.py         # Translation service tests
    └── test_config.py              # Configuration tests
```

## 📖 About ArgosTranslate

This service uses [ArgosTranslate](https://github.com/argosopentech/argos-translate), an open-source neural machine translation library that allows for offline translation. It supports multiple language pairs and uses lightweight models suitable for containerized deployments.

## 📝 Performance Considerations

- **Model Download**: Language models are downloaded on first use, which may cause initial delays
- **Memory Usage**: Consider container memory limits based on the number of language pairs loaded
- **Caching**: API responses are not cached; consider implementing a caching layer for frequent translations
- **Scaling**: For high-volume scenarios, deploy multiple instances behind a load balancer

## 🛡️ Security Notes

- The service does not implement authentication; consider adding API keys or OAuth2
- Request rates are tracked by IP address; implement user-based tracking for multi-user scenarios
- Add HTTPS for production deployments

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.