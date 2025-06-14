# Internal dashboard routing script
from flask import Flask, render_template, jsonify, send_from_directory, request, Response, stream_with_context
import os
import logging
import traceback
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.middleware.profiler import ProfilerMiddleware
import datetime
from functools import wraps
import time
from dotenv import load_dotenv
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration
from prometheus_flask_exporter import PrometheusMetrics
from flask_monitoringdashboard import Dashboard
from openai import OpenAI
import json

# Load environment variables
load_dotenv()

# Configure Sentry for error tracking
sentry_sdk.init(
    dsn=os.getenv('SENTRY_DSN'),
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0,
    environment=os.getenv('FLASK_ENV', 'development')
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create a file handler for IP logging
ip_logger = logging.getLogger('ip_tracker')
ip_logger.setLevel(logging.INFO)
ip_handler = logging.FileHandler('ip_tracking.log')
ip_handler.setFormatter(logging.Formatter('%(asctime)s - %(message)s'))
ip_logger.addHandler(ip_handler)

# Verify required environment variables
required_env_vars = ['OPENAI_API_KEY', 'SECRET_KEY']
missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
    raise EnvironmentError(f"Missing required environment variables: {', '.join(missing_vars)}")

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Initialize Prometheus metrics
metrics = PrometheusMetrics(app)
metrics.info('app_info', 'Application info', version='1.0.0')

# Initialize Flask Monitoring Dashboard
Dashboard.bind(app)

# Enable profiling in development
if os.environ.get('FLASK_ENV') == 'development':
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app)

# Simple in-memory cache
cache = {}
CACHE_TIMEOUT = 300  # 5 minutes

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Known IPs to monitor
MONITORED_IPS = {
    '100.20.92.101': 'Vercel IP 1',
    '44.225.181.72': 'Vercel IP 2',
    '44.227.217.144': 'Vercel IP 3'
}

def track_ip(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        client_ip = request.remote_addr
        if client_ip in MONITORED_IPS:
            ip_logger.info(f"Monitored IP Access - IP: {client_ip} ({MONITORED_IPS[client_ip]}) - "
                         f"Path: {request.path} - Method: {request.method} - "
                         f"User Agent: {request.headers.get('User-Agent', 'Unknown')}")
        return f(*args, **kwargs)
    return decorated_function

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

# Apply IP tracking to all routes
@app.before_request
def before_request():
    client_ip = request.remote_addr
    if client_ip in MONITORED_IPS:
        ip_logger.info(f"Monitored IP Access - IP: {client_ip} ({MONITORED_IPS[client_ip]}) - "
                      f"Path: {request.path} - Method: {request.method} - "
                      f"User Agent: {request.headers.get('User-Agent', 'Unknown')}")

# Add IP tracking to existing routes
@app.route('/')
@track_ip
@metrics.counter('home_page_views', 'Number of home page views')
@cache_response(timeout=60)  # Cache home page for 1 minute
def home():
    try:
        logger.info("Rendering home page")
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error rendering index.html: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@app.route('/admin')
@track_ip
@metrics.counter('admin_page_views', 'Number of admin page views')
@cache_response(timeout=30)  # Cache admin page for 30 seconds
def admin():
    try:
        logger.info("Rendering admin page")
        return render_template('admin.html')
    except Exception as e:
        logger.error(f"Error rendering admin.html: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@app.route('/investor')
@track_ip
@metrics.counter('investor_page_views', 'Number of investor page views')
@cache_response(timeout=30)  # Cache investor page for 30 seconds
def investor():
    try:
        logger.info("Rendering investor page")
        return render_template('investor_view.html')
    except Exception as e:
        logger.error(f"Error rendering investor_view.html: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

@app.route('/health')
@track_ip
@metrics.gauge('health_check', 'Health check status')
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
        
        # Get performance metrics
        metrics_data = {
            'response_times': metrics.get_metrics(),
            'cache_hits': cache_size,
            'memory_usage': memory_usage
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
            },
            "metrics": metrics_data
        }), 200
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}\n{traceback.format_exc()}")
        return jsonify({"status": "unhealthy", "error": str(e)}), 500

@app.route('/static/<path:filename>')
@track_ip
@metrics.counter('static_file_requests', 'Number of static file requests')
def serve_static(filename):
    try:
        return send_from_directory('static', filename, cache_timeout=3600)  # Cache static files for 1 hour
    except Exception as e:
        logger.error(f"Error serving static file {filename}: {str(e)}")
        return jsonify({"error": "File not found"}), 404

@app.route('/generate', methods=['POST'])
@track_ip
def generate_text():
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        
        def generate():
            # Create a streaming response from OpenAI
            stream = client.chat.completions.create(
                model="gpt-4",  # or your preferred model
                messages=[{"role": "user", "content": prompt}],
                stream=True
            )
            
            # Stream the response
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        
        return Response(stream_with_context(generate()), mimetype='text/event-stream')
    
    except Exception as e:
        app.logger.error(f"Error in text generation: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/generate-page')
@track_ip
def generate_page():
    return render_template('generate.html')

@app.route('/ip-stats')
def ip_stats():
    try:
        with open('ip_tracking.log', 'r') as f:
            logs = f.readlines()
        
        stats = {
            'total_requests': len(logs),
            'ip_counts': {},
            'recent_requests': []
        }
        
        for log in logs[-100:]:  # Get last 100 requests
            if any(ip in log for ip in MONITORED_IPS):
                stats['recent_requests'].append(log.strip())
                ip = next(ip for ip in MONITORED_IPS if ip in log)
                stats['ip_counts'][ip] = stats['ip_counts'].get(ip, 0) + 1
        
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting IP stats: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/ip-stats-page')
@track_ip
def ip_stats_page():
    return render_template('ip_stats.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)