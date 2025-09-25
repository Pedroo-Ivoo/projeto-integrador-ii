from config import db
from models import Regioes, Usuarios
# Define a classe Motoristas que representa a tabela de motoristas no banco de dados
class Motoristas(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    sobrenome = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    telefone = db.Column(db.String(20), nullable=False)
    regiao = db.Column(db.String(50), nullable=False)
    id_regiao = db.Column(db.Integer, db.ForeignKey('regioes.id'), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    #Estabelecendo relacionamento entre as tabelas
    regiao_obj = db.relationship('Regioes', backref='motoristas')
    usuario_obj = db.relationship('Usuarios', backref='motoristas')
