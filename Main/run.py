from datetime import timedelta
from app import create_app
from app.routes import register_routes
from flask_cors import CORS

app = create_app()
register_routes(app)

CORS(app, supports_credentials=True, origins="http://127.0.0.1:5500")

app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax' 
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_TYPE'] = 'filesystem'

app.config['DEBUG'] = True

if __name__ == "__main__":
    app.run(debug=True)
