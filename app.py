from flask import Flask, render_template, request, redirect, url_for, flash
import os
from dotenv import load_dotenv
import bcrypt
from flask_login import LoginManager, login_user, login_required, logout_user, current_user 
import re

from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer as Serializer


import smtplib #biblioteca necesária para o envio de e-mail
from email.mime.text import MIMEText #Biblioteca para usar no e-mail
from email.mime.multipart import MIMEMultipart #Biblioteca para usar no e-mail

from models import Usuarios
from config import db # Importa o inicializador do banco de dados
load_dotenv()

app = Flask(__name__)
# Instancia o gerenciador de autenticação do Flask-Login.
# Essa linha cria o objeto LoginManager, responsável por controlar o fluxo de login,
# logout, verificação de sessão e redirecionamento de usuários não autenticados.
logMan = LoginManager(app)
#O view redireciona para a rota que realiza o login evitando que usuario sem acesso receba a mensagem de não autorizado em uma página 401
logMan.login_view = "/"
#Mensagem que aparecerá na pagina de login
logMan.login_message = "Você precisa estar logado para acessar esta página."
logMan.login_message_category = "warning"
CHAVE_SECRETA = os.getenv("CHAVESEGURA")
app.secret_key = CHAVE_SECRETA

POSTGRES_URI = os.getenv("DATABASE_URL")
# Verificações básicas para garantir que as variáveis do DB foram carregadas
if not POSTGRES_URI:
    raise ValueError("DATABASE_URL não definida! Verifique o arquivo .env ou variáveis de ambiente")
    
app.config["SQLALCHEMY_DATABASE_URI"] = POSTGRES_URI
db.init_app(app)




#-----------------------------------------Funções--------------------------------------------------------#
#Metodo necessário para acessar o site sem o login realizado.
@logMan.user_loader
def load_user(user_id):
    return None  # Nenhum usuário será carregado por enquanto

#--------------------------------------------------------------------------------------------------------#

#Função que verifica se o e-mail foi escrito dentro do padrão correto#
def verifica_email(email):
    #Expressão regular para verificação da escrita correta de e-mail.
    # "exemplo" + @ + "email" . "com" e ou ."br"
    padrao = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"

    if re.fullmatch(padrao, email):
        return True
    else:
        return False
    
#--------------------------------------------------------------------------------------------------------#  

#Função que formata os nomes para deixar padronizdo com as iniciais maiúsculas#
def formatar_nome(nome):
    particulas = {"da", "das", "de", "do", "dos", "e"}
    # Aplica title() pra capitalizar
    nome_formatado = nome.title()
    
    # Quebrar o nome em palavras para avaliar as partículas
    palavras = nome_formatado.split()
    
    # Ajustar partículas para minúsculo
    resultado = []
    for palavra in palavras:
        if palavra.lower() in particulas:
            resultado.append(palavra.lower())
        else:
            resultado.append(palavra)
    
    return " ".join(resultado)

#--------------------------------------------------------------------------------------------------------#
#Função que gera um token seguro para a confirmação de cadastro ou refazer a senha
s = Serializer(CHAVE_SECRETA)
def gerador_token(email):
    token = s.dumps(email, salt='email-confirm')
    return token

def enviar_confirmacao(email):
    token = gerador_token(email)
    confirm_url = url_for('confirm_email', token=token, _external=True)
    html = render_template('confirma_cadastro.html', confirm_url=confirm_url)
    # Aqui você chama sua função de envio de e-mail
    enviar_email(email, html)
