# Internal dashboard routing script
from flask import Flask, render_template
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

@app.route('/')
def home():
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error rendering index.html: {str(e)}")
        return "An error occurred", 500

@app.route('/admin')
def admin():
    try:
        return render_template('admin.html')
    except Exception as e:
        logger.error(f"Error rendering admin.html: {str(e)}")
        return "An error occurred", 500

@app.route('/investor')
def investor():
    try:
        return render_template('investor_view.html')
    except Exception as e:
        logger.error(f"Error rendering investor_view.html: {str(e)}")
        return "An error occurred", 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting server on port {port}")
    app.run(host='0.0.0.0', port=port)