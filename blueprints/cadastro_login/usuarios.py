from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from itsdangerous import URLSafeTimedSerializer as Serializer, SignatureExpired, BadSignature
import bcrypt
from models import Usuarios
from config import db
from utils import enviar_confirmacao, formatar_nome, verifica_email, gerador_serializer
import os

usuarios_bp = Blueprint('usuarios', __name__)
#-------------------------------------------------------------------------------------------------------#
                    #---------Rotas de Usuários (Cadastro e Login)-------------#
                    #--Aqui são definidas as rotas relacionadas ao cadastro e login de usuários--#
#-------------------------------------------------------------------------------------------------------#

#--------------Rota para realização do login e logout do sistema.------------------#
#Rota para realizar o login no sistema.
@usuarios_bp.route("/login", methods=["GET", "POST"])
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
                return redirect(url_for("usuarios.login"))
        else:
            flash(f"Usuário ou senha inválidos", "danger")
            return redirect(url_for("usuarios.login"))
    

    return render_template("login.html")


#Rota para realizar o logout do sistema.
@usuarios_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logout realizado com sucesso.", "success")

    return redirect(url_for("index"))

#------------------------------------------------------------------------------------------------------#
#-Rotas para o cadastro de novos usuários, confirmação de cadastro e reenvio de e-mail de confirmação--#
#------------------------------------------------------------------------------------------------------#

#Rota para cadastrar novos usuários
@usuarios_bp.route("/cadastro_usuarios", methods=["GET", "POST"])

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
            return redirect(url_for("usuarios.cadastro_usuarios"))

        #-------------------------------------------------------------------------------------------------------#
        #-------------------------------------Segundo nivel de verificação--------------------------------------#
        #Busca do Banco de dados se há usuario com o mesmo nome
        cadastro_existente = Usuarios.query.filter_by(usuario=usuario).first() #realiza a consulta no banco.
        
        #Verifica se o nome cadastrado já se encontra no banco de dados, se já constar retornará um aviso ao usuário
        if cadastro_existente:
            flash(f"Nome de usuário já existe! Por favor, utilize outro nome de usuário.", "warning")
            return redirect(url_for("usuarios.cadastro_usuarios"))
        else:
        #Conversão da senha em hash pelo bcrypt
            hashed = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())
            novo_usuario = Usuarios(nome=nome, email=email, usuario=usuario,senha=hashed, perfilAcesso=perfilAcesso, confirmado=False)
            
            db.session.add(novo_usuario)
            db.session.commit()
            #Variaveis para o envio da confirmação
            salt='email-confirm'
            pagina = 'confirma_cadastro.html'
            nome_funcao = 'usuarios.confirm_email'
            assunto = "Confirmação de cadastro"

            enviar_confirmacao(email, salt, pagina, nome_funcao, assunto)

            flash("Cadastro realizado! Verifique seu e-mail para confirmar o acesso.", "info")
            return redirect(url_for("usuarios.cadastro_finalizar", email=novo_usuario.email))  # Evita resubmissão do formulário
        
    return render_template("cadastro_usuarios.html")

#Rota de confirmação para o cadastro
#Essa rota é chamada no pelo link do e-mail e quando utlizada confirma o cadastro do usuário
#Mudando o seu status no banco de dados para "confirmado=True" que permitirá o acesso ao site.
@usuarios_bp.route('/confirmar/<token>')
def confirm_email(token):
    s = gerador_serializer()
    try:
        email = s.loads(token, salt='email-confirm', max_age=1800)  # 30 minutos 
         # Consulta ao banco
        usuario = Usuarios.query.filter_by(email=email).first()

        if not usuario:
            flash("Usuário não encontrado.", "danger")
            return redirect(url_for('usuarios.login'))

        if usuario.confirmado:
            flash("E-mail já foi confirmado anteriormente.", "info")
            return redirect(url_for('usuarios.login'))

        # Atualiza o status
        usuario.confirmado = True
        db.session.commit()

        flash("E-mail confirmado com sucesso!", "success")
        return redirect(url_for('usuarios.login'))

    except SignatureExpired:
        flash("O link expirou. Solicite um novo.", "danger")
        return redirect(url_for('usuarios.login'))
    except BadSignature:
        flash("Token inválido.", "danger")
        return redirect(url_for('usuarios.login'))
    
