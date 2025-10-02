from config import db
from models import Motoristas
# Define a classe Veiculos que representa a tabela de Veiculos no banco de dados
class Veiculos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    placa = db.Column(db.String(10), unique=True, nullable=False)
    modelo = db.Column(db.String(100), nullable=True)             
    ano_fabricacao = db.Column(db.Integer, nullable=True)         
    tipo = db.Column(db.String(150), nullable=False)
    vagas = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(50), default='Ativo')            
    data_registro = db.Column(db.DateTime, default=db.func.now()) 
    
    # Chave estrangeira
    id_motorista = db.Column(db.Integer, db.ForeignKey('motoristas.id'), nullable=False)
    
    #Estabelecendo relacionamento entre as tabelas
    regiao_obj = db.relationship('Motoristas', backref='veiculos')
