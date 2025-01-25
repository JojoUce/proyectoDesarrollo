from datetime import timedelta
from app import create_app
from app.routes import register_routes
from flask_cors import CORS

app = create_app()
register_routes(app)
CORS(app, supports_credentials=True, origins=["http://127.0.0.1:5500"])

# Establecer la duración de la sesión
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# Asegúrate de que esta opción sea False si no estás usando HTTPS
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_SAMESITE'] = 'None'

# Configuración de sesión
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_TYPE'] = 'filesystem'

# Habilitar el modo de depuración
app.config['DEBUG'] = True

if __name__ == "__main__":
    app.run(debug=True)
