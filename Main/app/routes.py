import types
import requests
import re
from dotenv import load_dotenv
from flask import Blueprint, jsonify, render_template, request, redirect, url_for, flash
from . import db
from .models import MetricasUsuario, ParametrosNutricionales, Receta, Usuario, UsuarioRestriccion, RestriccionDietetica
from flask_login import login_user, login_required, current_user, logout_user
import pandas as pd
import plotly.express as px
from groq import Groq
import openai
import os
import uuid
import random
from bs4 import BeautifulSoup
from werkzeug.utils import secure_filename
from google.cloud import vision



load_dotenv()
HF_API_KEY = os.getenv('HF_API_KEY')
qclient = Groq()
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = '../proyectoDesarrollo/Main/googlevision.json'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """Verifica si el archivo tiene una extensión permitida"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


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
        try: 
            edad = int(edad)
            altura = int (altura)
        except ValueError:
            flash('Ingrese valores numéricos correctos', 'danger')
            return redirect(url_for('bp.register'))
        

        if not (1 <= edad <= 110):
            flash('Ingrese la edad correcta', 'danger')
            return redirect(url_for('bp.register'))

        if not (30 <= altura <= 200):
            flash('Ingrese la altura correcta', 'danger')
            return redirect(url_for('bp.register'))

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
    # Obtener la última receta generada del usuario actual
    ultima_receta = db.session.query(Receta).filter(Receta.creado_por == current_user.id).order_by(Receta.creado_en.desc()).first()
    
    if ultima_receta:
        # Obtener los parámetros nutricionales de la última receta
        parametros_nutricionales = db.session.query(ParametrosNutricionales).filter(ParametrosNutricionales.receta_id == ultima_receta.id).first()
        
        if parametros_nutricionales:
            # Extraer los datos nutricionales
            calorias = parametros_nutricionales.calorias
            proteinas = parametros_nutricionales.proteinas
            carbohidratos = parametros_nutricionales.carbohidratos
            grasas = parametros_nutricionales.grasas
            sodio = parametros_nutricionales.sodio
            azucar = parametros_nutricionales.azucar
            
            # Pasar los datos al template
            return render_template('tablas.html', calorias=calorias, proteinas=proteinas, carbohidratos=carbohidratos, grasas=grasas, sodio=sodio, azucar=azucar)
        else:
            flash("No se encontraron parámetros nutricionales para esta receta.", "warning")
    else:
        flash("No tienes recetas generadas aún.", "warning")
    
    return redirect(url_for('index'))  # Redirigir al inicio si no se encuentra receta




@bp.route('/logout')
@login_required 
def logout():
    logout_user() 
    flash('Has cerrado sesión con éxito', 'success')
    return redirect(url_for('bp.login')) 

@bp.route('/historial')
@login_required
def historial():
    recetas = Receta.query.filter_by(creado_por=current_user.id).all()
    
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
    if request.method == 'POST':
        nombre_restriccion = request.form.get('nombre_restriccion')
        descripcion = request.form.get('descripcion')

        if nombre_restriccion:
            # Crear una nueva restricción dietética
            nueva_restriccion = RestriccionDietetica(nombre=nombre_restriccion, descripcion=descripcion)
            db.session.add(nueva_restriccion)
            db.session.commit()

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
        nombre_metrica = request.form.get('selectedMetric')
        valor_metrica = request.form.get('metricValue', type=int)

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

    metricas_usuario = MetricasUsuario.query.filter_by(usuario_id=current_user.id).order_by(MetricasUsuario.actualizado_en.desc()).limit(10).all()

    return render_template('agregar_metricas.html', metricas=metricas_usuario)


def format_receta(response):
    response = response.replace('\n', '<br>')
    response = response.replace('*', '<li>')
    response = response.replace('  ', ' ')
    receta_formateada = f'<div class="receta-container"><p>{response}</p></div>'
    
    return receta_formateada

def extraer_nombre_receta(response):
    """
    Extrae el nombre de la receta desde la respuesta de Groq (lo que está entre comillas).
    """
    match = re.search(r'"([^"]+)"', response)
    return match.group(1) if match else None


def detectar_ingredientes_google_vision(imagen_path):
    client = vision.ImageAnnotatorClient()

    with open(imagen_path, 'rb') as imagen:
        content = imagen.read()

    image = vision.Image(content=content)

    response = client.label_detection(image=image)
    labels = response.label_annotations

    ingredientes = []
    
    if labels:
        for label in labels:
            ingredientes.append(label.description)

    if response.error.message:
        raise Exception(f'Error en Google Vision API: {response.error.message}')
    
    return ingredientes

@bp.route('/generar_receta', methods=['GET', 'POST'])
@login_required
def generar_receta():
    receta = None
    imagen_url = None
    restricciones = []
    ingredientes_detectados = []

    restricciones_db = db.session.query(RestriccionDietetica).join(UsuarioRestriccion).filter(
        UsuarioRestriccion.usuario_id == current_user.id
    ).all()

    restricciones = [restriccion.nombre for restriccion in restricciones_db]
    valor_restriccion = [restriccion.descripcion for restriccion in restricciones_db]

    if request.method == 'POST':
        if 'imagen' in request.files:
            imagen = request.files['imagen']
            if imagen.filename != '' and allowed_file(imagen.filename):
                filename = secure_filename(imagen.filename)
                filepath = os.path.join("uploads", filename)
                imagen.save(filepath)
                
                # Enviar imagen a Google Vision para detectar ingredientes
                ingredientes_detectados = detectar_ingredientes_google_vision(filepath)
                print("Ingredientes detectados desde la imagen:", ingredientes_detectados)
                os.remove(filepath)

        # Si el usuario ingresa ingredientes manualmente
        ingredientes_manual = request.form.getlist('ingredientes')
        ingredientes = list(set(ingredientes_detectados + ingredientes_manual))

        if not ingredientes:
            flash("No se detectaron ingredientes. Por favor, súbelo nuevamente o ingresa manualmente.", "warning")
            return redirect(url_for('generar_receta'))

        prompt = f"""Genera una receta que use los ingredientes {', '.join(ingredientes)} y que cumpla con las siguientes restricciones obligatoriamente: {', '.join(restricciones)} con su detalle
        {', '.join(valor_restriccion)}. Además, incluye los siguientes detalles nutricionales para la receta:

        1. Calorías (kcal)
        2. Proteínas (g)
        3. Carbohidratos (g)
        4. Grasas (g)
        5. Sodio (mg)
        6. Azúcar (g)

        Por favor, incluye estos valores de manera clara y precisa. No pongas mensajes similares a este: 'Si quieres que te genere otra receta, dimelo'. Finalmente, coloca el nombre de la receta entre comillas sin negritas. Todo en Español."""


        try:
            stream_response = qclient.chat.completions.create(
                messages=[{
                    "role": "system", 
                    "content": "Solo generar recetas en español."
                },
                {
                    "role": "user", 
                    "content": prompt
                }],
                model="llama3-8b-8192",
                stream=True
            )

            response = ''
            for chunk in stream_response:
                if chunk.choices[0].delta.content:
                    response += chunk.choices[0].delta.content

            receta = format_receta(response)

            nombre_receta = extraer_nombre_receta(response)

            if nombre_receta:
                imagen_url = generar_imagen_huggingface(nombre_receta)
            receta_limpia = limpiar_html_para_bd(response)

            # EXTRAER LOS PARÁMETROS NUTRICIONALES
            parametros_nutricionales = extraer_parametros_nutricionales(receta_limpia)
            print("Parámetros nutricionales extraídos:", parametros_nutricionales)

            # Guardar en la base de datos
            if receta_limpia:
                nueva_receta = Receta(
                    titulo=nombre_receta,
                    descripcion=receta_limpia,
                    creado_por=current_user.id
                )
                db.session.add(nueva_receta)
                db.session.commit()

                receta_id = nueva_receta.id  # Obtener el ID de la receta recién guardada

                # GUARDAR LOS PARÁMETROS NUTRICIONALES EN LA BASE DE DATOS
                nueva_entrada_parametros = ParametrosNutricionales(
                    receta_id=receta_id,
                    calorias=parametros_nutricionales.get("calorias", 0),
                    proteinas=parametros_nutricionales.get("proteinas", 0),
                    carbohidratos=parametros_nutricionales.get("carbohidratos", 0),
                    grasas=parametros_nutricionales.get("grasas", 0),
                    sodio=parametros_nutricionales.get("sodio", 0),
                    azucar=parametros_nutricionales.get("azucar", 0)
                )
                db.session.add(nueva_entrada_parametros)
                db.session.commit()
                print(f"✅ Receta '{nombre_receta}' y parámetros nutricionales guardados en la base de datos.")

        except Exception as e:
            receta = f"<p><strong>Error:</strong> {str(e)}</p>"

    return render_template('generar_receta.html', receta=receta, restricciones=restricciones, imagen_url=imagen_url, random=random.random)

def extraer_parametros_nutricionales(descripcion):
    # Definir los patrones de búsqueda para los nutrientes
    patrones = {
        "calorias": r"calor(?:ías|ias):?\s*(\d+)\s?kcal",  # Maneja calorías con y sin acento
        "proteinas": r"proteínas?:?\s*(\d+)\s*g",  # Maneja proteínas con y sin acento
        "carbohidratos": r"carbohidratos?:?\s*(\d+)\s*g",  # Maneja carbohidratos con y sin acento
        "grasas": r"grasas?:?\s*(\d+)\s*g",  # Maneja grasas con y sin acento
        "sodio": r"sodio:?\s*(\d+)\s*mg",  # Maneja sodio
        "azucar": r"azúcar:?\s*(\d+)\s*g"  # Maneja azúcar
    }

    parametros = {}
    for clave, patron in patrones.items():
        resultado = re.search(patron, descripcion, re.IGNORECASE)  # Añadir re.IGNORECASE para evitar problemas con mayúsculas/minúsculas
        if resultado:
            parametros[clave] = float(resultado.group(1))
        else:
            parametros[clave] = 0.0  # Si no se encuentra, asignar 0

    return parametros


def limpiar_html_para_bd(texto):
    """Limpia el HTML antes de guardarlo en la base de datos."""
    # Eliminar etiquetas <br> y reemplazarlas por saltos de línea
    texto_limpio = re.sub(r'<br\s*/?>', '\n', texto)
    
    # Eliminar etiquetas <p>, <div>, <strong>, etc. si no son necesarias
    texto_limpio = re.sub(r'<[^>]+>', '', texto_limpio)
    
    # Opcional: Eliminar cualquier espacio extra o normalizar los saltos de línea
    texto_limpio = re.sub(r'\n+', '\n', texto_limpio).strip()
    
    return texto_limpio

def generar_imagen_huggingface(nombre_receta):
    """Genera una imagen con Hugging Face y la guarda en app/static/img/ con un nombre único."""
    if not HF_API_KEY:
        print("ERROR: No se encontró la API Key de Hugging Face.")
        return None

    try:
        response = requests.post(
            "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5",
            headers={"Authorization": f"Bearer {HF_API_KEY}"},
            json={"inputs": f"Un plato delicioso de {nombre_receta}, con presentación atractiva, en un fondo de cocina profesional."}
        )

        if response.status_code == 503:
            print("El modelo está cargando en Hugging Face, intenta en unos minutos.")
            return None

        if response.status_code == 200:
            # Guardar las imágenes en "app/static/img"
            image_dir = os.path.join("app", "static", "img")
            os.makedirs(image_dir, exist_ok=True)

            # Generar un nombre único para la imagen
            image_filename = f"receta_{uuid.uuid4().hex}.jpg"
            image_path = os.path.join(image_dir, image_filename)

            # Guardar la imagen en la carpeta correcta
            with open(image_path, "wb") as f:
                f.write(response.content)

            print("Imagen guardada en:", image_path)
            return f"/static/img/{image_filename}"  # URL accesible en Flask

        else:
            print(f"Error en Hugging Face: {response.status_code} - {response.text}")
            return None

    except Exception as e:
        print(f"ERROR generando imagen con Hugging Face: {e}")
        return None



def init_routes(app):
    app.register_blueprint(bp) 
