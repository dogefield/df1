# Internal dashboard routing script
from flask import Flask, render_template, jsonify, send_from_directory
import os
import logging
import traceback
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.middleware.profiler import ProfilerMiddleware
import datetime
from functools import wraps
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Verify required environment variables
required_env_vars = ['OPENAI_API_KEY', 'SECRET_KEY']
missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
    raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Enable profiling in development
if os.environ.get('FLASK_ENV') == 'development':
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app)

# Simple in-memory cache
cache = {}
CACHE_TIMEOUT = 300  # 5 minutes

def cache_response(timeout=CACHE_TIMEOUT):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            cache_key = f"{f.__name__}:{str(args)}:{str(kwargs)}"
            if cache_key in cache:
                timestamp, data = cache[cache_key]
                if time.time() - timestamp < timeout:
                    return data
            result = f(*args, **kwargs)
            cache[cache_key] = (time.time(), result)
            return result
        return decorated_function
    return decorator

@app.route('/')
@cache_response(timeout=60)  # Cache home page for 1 minute
def home():
    try:
        logger.info("Rendering home page")
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error rendering index.html: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@app.route('/admin')
@cache_response(timeout=30)  # Cache admin page for 30 seconds
def admin():
    try:
        logger.info("Rendering admin page")
        return render_template('admin.html')
    except Exception as e:
        logger.error(f"Error rendering admin.html: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@app.route('/investor')
@cache_response(timeout=30)  # Cache investor page for 30 seconds
def investor():
    try:
        logger.info("Rendering investor page")
        return render_template('investor_view.html')
    except Exception as e:
        logger.error(f"Error rendering investor_view.html: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@app.route('/health')
def health_check():
    try:
        logger.info("Health check requested")
        # Check cache health
        cache_size = len(cache)
        cache_health = "healthy" if cache_size < 1000 else "warning"
        
        # Check memory usage
        import psutil
        process = psutil.Process()
        memory_info = process.memory_info()
        memory_usage = memory_info.rss / 1024 / 1024  # Convert to MB
        
        # Check environment variables (without exposing values)
        env_vars_status = {
            var: "configured" if os.getenv(var) else "missing"
            for var in required_env_vars
        }
        
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "cache": {
                "size": cache_size,
                "status": cache_health
            },
            "memory": {
                "usage_mb": round(memory_usage, 2),
                "status": "healthy" if memory_usage < 500 else "warning"
            },
            "environment": {
                "variables": env_vars_status,
                "status": "healthy" if all(os.getenv(var) for var in required_env_vars) else "warning"
            }
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

@app.route('/static/<path:filename>')
def serve_static(filename):
    try:
        return send_from_directory('static', filename, cache_timeout=3600)  # Cache static files for 1 hour
    except Exception as e:
        logger.error(f"Error serving static file {filename}: {str(e)}")
        return jsonify({"error": "File not found"}), 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)