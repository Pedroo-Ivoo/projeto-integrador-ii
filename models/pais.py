from config import db
from models import Regioes, Usuarios
# Define a classe Pais/Responsáveis que representa a tabela de motoristas no banco de dados
class Pais(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    sobrenome = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    telefone = db.Column(db.String(20), nullable=False)
    cep =  db.Column(db.String(10), nullable=False)
    rua = db.Column(db.String(150), nullable=False)
    numero = db.Column(db.String(10), nullable=False)
    complemento = db.Column(db.String(100), nullable=True)
    bairro = db.Column(db.String(100), nullable=False)
    cidade = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.String(2), nullable=False)
    regiao = db.Column(db.String(50), nullable=False)
    latitude = db.Column(db.Float, nullable=True)  
    longitude = db.Column(db.Float, nullable=True)
    
    id_regiao = db.Column(db.Integer, db.ForeignKey('regioes.id'), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    #Estabelecendo relacionamento entre as tabelas
    regiao_obj = db.relationship('Regioes', backref='pais')
    usuario_obj = db.relationship('Usuarios', backref='pais')
