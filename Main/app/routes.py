from flask import Blueprint, jsonify, request
from app.services.recipe_service import recipeService
from app.models import Usuario, db  
import uuid


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
            return jsonify({"error": "No se ingresaron ingredientes"}), 400   

        # Instanciar el servicio de recetas y obtener resultados
        recipe_service = recipeService()
        recipe = recipe_service.fetch_recipes(ingredients)
        
        # Manejo de errores en el servicio
        if "error" in recipe:
            return jsonify({"error": recipe["error"]}), 500
        
        return jsonify({"Recetas": recipe})

# Ruta para crear un usuario
@bp.route('/users', methods=['POST'])
def create_user():
    data = request.json

    # Verificar que todos los campos necesarios estén presentes
    required_fields = ['nombre_usuario', 'correo_electronico', 'contrasena', 'edad', 'altura']
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"Falta el campo obligatorio: {field}"}), 400

    # Crear un nuevo usuario con los datos proporcionados
    new_user = Usuario(
        nombre_usuario=data['nombre_usuario'],
        correo_electronico=data['correo_electronico'],
        edad=data['edad'],
        altura=data['altura']
    )

    new_user.set_contrasena(data['contrasena'])


    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'Usuario creado exitosamente!'}), 201


@bp.route('/users', methods=['GET'])
def get_users():
    usuarios = Usuario.query.all()
    result = [{'id': u.id, 'nombre_usuario': u.nombre_usuario, 'correo_electronico': u.correo_electronico} for u in usuarios]
    return jsonify(result)

# Ruta para el login de usuarios
@bp.route('/login', methods=['POST'])
def login():
    # Obtener datos del cliente
    data = request.json
    nombre_usuario = data.get('nombre_usuario')
    contrasena = data.get('contrasena')

    # Buscar el usuario en la base de datos
    usuario = Usuario.query.filter_by(nombre_usuario=nombre_usuario).first()

    if not usuario:
        return jsonify({'error': 'Usuario no encontrado'}), 404


    if not usuario.verificar_contrasena(contrasena):
        return jsonify({'error': 'Contraseña incorrecta'}), 401


    return jsonify({
        'message': 'Inicio de sesión exitoso',
        'id': usuario.id,
        'nombre_usuario': usuario.nombre_usuario,
        'correo_electronico': usuario.correo_electronico
    })

@bp.route('/users/<id>', methods=['PUT'])
def update_user(id):
    data = request.json

    try:
        # Convierte el id a un UUID válido
        id_uuid = uuid.UUID(id)  # Convertimos la cadena a UUID
    except ValueError:
        return jsonify({"message": "ID no válido"}), 400  # Si no es un UUID válido

    # Buscar al usuario en la base de datos usando el UUID
    usuario = Usuario.query.filter_by(id=id_uuid).first()

    if not usuario:
        return jsonify({"error": "Usuario no encontrado"}), 404

    # Actualizar los campos que se envían en la solicitud
    nombre_usuario = data.get('nombre_usuario')
    correo_electronico = data.get('correo_electronico')
    edad = data.get('edad')
    altura = data.get('altura')
    contrasena = data.get('contrasena')

    # Verificar y actualizar cada campo (si se proporciona)
    if nombre_usuario:
        usuario.nombre_usuario = nombre_usuario
    if correo_electronico:
        usuario.correo_electronico = correo_electronico
    if edad:
        usuario.edad = edad
    if altura:
        usuario.altura = altura
    if contrasena:
        usuario.set_contrasena(contrasena)

    # Guardar los cambios en la base de datos
    db.session.commit()

    return jsonify({"message": "Usuario actualizado exitosamente!"}), 200



def register_routes(app):
    app.register_blueprint(bp)
