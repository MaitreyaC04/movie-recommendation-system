import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

db = SQLAlchemy()

def create_app():
    # Load environment variables
    load_dotenv()
    
    app = Flask(__name__,
                template_folder="templates",
                static_folder="static")

    # Config
    app.secret_key = os.getenv("SECRET_KEY", "fallback_secret")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "postgresql+psycopg2://username:password@localhost/movie_db")
    
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config['SECRET_KEY'] = 'your-secret-key'  # Needed for session handling
    
    UPLOAD_FOLDER = "static/uploads"   # ensure folder exists
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    # Init DB
    db.init_app(app)
    
    # Import routes inside factory
    from app import routes
    app.register_blueprint(routes.auth_bp)

    return app