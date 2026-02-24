from flask import Flask, render_template
from route import api_bp
from database import init_db
import logging
import os

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')

# Register blueprints
app.register_blueprint(api_bp)

# Initialize database on startup
with app.app_context():
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")

# Create videos directory if it doesn't exist
os.makedirs('videos', exist_ok=True)


@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    """Render the dashboard page"""
    return render_template('dashboard.html')


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return {"error": "Not found"}, 404


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    logger.error(f"Server error: {error}")
    return {"error": "Internal server error"}, 500


if __name__ == '__main__':
    logger.info("Starting Flask application")
    app.run(debug=True, host='0.0.0.0', port=5000)
