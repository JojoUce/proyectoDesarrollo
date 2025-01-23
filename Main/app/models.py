# Main/app/models.py
from app import db
from datetime import datetime
from uuid import uuid4

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    nombre_usuario = db.Column(db.String(50), unique=True, nullable=False)
    correo_electronico = db.Column(db.String(100), unique=True, nullable=False)
    contrasena_hash = db.Column(db.String(255), nullable=False)
    edad = db.Column(db.Integer, nullable=False)
    altura = db.Column(db.Float, nullable=False)
    creado_en = db.Column(db.DateTime, default=datetime.utcnow)
    actualizado_en = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
