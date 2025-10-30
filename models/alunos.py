from config import db
from models import Pais
# Define a classe Alunos que representa a tabela de Alunos no banco de dados
class Alunos(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), nullable=False)
    sobrenome = db.Column(db.String(150), nullable=False)
    
    id_pais = db.Column(db.Integer, db.ForeignKey('pais.id'), nullable=False)
    #Estabelecendo relacionamento entre as tabelas
    pais = db.relationship('Pais', backref='alunos')
     
