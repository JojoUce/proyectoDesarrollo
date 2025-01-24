from flask import Blueprint, jsonify, request
from app.services.recipe_service import recipeService
from app.models import Usuario, db  # Ajustado para usar Usuario en lugar de User

bp = Blueprint('main', __name__)

# Función para inicializar rutas
def init_routes(app):
    # Ruta para obtener recetas con ingredientes
    @app.route('/ingredients', methods=['POST'])
    def get_recipes():
        # Obtener los ingredientes desde el cuerpo de la solicitud
        data = request.json
        ingredients = data.get("ingredients")
        
        # Validación: Verificar si se ingresaron ingredientes
        if not ingredients:
            return jsonify({"error": "No se ingresó ingredientes"}), 400   

        # Instanciar el servicio de recetas y obtener resultados
        recipe_service = recipeService()
        recipe = recipe_service.fetch_recipes(ingredients)
        
        # Manejo de errores en el servicio
        if "error" in recipe:
            return jsonify({"error": recipe["error"]}), 500
        
        return jsonify({"Recetas": recipe})
    
@bp.route('/users', methods=['POST'])
def create_user():
    data = request.json

    # Verificar que todos los campos necesarios estén presentes
    required_fields = ['nombre_usuario', 'correo_electronico', 'contrasena_hash', 'edad', 'altura']
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"Falta el campo obligatorio: {field}"}), 400

    # Crear un nuevo usuario con los datos proporcionados
    new_user = Usuario(
        nombre_usuario=data['nombre_usuario'],
        correo_electronico=data['correo_electronico'],
        contrasena_hash=data['contrasena_hash'],
        edad=data['edad'],
        altura=data['altura']
    )
    
    db.session.add(new_user)
    db.session.commit()
    
    return jsonify({'message': 'Usuario creado exitosamente!'}), 201


# Ruta para obtener todos los usuarios
@bp.route('/users', methods=['GET'])
def get_users():
    usuarios = Usuario.query.all()  # Ajustado para usar Usuario
    result = [{'id': u.id, 'nombre_usuario': u.nombre_usuario, 'correo_electronico': u.correo_electronico} for u in usuarios]  # Ajustado para mostrar los campos correctos
    return jsonify(result)


# Registrar las rutas en la aplicación
def register_routes(app):
    app.register_blueprint(bp)