#--------------------------------------------------------------------------------------------------------#
#Função que envia e-mail para a confirmar cadastro ou refazer a senha
def enviar_email(email, html):
    #Configurações
    port = os.getenv("port")
    smtp_server = os.getenv("smtp_server")
    login = os.getenv("login")  # Seu login gerado pelo Mailtrap
    password = os.getenv('password')  # Sua senha gerada pelo Mailtrap

    sender_email = os.getenv("sender_email")
    receiver_email = email
    # Conteúdo de email
    subject = "Confirmação de cadastro"
    # html = """\
    # <html>
    # <body>
    #     <p>Olá,<br>
    #     Este é um email de <b>confirmação do cadastro</b> clique no link a seguir para confirmar o teu cadastro <a href="http://127.0.0.1:5000/confirmar/{token}">Clique aqui para confirmar o cadastro</a><br>
    #     Atenciosamente a Equipe de Desenvolvedores.</p>
    # </body>
    # </html>
    # """

    # Criar uma mensagem multipart e definir cabeçalhos
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    # Anexar a parte em HTML
    message.attach(MIMEText(html, "html"))

    # Enviar o email
    with smtplib.SMTP(smtp_server, port) as server:
        server.starttls()
        server.login(login, password)
        server.sendmail(sender_email, receiver_email, message.as_string())

    print('Enviado')

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
    return redirect(url_for("index"))

#Rota para realização do login
@app.route("/login", methods=["GET", "POST"])
#Regra de negócio para acessar as páginas restritas
def login():
    if request.method== "POST":
        usuario = request.form.get("usuario", "").lower().strip()
        senha = request.form.get("senha","").lower().strip()
        print(f"Usuario {usuario} e senha {senha}")
        usuario_cadastrado = Usuarios.query.filter_by(usuario=usuario).first()
        if usuario_cadastrado:
            #Verificador se a senha com hash corresponde com a senha do salva
            if bcrypt.checkpw(senha.encode('utf-8'), usuario_cadastrado.senha):
                login_user(usuario_cadastrado)
                return redirect(url_for("home"))
            else:
                flash(f"Usuário ou senha inválidos", "danger")
                return redirect(url_for("login"))
        else:
            flash(f"Usuário ou senha inválidos", "danger")
            return redirect(url_for("login"))
    

    return render_template("login.html")
#Rota para cadastrar novos usuários
@app.route("/cadastro_usuarios", methods=["GET", "POST"])

def cadastro_usuario():
    if request.method == "POST":
        nome_recebido= request.form.get("nome","").strip() #as "" faz com que se o input vir sem dados o fluxo não quebre aos tentar aplicar o strip() é preciso validar o dado antes de enviar ao banco de dados
        nome= formatar_nome(nome_recebido)
        email = request.form.get("email", "").lower().strip()
        usuario = request.form.get("usuario", "").lower().strip()
        senha= request.form.get("senha", "").strip()
        perfilAcesso = request.form.get("opcao", "")

        
        ##---------------------------------------Validações---------------------------------------##
        #Nos campos obrigatórios se precisamos informar ao usuário qual campo foi preenchido de forma incorreta.
        #Assim as validações deve ser individualizadas e ao final, caso existam erros, retornar os erros ao usuário.
        #Inicia com um verificador de erros inicialmente configurado no False, na ocorrencia de erro irá modificar para TRUE
        existe_erro= False
        
        #Verifica se o nome está preenchido
        if not nome:
            flash("O campo 'Nome' é obrigatório.", "warning")
            existe_erro = True
        
        #Verifica se email está preenchido e se o formato está correto
        if not email:
            flash("O campo 'E-mail' é obrigatório.", "warning")
            existe_erro =True    
        #Verifica se no input o formato do e-mail está correto. Não estando retorna um aviso ao usuário
        elif not verifica_email(email):
            flash(f"{email} - Não corresponde ao padrão de e-mail:'exemplo@email.com'", "danger")
            existe_erro =True    
        
        #Verifica se o Usuário está preenchido
        if not usuario:
            flash("O campo 'Usuário' é obrigatório.", "warning")
            existe_erro =True    
        
        #Verifica se a senha está preenchida
        if not senha:
            flash("O campo 'Senha' é obrigatório.", "warning")
            existe_erro =True 
            
        if not perfilAcesso:
            flash("Por favor, selecione um perfil de acesso.", "danger")
            existe_erro =True   
        
        #Verifica se todos os campos foram preenchidos. Se não forem não realiza o cadastro e retorna uma informação ao usuário.
        #Na existencia de erro irá redirecionar para a página cadastro com as informações.            
        if existe_erro:
            return redirect(url_for("cadastro_usuarios"))

        #-------------------------------------------------------------------------------------------------------#
        #-------------------------------------Segundo nivel de verificação--------------------------------------#
        #Busca do Banco de dados se há usuario com o mesmo nome
        cadastro_existente = Usuarios.query.filter_by(usuario=usuario).first() #realiza a consulta no banco.
        
        #Verifica se o nome cadastrado já se encontra no banco de dados, se já constar retornará um aviso ao usuário
        if cadastro_existente:
            flash(f"Nome de usuário já existe! Por favor, utilize outro nome de usuário.", "warning")
            return redirect(url_for("cadastro_usuarios"))
        else:
        #Conversão da senha em hash pelo bcrypt
            hashed = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())
            novo_usuario = Usuarios(nome=nome, email=email, usuario=usuario,senha=hashed, perfilAcesso=perfilAcesso, confirmado=False)
            
            db.session.add(novo_usuario)
            db.session.commit()
            enviar_confirmacao(email)

            flash("Cadastro realizado! Verifique seu e-mail para confirmar o acesso.", "info")
            return redirect(url_for("cadastro_finalizar", email=novo_usuario.email))  # Evita resubmissão do formulário
        
    return render_template("cadastro_usuarios.html")
