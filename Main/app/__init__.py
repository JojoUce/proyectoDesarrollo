from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import os
from dotenv import load_dotenv
from flask_login import LoginManager

from uuid import UUID

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

def create_app():
    load_dotenv()
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    login_manager.login_view = '/Main/app/static/login.html' 
    from .routes import init_routes
    init_routes(app)

    return app

@login_manager.user_loader
def load_user(user_id):
    from .models import Usuario
    try:
        user_id = UUID(user_id)
        user = Usuario.query.get(str(user_id))
        print(f'Usuario cargado: {user}')  # Asegúrate de que el usuario se cargue correctamente
        return user
    except ValueError:
        print('Error al cargar el usuario: ID no válido')  # Depuración en caso de error
        return None


