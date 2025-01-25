from flask import Blueprint, current_app, jsonify, redirect, render_template, request, url_for
from app.services.recipe_service import recipeService
from flask_login import current_user, login_required
from flask_login import login_user
from flask_login import logout_user
from uuid import UUID  # Asegúrate de importar UUI

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
    
    login_user(usuario)
    print(f"Usuario autenticado: {current_user.is_authenticated}")

    return jsonify({
        'message': 'Inicio de sesión exitoso',
        'id': usuario.id,
        'nombre_usuario': usuario.nombre_usuario,
        'correo_electronico': usuario.correo_electronico
    })
@bp.route('/users/<id>', methods=['PUT'])
@login_required  # Protege la ruta con autenticación
def update_user(id):
    try:
        id_uuid = UUID(id)  # Convertimos la cadena a UUID
    except ValueError:
        return jsonify({"message": "ID no válido"}), 400  # Si no es un UUID válido

    # Verificar si el ID en la URL coincide con el ID del usuario autenticado
    if str(current_user.id) != str(id_uuid):  # Asegurarse de comparar como cadenas de texto
        return jsonify({"error": "No tienes permisos para modificar este usuario"}), 403  # Forbidden

    data = request.json

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

@bp.route('/logout', methods=['POST'])
@login_required  # Asegúrate de que solo los usuarios autenticados puedan cerrar sesión
def logout():
    logout_user()
    return jsonify({'message': 'Sesión cerrada correctamente'}), 200

@bp.route('/current_user', methods=['GET'])
def get_current_user():
    if not current_user.is_authenticated:
        return jsonify({"error": "No estas autenticado"}), 401  # o redirigir a login
    
    current_app.logger.debug(f'User is authenticated: {current_user.is_authenticated}')
    current_app.logger.debug(f'User ID: {current_user.id}')
    
    user_data = {
        'id': current_user.id,
        'nombre_usuario': current_user.nombre_usuario,
        'correo_electronico': current_user.correo_electronico
    }
    return jsonify(user_data)



def register_routes(app):
    app.register_blueprint(bp)
