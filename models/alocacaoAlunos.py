from config import db
from models import Alunos, AlocacaoViagens
#Definição do modelo de Alocação dos Alunos para viagens
class AlocacaoAlunos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_aluno = db.Column(db.Integer, db.ForeignKey('alunos.id'), nullable=False)
    id_alocacaoViagem = db.Column(db.Integer, db.ForeignKey('alocacao_viagens.id'), nullable=False)
 
#Estabelecendo relacionamento entre as tabelas
    aluno = db.relationship('Alunos', backref='alocacaoAlunos')
    transporte = db.relationship('AlocacaoViagens', backref='alocacaoAlunos')
