from app import create_app
from app.routes import register_routes
from flask_cors import CORS

app = create_app()
register_routes(app)
CORS(app)
app.config['DEBUG'] = True


if __name__ == "__main__":
    app.run(debug=True)
