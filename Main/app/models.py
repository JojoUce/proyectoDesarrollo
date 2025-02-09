from app import db
from datetime import datetime
from uuid import uuid4
from flask_login import UserMixin 
from werkzeug.security import generate_password_hash, check_password_hash

class Usuario(db.Model, UserMixin):  # Heredamos de UserMixin
    __tablename__ = 'usuarios'

    # Definir columnas
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    nombre_usuario = db.Column(db.String(50), unique=True, nullable=False)
    correo_electronico = db.Column(db.String(100), unique=True, nullable=False)
    contrasena_hash = db.Column(db.String(255), nullable=False)
    edad = db.Column(db.Integer, nullable=False)
    altura = db.Column(db.Float, nullable=False)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)
    actualizado_en = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<Usuario {self.nombre_usuario}>"

    # Método para asignar una contraseña hasheada
    def set_contrasena(self, contrasena):
        """Genera un hash para la contraseña y lo guarda en la base de datos"""
        self.contrasena_hash = generate_password_hash(contrasena)

    # Método para verificar la contraseña ingresada
    def verificar_contrasena(self, contrasena):
        """Verifica si la contraseña proporcionada coincide con el hash almacenado"""
        return check_password_hash(self.contrasena_hash, contrasena)

class Receta(db.Model):
    __tablename__ = 'recetas'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    titulo = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    creado_por = db.Column(db.String(36), db.ForeignKey('usuarios.id'), nullable=False)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)
    actualizado_en = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relación inversa con el Usuario
    creador = db.relationship('Usuario', backref=db.backref('recetas', lazy=True))

    def __repr__(self):
        return f"<Receta {self.titulo}>"
    
class ParametrosNutricionales(db.Model):
    __tablename__ = 'parametros_nutricionales'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    receta_id = db.Column(db.String(36), db.ForeignKey('recetas.id'), nullable=False)
    calorias = db.Column(db.Float, nullable=False)
    proteinas = db.Column(db.Float, nullable=False)
    carbohidratos = db.Column(db.Float, nullable=False)
    grasas = db.Column(db.Float, nullable=False)
    sodio = db.Column(db.Float, nullable=False)
    azucar = db.Column(db.Float, nullable=False)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)
    actualizado_en = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relación inversa con Receta
    receta = db.relationship('Receta', backref=db.backref('parametros_nutricionales', lazy=True))

    def __repr__(self):
        return f"<ParametrosNutricionales Receta {self.receta_id}>"


# Modelo de Ingrediente
class Ingrediente(db.Model):
    __tablename__ = 'ingredientes'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    categoria = db.Column(db.String(50))
    es_alergeno = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"<Ingrediente {self.nombre}>"


# Modelo de Restricción Dietética
class RestriccionDietetica(db.Model):
    __tablename__ = 'restricciones_dieteticas'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    descripcion = db.Column(db.Text)

    def __repr__(self):
        return f"<Restriccion {self.nombre}>"


# Tabla intermedia para la relación muchos a muchos entre Recetas e Ingredientes
class RecetaIngrediente(db.Model):
    __tablename__ = 'receta_ingredientes'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    receta_id = db.Column(db.String(36), db.ForeignKey('recetas.id'), nullable=False)
    ingrediente_id = db.Column(db.String(36), db.ForeignKey('ingredientes.id'), nullable=False)
    cantidad = db.Column(db.Float, nullable=False)
    unidad = db.Column(db.String(20), nullable=False)

    receta = db.relationship('Receta', backref=db.backref('ingredientes', lazy=True))
    ingrediente = db.relationship('Ingrediente', backref=db.backref('recetas', lazy=True))

    def __repr__(self):
        return f"<RecetaIngrediente receta_id={self.receta_id} ingrediente_id={self.ingrediente_id}>"


# Relación muchos a muchos entre Usuario y Restricción Dietética
class UsuarioRestriccion(db.Model):
    __tablename__ = 'usuario_restricciones'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    usuario_id = db.Column(db.String(36), db.ForeignKey('usuarios.id'), nullable=False)
    restriccion_id = db.Column(db.String(36), db.ForeignKey('restricciones_dieteticas.id'), nullable=False)

    usuario = db.relationship('Usuario', backref=db.backref('usuario_restricciones', cascade='all, delete-orphan'))
    restriccion = db.relationship('RestriccionDietetica', backref=db.backref('usuario_restricciones', cascade='all, delete-orphan'))

    def __repr__(self):
        return f"<UsuarioRestriccion usuario_id={self.usuario_id} restriccion_id={self.restriccion_id}>"


# Modelo de Configuración de Usuario
class ConfiguracionUsuario(db.Model):
    __tablename__ = 'configuraciones_usuario'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    usuario_id = db.Column(db.String(36), db.ForeignKey('usuarios.id'), nullable=False)
    clave_configuracion = db.Column(db.String(50), nullable=False)
    valor_configuracion = db.Column(db.Text)

    usuario = db.relationship('Usuario', backref=db.backref('configuraciones_usuario', lazy=True))

    def __repr__(self):
        return f"<ConfiguracionUsuario usuario_id={self.usuario_id} clave={self.clave_configuracion}>"


# Modelo de Historial de Búsquedas de Usuario
class HistorialBusqueda(db.Model):
    __tablename__ = 'historial_busquedas'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    usuario_id = db.Column(db.String(36), db.ForeignKey('usuarios.id'), nullable=False)
    consulta = db.Column(db.Text, nullable=False)
    buscado_en = db.Column(db.DateTime, default=datetime.utcnow)

    usuario = db.relationship('Usuario', backref=db.backref('historial_busquedas', lazy=True))

    def __repr__(self):
        return f"<HistorialBusqueda usuario_id={self.usuario_id} consulta={self.consulta}>"


# Modelo de Métricas de Usuario
class MetricasUsuario(db.Model):
    __tablename__ = 'metricas_usuario'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    usuario_id = db.Column(db.String(36), db.ForeignKey('usuarios.id'), nullable=False)
    nombre_metrica = db.Column(db.String(50), nullable=False)
    valor_metrica = db.Column(db.Integer, default=0)
    actualizado_en = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    usuario = db.relationship('Usuario', backref=db.backref('metricas_usuario', lazy=True))

    def __repr__(self):
        return f"<MetricasUsuario usuario_id={self.usuario_id} nombre_metrica={self.nombre_metrica}>"