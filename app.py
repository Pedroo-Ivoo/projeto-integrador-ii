from flask import Flask, render_template, request, redirect, url_for, flash
import os
from dotenv import load_dotenv
from flask_login import LoginManager, login_user, login_required, logout_user, current_user 

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer as Serializer



from models import Usuarios
from config import db # Importa o inicializador do banco de dados

from blueprints import usuarios_bp  # Importa o blueprint de usuários
load_dotenv()

app = Flask(__name__)
# Instancia o gerenciador de autenticação do Flask-Login.
# Essa linha cria o objeto LoginManager, responsável por controlar o fluxo de login,
# logout, verificação de sessão e redirecionamento de usuários não autenticados.
logMan = LoginManager(app)
#O view redireciona para a rota que realiza o login evitando que usuario sem acesso receba a mensagem de não autorizado em uma página 401
logMan.login_view = "login"
#Mensagem que aparecerá na pagina de login
logMan.login_message = "Você precisa estar logado para acessar esta página."
logMan.login_message_category = "warning"

CHAVE_SECRETA = os.getenv("CHAVESEGURA")
app.secret_key = CHAVE_SECRETA
s = Serializer(CHAVE_SECRETA)

POSTGRES_URI = os.getenv("DATABASE_URL")
# Verificações básicas para garantir que as variáveis do DB foram carregadas
if not POSTGRES_URI:
    raise ValueError("DATABASE_URL não definida! Verifique o arquivo .env ou variáveis de ambiente")
    
app.config["SQLALCHEMY_DATABASE_URI"] = POSTGRES_URI
db.init_app(app)

# Registro do blueprint de usuários
app.register_blueprint(usuarios_bp)



#-----------------------------------------Funções--------------------------------------------------------#
#Metodo necessário para acessar o site sem o login realizado.
@logMan.user_loader #quando estamos logado o que fica guardado é o id
def user_loader(id):
    usuario = Usuarios.query.filter_by(id=id).first()
    return usuario
#-------------------------------------Endpoints---------------------------------------------#
#Rota da página inicial
@app.route('/')
def index():
    return render_template("index.html")

#Rota para realizar o logout do sistema.
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logout realizado com sucesso.", "success")

    return redirect(url_for("index"))

#Rota para a página central da aplicação
@app.route("/home")
def home():
    return render_template("home.html")

    
if __name__ == "__main__":
    app.run(debug=True) 
    