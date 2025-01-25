from app import db
from datetime import datetime
from uuid import uuid4

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


class RestriccionesDieteticas(db.Model):
    __tablename__ = 'restricciones_dieteticas'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    nombre = db.Column(db.String(50), unique=True, nullable=False)
    descripcion = db.Column(db.Text)

class UsuarioRestricciones(db.Model):
    __tablename__ = 'usuario_restricciones'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    usuario_id = db.Column(db.String(36), db.ForeignKey('usuarios.id', ondelete='CASCADE'), nullable=False)
    restriccion_id = db.Column(db.String(36), db.ForeignKey('restricciones_dieteticas.id', ondelete='CASCADE'), nullable=False)

