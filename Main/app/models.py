from app import db
from datetime import datetime
from uuid import uuid4
from werkzeug.security import generate_password_hash, check_password_hash

class Usuario(db.Model):
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
