from app import app
from config import db
from models import Usuarios, Regioes, Motoristas, Pais, Alunos, Veiculos  # Importe todas as suas classes de modelo aqui

with app.app_context():
    # Isso cria as tabelas no banco de dados
    # Apenas se elas não existirem
    db.create_all()
    
    # Inserindo regiões padrão na tabela Regioes
    regioes_padrao = [
        Regioes(regiao='Norte'),
        Regioes(regiao='Sul'),
        Regioes(regiao='Leste'),
        Regioes(regiao='Oeste'),
        Regioes(regiao='Centro')
    ]
    if not Regioes.query.first():
        db.session.add_all(regioes_padrao)
        db.session.commit()

   

    
  

    print("Banco de dados inicializado com sucesso!")