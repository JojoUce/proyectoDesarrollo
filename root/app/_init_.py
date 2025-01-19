from flask import Flask
from dotenv import load_dotenv
import os

def create_app():
    
    load_dotenv()
    app=Flask(_name_)    
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    
    with app.app_context():
        
        from .routes import init_routes
        init_routes(app)
    return app