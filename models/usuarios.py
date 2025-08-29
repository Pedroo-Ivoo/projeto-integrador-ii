from flask_login import UserMixin
from config import db

class Usuarios(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(50), nullable=False, unique=True)
    nome = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    senha = db.Column(db.LargeBinary, nullable=False, unique=True)
    perfilAcesso = db.Column(db.String(50), nullable=False)
    confirmado = db.Column(db.Boolean, default=False, nullable=False)