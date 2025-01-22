from flask import Flask
from app.routes import init_routes
from dotenv import load_dotenv 
from app.routes import init_routes
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    
    app=Flask(__name__)    
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    
    with app.app_context():
        init_routes(app)
        
    return app


def create_app():
    # Carga las variables de entorno desde el archivo .env
    load_dotenv()

    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)

    # Registrar blueprints si es necesario
    from app.routes import bp as main_bp
    app.register_blueprint(main_bp)

    return app