from flask import Flask, request
from config.config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    @app.before_request
    def log_request_info():
        print(f"[REQUEST] {request.method} {request.path} from {request.remote_addr}")
        
    # Import and register blueprints
    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)
    
    return app
