from app import app
from config import db
from models import Usuarios # Importe todas as suas classes de modelo aqui

with app.app_context():
    # Isso cria as tabelas no banco de dados
    # Apenas se elas não existirem
    db.create_all()

    print("Banco de dados inicializado com sucesso!")