from flask import Blueprint, jsonify, request
from app.services.recipe_service import recipeService
from app.models import Usuario, db  # Ajustado para usar Usuario en lugar de User
from app.models import UsuarioRestricciones, RestriccionesDieteticas, db

bp = Blueprint('main', __name__)

# Función para inicializar rutas
def init_routes(app):
    # Ruta para obtener recetas con ingredientes
    @bp.route('/ingredients', methods=['POST'])
    def get_recipes():
        data = request.json
        ingredients = data.get("ingredients")
        usuario_id = data.get("usuario_id")

        if not ingredients:
            return jsonify({"error": "No se ingresaron ingredientes"}), 400

        recipe_service = recipeService()
        recipes = recipe_service.fetch_recipes(ingredients, usuario_id)

        if "error" in recipes:
            return jsonify({"error": recipes["error"]}), 404

        return jsonify({"Recetas": recipes}), 200
    
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


#Ruta para que los usuarios puedan añadir restricciones dietéticas
@bp.route('/restricciones', methods=['POST'])
def agregar_restriccion():
    data = request.json
    restriccion_id = data.get('restriccion_id')
    usuario_id = data.get('usuario_id')

    if not restriccion_id or not usuario_id:
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    # Verificar si la restricción ya existe
    existente = UsuarioRestricciones.query.filter_by(usuario_id=usuario_id, restriccion_id=restriccion_id).first()
    if existente:
        return jsonify({"message": "La restricción ya está asignada"}), 200

    nueva_restriccion = UsuarioRestricciones(usuario_id=usuario_id, restriccion_id=restriccion_id)
    db.session.add(nueva_restriccion)
    db.session.commit()
    return jsonify({"message": "Restricción agregada correctamente"}), 201

@bp.route('/restricciones/<usuario_id>', methods=['GET'])
def obtener_restricciones(usuario_id):
    restricciones = UsuarioRestricciones.query.filter_by(usuario_id=usuario_id).all()
    resultado = [
        {
            "id": r.id,
            "nombre": r.restriccion.nombre,
            "descripcion": r.restriccion.descripcion
        }
        for r in restricciones
    ]
    return jsonify({"restricciones": resultado}), 200
