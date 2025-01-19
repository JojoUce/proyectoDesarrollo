from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'your_secret_key'

    with app.app_context():
        from .routes import init_routes
        init_routes(app)

    return app
