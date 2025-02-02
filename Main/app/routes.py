from dotenv import load_dotenv
from flask import Blueprint, jsonify, render_template, request, redirect, url_for, flash
from . import db
from .models import MetricasUsuario, Receta, Usuario, UsuarioRestriccion, RestriccionDietetica
from flask_login import login_user, login_required, current_user, logout_user
import pandas as pd
import plotly.express as px
from groq import Groq

# Cargar variables de entorno (incluye la clave de API de Groq)
load_dotenv()

# Inicializar el cliente de Groq
qclient = Groq()


bp = Blueprint('bp', __name__)


@bp.route('/')
@login_required
def index():
    return render_template('index.html', nombre_usuario=current_user.nombre_usuario)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nombre_usuario = request.form.get('nombre_usuario')
        contrasena = request.form.get('contrasena')

        usuario = Usuario.query.filter_by(nombre_usuario=nombre_usuario).first()


        if usuario and usuario.verificar_contrasena(contrasena):
            login_user(usuario)
            flash('Inicio de sesión exitoso', 'success')
            return redirect(url_for('bp.index')) 

        flash('Usuario o contraseña incorrectos', 'danger')

    return render_template('login.html') 


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre_usuario = request.form.get('nombre_usuario')
        correo_electronico = request.form.get('correo_electronico')
        contrasena = request.form.get('contrasena')
        confirm_contrasena = request.form.get('confirm_contrasena')
        edad = request.form.get('edad')
        altura = request.form.get('altura')

        if contrasena != confirm_contrasena:
            flash('Las contraseñas no coinciden', 'danger')
            return redirect(url_for('bp.register'))

        usuario_existente = Usuario.query.filter_by(nombre_usuario=nombre_usuario).first()
        if usuario_existente:
            flash('El nombre de usuario ya está en uso', 'danger')
            return redirect(url_for('bp.register'))

        correo_existente = Usuario.query.filter_by(correo_electronico=correo_electronico).first()
        if correo_existente:
            flash('El correo electrónico ya está registrado', 'danger')
            return redirect(url_for('bp.register'))


        nuevo_usuario = Usuario(
            nombre_usuario=nombre_usuario,
            correo_electronico=correo_electronico,
            edad=edad,
            altura=altura
        )

        nuevo_usuario.set_contrasena(contrasena)

        db.session.add(nuevo_usuario)
        db.session.commit()

        flash('Cuenta creada con éxito', 'success')
        return redirect(url_for('bp.login')) 

    return render_template('register.html') 


@bp.route('/perfil', methods=['GET', 'POST'])
@login_required  #
def perfil():
    if request.method == 'POST':
        nombre_usuario = request.form.get('nombre_usuario')
        correo_electronico = request.form.get('correo_electronico')
        edad = request.form.get('edad')
        altura = request.form.get('altura')

  
        current_user.nombre_usuario = nombre_usuario
        current_user.correo_electronico = correo_electronico
        current_user.edad = edad
        current_user.altura = altura

      
        db.session.commit()

        flash('Perfil actualizado con éxito', 'success')

      
        return redirect(url_for('bp.perfil'))

    return render_template('perfil.html', usuario=current_user) 

@bp.route('/tablas', methods=['GET'])
@login_required
def tablas():
    from .models import MetricasUsuario

    # Definimos las métricas que vamos a consultar
    metricas_especificas = [
        "Pasos diarios",
        "Calorías quemadas",
        "Configuraciones activas",
        "Búsquedas realizadas"
    ]

    # Usamos un diccionario para guardar los resultados de cada métrica
    resultados_metricas = {}

    # Realizamos la consulta por cada tipo de métrica
    for metrica in metricas_especificas:
        resultados_metricas[metrica] = (
            MetricasUsuario.query
            .filter(MetricasUsuario.usuario_id == current_user.id, MetricasUsuario.nombre_metrica == metrica)
            .order_by(MetricasUsuario.actualizado_en.desc())  # Ordenamos por la fecha de actualización (más reciente primero)
            .limit(5)  # Limite de 5 resultados
            .all()
        )

    # Extraemos los valores de cada métrica
    pasos_diarios_values = [m.valor_metrica for m in resultados_metricas["Pasos diarios"]]
    calorias_quemadas_values = [m.valor_metrica for m in resultados_metricas["Calorías quemadas"]]
    configuraciones_activas_values = [m.valor_metrica for m in resultados_metricas["Configuraciones activas"]]
    busquedas_realizadas_values = [m.valor_metrica for m in resultados_metricas["Búsquedas realizadas"]]

    # Pasamos los datos a la plantilla
    return render_template('tablas.html', 
                           pasos_diarios=pasos_diarios_values,
                           calorias_quemadas=calorias_quemadas_values,
                           configuraciones_activas=configuraciones_activas_values,
                           busquedas_realizadas=busquedas_realizadas_values)




@bp.route('/logout')
@login_required 
def logout():
    logout_user() 
    flash('Has cerrado sesión con éxito', 'success')
    return redirect(url_for('bp.login')) 