#Rota de para a página de confirmação do cadastros
@app.route('/cadastro_finalizar', methods=["POST", "GET"])
def cadastro_finalizar():
    email = request.args.get("email")
    return render_template("cadastro_finalizar.html", email=email)

#Rota para reenvio do e-mail
@app.route('/reenviar_confirmacao/<email>', methods=['GET'])
def reenviar_confirmacao(email):
    usuario = Usuarios.query.filter_by(email=email).first()

    if not usuario:
        flash("Usuário não encontrado.", "danger")
        return redirect(url_for("cadastro_finalizar", email=email))

    if usuario.confirmado:
        flash("Este e-mail já foi confirmado.", "info")
        return redirect(url_for("login"))

    enviar_confirmacao(email)
    flash("E-mail de confirmação reenviado com sucesso!", "success")
    return redirect(url_for("cadastro_finalizar", email=email))

#Rota para a página central da aplicação
@app.route("/home")
def home():
    return render_template("home.html")
    
@app.route("/recuperar_senha", methods=["POST", "GET"])
def recuperar():
    if request.method == "POST":
        email = request.form.get("email", "").lower().strip()
        print(email)
         #Busca do Banco de dados se há usuario com o mesmo nome
        cadastro_existente = Usuarios.query.filter_by(email=email).first() #realiza a consulta no banco.
        if not cadastro_existente:
            flash(f"E-mail informado não está cadastrado.Informe um e-mail cadastrado.", "warning")
            print('email invalido')
            return redirect(url_for("recuperar"))
        else:
            enviar_confirmacao(email)
            flash(f"E-mail enviado com sucesso.", "warning")
            print("email valido")
            return redirect(url_for("recuperar"))
    
    
    return render_template("recuperar_senha.html")
#Rota de confirmação para o cadastro
@app.route('/confirmar/<token>')
def confirm_email(token):
    s = Serializer(CHAVE_SECRETA)
    try:
        email = s.loads(token, salt='email-confirm', max_age=3600)  # 1 hora
         # Consulta ao banco
        usuario = Usuarios.query.filter_by(email=email).first()

        if not usuario:
            flash("Usuário não encontrado.", "danger")
            return redirect(url_for('login'))

        if usuario.confirmado:
            flash("E-mail já foi confirmado anteriormente.", "info")
            return redirect(url_for('login'))

        # Atualiza o status
        usuario.confirmado = True
        db.session.commit()

        flash("E-mail confirmado com sucesso!", "success")
        return redirect(url_for('login'))

    except SignatureExpired:
        flash("O link expirou. Solicite um novo.", "danger")
        return redirect(url_for('login'))
    except BadSignature:
        flash("Token inválido.", "danger")
        return redirect(url_for('login'))


if __name__ == "__main__":
    app.run(debug=True) 
    