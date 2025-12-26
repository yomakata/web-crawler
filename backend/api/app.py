"""Flask application configuration and initialization"""
import os
from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def create_app():
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CSV_SIZE_MB', 10)) * 1024 * 1024
    app.config['OUTPUT_DIRECTORY'] = os.getenv('OUTPUT_DIRECTORY', './output')
    app.config['DEBUG'] = os.getenv('DEBUG', 'false').lower() == 'true'
    
    # CORS configuration
    cors_origins = os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(',')
    CORS(app, origins=cors_origins, supports_credentials=True)
    
    # Register routes
    from api.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Health check endpoint
    @app.route('/health')
    def health():
        return {'status': 'healthy', 'message': 'Web Crawler API is running'}
    
    @app.route('/')
    def index():
        return {
            'name': 'Web Crawler API',
            'version': '1.0.0',
            'endpoints': {
                'health': '/health',
                'api': '/api',
                'docs': '/api/docs'
            }
        }
    
    return app


if __name__ == '__main__':
    app = create_app()
    port = int(os.getenv('BACKEND_PORT', 5000))
    host = os.getenv('BACKEND_HOST', '0.0.0.0')
    app.run(host=host, port=port, debug=app.config['DEBUG'])
