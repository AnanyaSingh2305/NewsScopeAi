from flask import Flask
from flask_cors import CORS
from dotenv import load_dotenv
import os

def create_app():
    load_dotenv()
    
    app = Flask(__name__, static_folder='../static', template_folder='../templates')
    CORS(app)
    
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-dev-key')
    
    register_error_handlers(app)
    
    from app.routes.fake_news import fake_news_bp
    from app.routes.bias import bias_bp
    from app.routes.summarize import summarize_bp
    from app.routes.translate import translate_bp
    from app.routes.video import video_bp
    from app.routes.analyze import analyze_bp
    from app.routes.feed import feed_bp
    from app.routes.media import media_bp
    from app.routes.auth import auth_bp
    
    app.register_blueprint(fake_news_bp, url_prefix='/api')
    app.register_blueprint(bias_bp, url_prefix='/api')
    app.register_blueprint(summarize_bp, url_prefix='/api')
    app.register_blueprint(translate_bp, url_prefix='/api')
    app.register_blueprint(video_bp, url_prefix='/api')
    app.register_blueprint(analyze_bp, url_prefix='/api')
    app.register_blueprint(feed_bp, url_prefix='/api')
    app.register_blueprint(media_bp, url_prefix='/api')
    app.register_blueprint(auth_bp, url_prefix='/api')
    
    @app.route('/')
    def index():
        from flask import render_template
        return render_template('index.html')
        
    @app.route('/api/health')
    def health():
        return {"status": "ok", "version": "2.0.0"}, 200
        
    return app

def register_error_handlers(app):
    @app.errorhandler(400)
    def bad_request(e): return {"error": "Bad Request", "message": str(e)}, 400
    @app.errorhandler(404)
    def not_found(e): return {"error": "Not Found", "message": "The requested API route does not exist."}, 404
    @app.errorhandler(500)
    def internal_error(e): return {"error": "Internal Server Error", "message": str(getattr(e, 'original_exception', e))}, 500
