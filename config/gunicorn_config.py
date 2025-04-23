# filepath: /workspaces/u18n/gunicorn_config.py
import os

# Worker Processes
workers = int(os.environ.get('GUNICORN_PROCESSES', '2'))
threads = int(os.environ.get('GUNICORN_THREADS', '4'))

# Logging
# Use '-' to log to stdout/stderr
accesslog = '-'
errorlog = '-'
# Add %(p)s for worker process ID
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" PID:%(p)s'
# Add %(process)d for worker process ID in error logs (uses standard Python logging formatters)
logformat = '[%(asctime)s] [%(process)d] [%(levelname)s] %(message)s'
loglevel = os.environ.get('GUNICORN_LOGLEVEL', 'info')

# Binding
bind = f"0.0.0.0:{os.environ.get('PORT', '5000')}"

# Other settings (optional)
# reload = bool(os.environ.get('GUNICORN_RELOAD', False)) # Useful for development
# timeout = int(os.environ.get('GUNICORN_TIMEOUT', '30'))