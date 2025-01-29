import datetime
from uuid import uuid4
from flask import Blueprint, render_template, request, redirect, url_for, flash
from . import db
from .models import MetricasUsuario, Receta, Usuario
from flask_login import login_user, login_required, current_user, logout_user
from datetime import datetime


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
@login_required  
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
    # Importa el modelo de métricas
    from .models import MetricasUsuario
    
    # Lista de métricas específicas que quieres graficar
    metricas_especificas = [
        "Pasos diarios",
        "Calorías quemadas",
        "Configuraciones activas",
        "Búsquedas realizadas"
    ]
    
    # Filtra las métricas basándote en el nombre de la métrica y el usuario actual
    metricas = MetricasUsuario.query.filter(
        MetricasUsuario.usuario_id == current_user.id,
        MetricasUsuario.nombre_metrica.in_(metricas_especificas)
    ).all()

    # Dividir las métricas en categorías individuales
    pasos_diarios = [m.valor_metrica for m in metricas if m.nombre_metrica == "Pasos diarios"]
    calorias_quemadas = [m.valor_metrica for m in metricas if m.nombre_metrica == "Calorías quemadas"]
    configuraciones_activas = [m.valor_metrica for m in metricas if m.nombre_metrica == "Configuraciones activas"]
    busquedas_realizadas = [m.valor_metrica for m in metricas if m.nombre_metrica == "Búsquedas realizadas"]

    # Enviar datos a la plantilla
    return render_template('tablas.html', 
                           pasos_diarios=pasos_diarios,
                           calorias_quemadas=calorias_quemadas,
                           configuraciones_activas=configuraciones_activas,
                           busquedas_realizadas=busquedas_realizadas)

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

@bp.route('/agregar_metricas', methods=['GET', 'POST'])
@login_required
def agregar_metricas():
    if request.method == 'POST':
        usuario_id = current_user.id
        selected_metric = request.form.get('selectedMetric')
        metric_value = request.form.get('metricValue', type=int)

        if selected_metric and metric_value is not None:
            nueva_metrica = MetricasUsuario(
                usuario_id=usuario_id,
                nombre_metrica=selected_metric,
                valor_metrica=metric_value
            )
            db.session.add(nueva_metrica)
            db.session.commit()
            flash(f'Métrica {selected_metric} creada correctamente', 'success')
        else:
            flash('Por favor selecciona una métrica y agrega un valor.', 'danger')
        return redirect(url_for('bp.agregar_metricas'))
    return render_template('agregar_metricas.html')

def init_routes(app):
    app.register_blueprint(bp) 