#Rota de para a página de confirmação do cadastros
@usuarios_bp.route('/cadastro_finalizar', methods=["POST", "GET"])
def cadastro_finalizar():
    email = request.args.get("email")
    return render_template("cadastro_finalizar.html", email=email)

#Rota para reenvio do e-mail no caso do usuário não receber o e-mail que é enviado ao final do cadastro.
@usuarios_bp.route('/reenviar_confirmacao/<email>', methods=['GET'])
def reenviar_confirmacao(email):
    usuario = Usuarios.query.filter_by(email=email).first()

    if not usuario:
        flash("Usuário não encontrado.", "danger")
        return redirect(url_for("usuarios.cadastro_finalizar", email=email))

    if usuario.confirmado:
        flash("Este e-mail já foi confirmado.", "info")
        return redirect(url_for("usuarios.login"))
    #variavel do envio
    salt='email-confirm'
    pagina = 'confirma_cadastro.html'
    nome_funcao = 'usuarios.confirm_email'
    assunto = "Confirmação de cadastro"
    
    enviar_confirmacao(email,salt,pagina,nome_funcao, assunto)
    flash("E-mail de confirmação reenviado com sucesso!", "success")
    return redirect(url_for("usuarios.cadastro_finalizar", email=email))


#---------------------------------------------------------------------------------------------------#
#-----------------Rotas para recuperação e redefinição de senha de usuários-------------------------#
#---------------------------------------------------------------------------------------------------#

#Rota para a recuperação da senha
@usuarios_bp.route("/recuperar_senha", methods=["POST", "GET"])
def recuperar():
    if request.method == "POST":
        email = request.form.get("email", "").lower().strip()
        print(email)
         #Busca do Banco de dados se há usuario com o mesmo nome
        cadastro_existente = Usuarios.query.filter_by(email=email).first() #realiza a consulta no banco.
        
        if not cadastro_existente:
            flash(f"E-mail informado não está cadastrado.Informe um e-mail cadastrado.", "warning")
            print('email invalido')
            return redirect(url_for("usuarios.recuperar"))
        else:
            salt = 'reset-password'
            pagina = 'email_senha.html'
            nome_funcao = 'usuarios.nova_senha'
            assunto = "Redefinir nova senha"

            enviar_confirmacao(email, salt, pagina, nome_funcao, assunto)
            
            flash(f"E-mail enviado com sucesso.", "warning")
            print("email valido")
            return redirect(url_for("usuarios.recuperar"))
    
    
    return render_template("recuperar_senha.html")



#Rota de redefinição de nova senha
@usuarios_bp.route('/redefinir/<token>', methods=["GET", "POST"])
def nova_senha(token):
    s = gerador_serializer()
    try:
        email = s.loads(token, salt='reset-password', max_age=1800)  # 30 minutos 
         # Consulta ao banco
        usuario = Usuarios.query.filter_by(email=email).first()

        if not usuario:
            flash("Usuário não encontrado.", "danger")
            return redirect(url_for('usuarios.login'))

        if request.method =="POST":
            senha= request.form.get("senha", "").strip()
            confirmar_senha = request.form.get("confirmar_senha", "").strip()
            
            #Inicia com um verificador de erros inicialmente configurado no False, na ocorrencia de erro irá modificar para TRUE
            existe_erro= False
            #Verifica se a senha está preenchida
            if not senha:
                flash("O campo 'Senha' é obrigatório.", "warning")
                existe_erro =True 
            #Na existencia de erro irá redirecionar para a página cadastro com as informações.            
            if existe_erro:
                return redirect(url_for("usuarios.nova_senha",token=token))
            if senha != confirmar_senha:
                flash("As senhas não coincidem.", "warning")
                existe_erro = True
            else:
            # Atualiza o status
            #Critptografa a senha
                hashed = bcrypt.hashpw(senha.encode('utf-8'), bcrypt.gensalt())
                usuario.senha = hashed
                db.session.commit()

                flash("Senha alterada com sucesso!", "success")
                return redirect(url_for('usuarios.login', token=token))

        return render_template("nova_senha.html",token=token)

    except SignatureExpired:
        flash("O link expirou. Solicite um novo.", "danger")
        return redirect(url_for('usuarios.login'))
    except BadSignature:
        flash("Token inválido.", "danger")
        return redirect(url_for('usuarios.login'))