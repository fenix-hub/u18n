# app/api/routes.py
from flask import jsonify, request, Response
from typing import Dict, Tuple
from app.api.middleware import apply_rate_limit, apply_throttling, add_headers

def register_routes(app, config, rate_limiter, request_throttler, translation_manager):
    """Register all routes for the application"""
    
    @app.route('/health', methods=['GET'])
    def health_check() -> Response:
        """Health check endpoint."""
        headers = {}
        response = jsonify({
            "status": "ok", 
            "installedPackages": list(translation_manager.installed_packages),
            "serviceInfo": {
                "rateLimit": config["rate_limit"],
                "throttling": config["throttling"],
                "formats": config["formats"]
            }
        })
        
        # Apply rate limiting if enabled
        if config["rate_limit"]["enabled"]:
            _, rate_headers = rate_limiter.check()
            headers.update(rate_headers)
        
        # Apply throttling if enabled
        if config["throttling"]["enabled"]:
            _, throttle_headers = request_throttler.acquire()
            headers.update(throttle_headers)
            request_throttler.release()
        
        return add_headers(response, headers)
    
    @app.route('/translate', methods=['POST'])
    def translate() -> Response:
        """Translation endpoint with rate limiting and throttling."""
        headers = {}
        
        # Apply rate limiting if enabled
        if config["rate_limit"]["enabled"]:
            rate_pass, rate_headers = rate_limiter.check()
            headers.update(rate_headers)
            if not rate_pass:
                response = jsonify({"error": "Rate limit exceeded"})
                return add_headers(response, headers), 429
        
        # Apply throttling if enabled
        if config["throttling"]["enabled"]:
            throttle_pass, throttle_headers = request_throttler.acquire()
            headers.update(throttle_headers)
            if not throttle_pass:
                response = jsonify({"error": "Service overloaded, try again later"})
                return add_headers(response, headers), 503
            
            # Ensure we release the semaphore even if an error occurs
            try:
                result, status_code = process_translation_request(
                    request, 
                    translation_manager, 
                    config["translation"]["max_chars_per_request"],
                    config["translation"]["available_packages"],
                    config["translation"]["fallback_response"],
                    config["formats"]["output"]
                )
                
                # Add headers to the response
                return add_headers(result, headers), status_code
            finally:
                request_throttler.release()
        else:
            # Process without throttling
            result, status_code = process_translation_request(
                request, 
                translation_manager, 
                config["translation"]["max_chars_per_request"],
                config["translation"]["available_packages"],
                config["translation"]["fallback_response"],
                config["formats"]["output"]
            )
            
            # Add headers if any
            if headers:
                return add_headers(result, headers), status_code
            return result, status_code
    
    @app.route('/config', methods=['GET'])
    def get_config() -> Response:
        """Get current configuration."""
        headers = {}
        response = jsonify(config)
        
        # Apply rate limiting if enabled
        if config["rate_limit"]["enabled"]:
            _, rate_headers = rate_limiter.check()
            headers.update(rate_headers)
        
        # Apply throttling if enabled
        if config["throttling"]["enabled"]:
            _, throttle_headers = request_throttler.acquire()
            headers.update(throttle_headers)
            request_throttler.release()
        
        return add_headers(response, headers)
    
    @app.route('/config', methods=['PUT'])
    def update_config() -> Response:
        """Update configuration."""
        # Implementation omitted for brevity - would validate and apply new config
        # Similar to original code but adapted to modular structure
        return jsonify({"message": "Configuration update endpoint"}), 200

def process_translation_request(
    req, 
    translation_manager, 
    max_chars, 
    available_packages,
    fallback_response,
    output_formats
) -> Tuple[Response, int]:
    """
    Process translation request based on the input format.
    
    Returns:
        Tuple of (response, status_code)
    """
    try:
        # Determine input format
        content_type = req.headers.get('Content-Type', '')
        
        if 'application/json' in content_type:
            # JSON input
            data = req.json
            
            # Required fields
            if not all(key in data for key in ['text', 'source', 'target']):
                return jsonify({
                    "error": "Missing required fields. Need 'text', 'source', and 'target'"
                }), 400
            
            text = data['text']
            source_lang = data['source']
            target_lang = data['target']
            output_format = data.get('outputFormat', 'json')
            
        else:
            # Form data or query parameters
            text = req.form.get('text') or req.args.get('text')
            source_lang = req.form.get('source') or req.args.get('source')
            target_lang = req.form.get('target') or req.args.get('target')
            output_format = req.form.get('outputFormat') or req.args.get('outputFormat') or 'text'
            
            if not all([text, source_lang, target_lang]):
                return jsonify({
                    "error": "Missing required parameters. Need 'text', 'source', and 'target'"
                }), 400
        
        # Check if output format is supported
        if output_format not in output_formats:
            return jsonify({
                "error": f"Unsupported output format. Supported formats: {output_formats}"
            }), 400
        
        # Check character limit
        if len(text) > max_chars:
            return jsonify({
                "error": f"Text exceeds maximum character limit of {max_chars}"
            }), 400
        
        # Check if language pair is supported
        language_pair = f"{source_lang}-{target_lang}"
        if language_pair not in available_packages:
            return jsonify({
                "error": f"Unsupported language pair: {language_pair}. Supported pairs: {available_packages}"
            }), 400
        
        # Translate the text
        translated_text = translation_manager.translate(
            text, 
            source_lang, 
            target_lang,
            fallback_response
        )
        
        # Return result based on requested output format
        if output_format == "json":
            response = jsonify({
                "translated": translated_text,
                "source": source_lang,
                "target": target_lang,
                "original": text
            })
            # Add X-Translation-Info header
            response.headers['X-Translation-Characters'] = str(len(text))
            return response, 200
        else:
            response = Response(translated_text, mimetype='text/plain')
            # Add X-Translation-Info header
            response.headers['X-Translation-Characters'] = str(len(text))
            return response, 200
    
    except Exception as e:
        import logging
        logging.error(f"Error processing translation request: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500