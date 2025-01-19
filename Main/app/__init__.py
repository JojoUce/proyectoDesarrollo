from flask import Flask
from app.routes import init_routes
from dotenv import load_dotenv 
from app.routes import init_routes
import os


def create_app():
    
    app=Flask(__name__)    
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    
    with app.app_context():
        init_routes(app)
        
    return app