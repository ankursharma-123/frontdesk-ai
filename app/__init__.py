from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

# Create the SQLAlchemy instance outside any function
db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    db.init_app(app)
    
    with app.app_context():
        # Import the models to register them with SQLAlchemy
        from app.models import HelpRequest, KnowledgeItem
        
        # Create database tables
        db.create_all()
        
        # Import and register blueprints after models are registered
        from app.routes import main
        app.register_blueprint(main)
    
    return app