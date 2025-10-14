from config import db
from models import Regioes, Motoristas, Veiculos
#Definição do modelo de Alocação de Viagens Motorista, Veículo e Região
class AlocacaoViagens(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_motorista = db.Column(db.Integer, db.ForeignKey('motoristas.id'), nullable=False)
    id_veiculo = db.Column(db.Integer, db.ForeignKey('veiculos.id'), nullable=False)
    
    

#Estabelecendo relacionamento entre as tabelas
    motorista_obj = db.relationship('Motoristas', backref='alocacao_viagens')
    veiculos_obj = db.relationship('Veiculos', backref='alocacao_viagens')
