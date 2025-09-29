
from flask import Flask, render_template, request, redirect, session, url_for, flash
import os
from dotenv import load_dotenv
from flask_login import LoginManager, login_user, login_required, logout_user, current_user 
from datetime import timedelta
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer as Serializer


from models import Usuarios
from config import db # Importa o inicializador do banco de dados

from blueprints import usuarios_bp, home_bp, motoritas_bp, pais_bp, alunos_bp # Importa o blueprint de usuários
from utils import cadastro_ativo, perfis_permitidos # Importa o decorador cadastro_ativo
load_dotenv()

app = Flask(__name__)
# Instancia o gerenciador de autenticação do Flask-Login.
# Essa linha cria o objeto LoginManager, responsável por controlar o fluxo de login,
# logout, verificação de sessão e redirecionamento de usuários não autenticados.
logMan = LoginManager(app)
#O view redireciona para a rota que realiza o login evitando que usuario sem acesso receba a mensagem de não autorizado em uma página 401
logMan.login_view = "usuarios.login"
#Mensagem que aparecerá na pagina de login
logMan.login_message = "Você precisa estar logado para acessar esta página."
logMan.login_message_category = "warning"
# Define a duração da sessão padrão para 1 hora.
# Após esse tempo, o usuário será deslogado automaticamente e precisará fazer login novamente.
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=1)

CHAVE_SECRETA = os.getenv("CHAVESEGURA")
app.secret_key = CHAVE_SECRETA
s = Serializer(CHAVE_SECRETA)

#Banco de dados local para testes
POSTGRES_URI = os.getenv("DATABASE_URL_LOCAL")

#Banco de dados hospedado no aiven
# POSTGRES_URI = os.getenv("DATABASE_URL")
# Verificações básicas para garantir que as variáveis do DB foram carregadas
if not POSTGRES_URI:
    raise ValueError("DATABASE_URL não definida! Verifique o arquivo .env ou variáveis de ambiente")
    
app.config["SQLALCHEMY_DATABASE_URI"] = POSTGRES_URI
db.init_app(app)

# Registro do blueprints
app.register_blueprint(usuarios_bp)
app.register_blueprint(home_bp)
app.register_blueprint(motoritas_bp)
app.register_blueprint(pais_bp)
app.register_blueprint(alunos_bp)



#-----------------------------------------Funções--------------------------------------------------------#
#Metodo necessário para acessar o site sem o login realizado.
@logMan.user_loader #quando estamos logado o que fica guardado é o id
def user_loader(id):
    usuario = Usuarios.query.filter_by(id=id).first()
    return usuario


# Antes de cada requisição, define a sessão como permanente para aplicar a duração configurada
# Assim a sessão será renovada a cada requisição, mantendo o usuário logado enquanto ele estiver ativo.
@app.before_request
def refresh_session():
    session.permanent = True  

#-------------------------------------Endpoints---------------------------------------------#
#Rota da página inicial
@app.route('/')
def index():
    return render_template("index.html")

    

@app.route("/pontodigital")
@login_required
@cadastro_ativo
@perfis_permitidos(["Motorista", "Admin"])
def pontodigital():
    return render_template("pontodigital.html")


if __name__ == "__main__":
    app.run(debug=True) 
    