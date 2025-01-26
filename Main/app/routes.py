from flask import Blueprint, render_template, request, redirect, url_for, flash
from . import db
from .models import Usuario
from flask_login import login_user, login_required, current_user, logout_user


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

@bp.route('/logout')
@login_required 
def logout():
    logout_user() 
    flash('Has cerrado sesión con éxito', 'success')
    return redirect(url_for('bp.login')) 


def init_routes(app):
    app.register_blueprint(bp) 