@bp.route('/historial')
@login_required
def historial():
    # Obtener todas las recetas de la base de datos
    recetas = Receta.query.filter_by(creado_por=current_user.id).all()
    
    # Crear una lista de diccionarios con la información de las recetas
    recetas_data = []
    for receta in recetas:
        recetas_data.append({
            "titulo": receta.titulo,
            "descripcion": receta.descripcion,
            "fecha": receta.creado_en.strftime("%Y-%m-%d")  # Formatear la fecha
        })
    
    return render_template('historial.html', recetas=recetas_data, nombre_usuario=current_user.nombre_usuario)

@bp.route('/restricciones', methods=['GET', 'POST'])
@login_required
def restricciones():
    # Si el método es POST, agregar la nueva restricción dietética
    if request.method == 'POST':
        nombre_restriccion = request.form.get('nombre_restriccion')
        descripcion = request.form.get('descripcion')

        # Verificar que el nombre de la restricción no esté vacío
        if nombre_restriccion:
            # Crear una nueva restricción dietética
            nueva_restriccion = RestriccionDietetica(nombre=nombre_restriccion, descripcion=descripcion)
            db.session.add(nueva_restriccion)
            db.session.commit()

            # Asociar la restricción dietética con el usuario logueado
            usuario_restriccion = UsuarioRestriccion(usuario_id=current_user.id, restriccion_id=nueva_restriccion.id)
            db.session.add(usuario_restriccion)
            db.session.commit()

            flash('Restricción dietética añadida exitosamente!', 'success')
        else:
            flash('El nombre de la restricción es obligatorio', 'danger')

    # Obtener las restricciones dietéticas asociadas al usuario logueado
    restricciones_usuario = db.session.query(UsuarioRestriccion).join(RestriccionDietetica).filter(UsuarioRestriccion.usuario_id == current_user.id).all()

    return render_template('restricciones.html', restricciones=restricciones_usuario)

@bp.route('/agregar_metricas', methods=['GET', 'POST'])
@login_required
def agregar_metricas():
    if request.method == 'POST':
        usuario_id = current_user.id
        
        # Obtener los valores del formulario
        nombre_metrica = request.form.get('selectedMetric')
        valor_metrica = request.form.get('metricValue', type=int)

        # Asegúrate de que los datos se reciban correctamente
        print(f"Nombre Métrica: {nombre_metrica}, Valor Métrica: {valor_metrica}")

        if nombre_metrica and valor_metrica is not None:
            nueva_metrica = MetricasUsuario(
                usuario_id=usuario_id,
                nombre_metrica=nombre_metrica,
                valor_metrica=valor_metrica
            )
            db.session.add(nueva_metrica)
            db.session.commit()
            flash('Métrica guardada correctamente', 'success')
        else:
            flash('Error al guardar la métrica', 'danger')

        return redirect(url_for('bp.agregar_metricas'))

    return render_template('agregar_metricas.html')






@bp.route('/generar_receta', methods=['GET', 'POST'])
@login_required
def generar_receta():
    receta = None  # Inicializar la variable de receta
    restricciones = []  # Inicializar las restricciones vacías

    # Obtener las restricciones de la base de datos asociadas al usuario logueado
    restricciones_db = db.session.query(RestriccionDietetica).join(UsuarioRestriccion).filter(UsuarioRestriccion.usuario_id == current_user.id).all()
    for restriccion in restricciones_db:
        restricciones.append(restriccion.nombre)  # Ajusta según el campo de nombre de la restricción

    if request.method == 'POST':
        # Obtener los ingredientes del formulario
        ingredientes = request.form.getlist('ingredientes')  # Lista de ingredientes seleccionados

        # Crear el prompt para la API de Groq
        prompt = f"Genera una receta que use los ingredientes {', '.join(ingredientes)} y que cumpla con las siguientes restricciones: {', '.join(restricciones)}."

        # Realizar la solicitud a la API de Groq
        try:
            stream_response = qclient.chat.completions.create(
                messages=[
                    {"role": "system", "content": "Solo generar recetas en español."},
                    {"role": "user", "content": prompt},
                ],
                model="llama3-8b-8192",  # Puedes usar el modelo que prefieras
                stream=True
            )

            # Procesar la respuesta de la API y formatear el contenido
            response = ''
            for chunk in stream_response:
                if chunk.choices[0].delta.content:
                    response += chunk.choices[0].delta.content
            
            # Formatear la respuesta para el HTML
            receta = format_receta(response)

        except Exception as e:
            # En caso de error, asignar el mensaje de error a receta
            receta = f"<p><strong>Error:</strong> {str(e)}</p>"

    # Aquí no usamos un return render_template, solo devolvemos la misma página
    return render_template('generar_receta.html', receta=receta, restricciones=restricciones)

def format_receta(response):
    # Formatear la receta, eliminando los espacios adicionales
    response = response.replace('\n', '<br>')  # Reemplazar saltos de línea por <br>
    response = response.replace('*', '<li>')  # Convertir a lista <li> (si es necesario)
    
    # Asegúrate de que los ingredientes no tengan espacios innecesarios
    response = response.replace('  ', ' ')  # Reemplazar dobles espacios por un solo espacio

    # Asegúrate de envolver la respuesta en una estructura HTML
    receta_formateada = f'<div class="receta-container"><p>{response}</p></div>'
    
    return receta_formateada







def init_routes(app):
    app.register_blueprint(bp) 
