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


def gerador_token(email, salt):
    token = s.dumps(email, salt )
    return token

def enviar_confirmacao(email, salt, pagina, nome_funcao, assunto):
    token = gerador_token(email, salt)
    confirm_url = url_for(nome_funcao, token=token, _external=True)
    html = render_template(pagina, confirm_url=confirm_url)
    # Aqui você chama sua função de envio de e-mail
    enviar_email(email, html, assunto)
#--------------------------------------------------------------------------------------------------------#
#Função que envia e-mail para a confirmar cadastro ou refazer a senha
def enviar_email(email, html, assunto):
    #Configurações
    port = os.getenv("port")
    smtp_server = os.getenv("smtp_server")
    login = os.getenv("login")  # Seu login gerado pelo Mailtrap
    password = os.getenv('password')  # Sua senha gerada pelo Mailtrap

    sender_email = os.getenv("sender_email")
    receiver_email = email
    # Conteúdo de email
    subject = assunto
    

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
            #Variaveis para o envio da confirmação
            salt='email-confirm'
            pagina = 'confirma_cadastro.html'
            nome_funcao = 'confirm_email'
            assunto = "Confirmação de cadastro"

            enviar_confirmacao(email, salt, pagina, nome_funcao, assunto)

            flash("Cadastro realizado! Verifique seu e-mail para confirmar o acesso.", "info")
            return redirect(url_for("cadastro_finalizar", email=novo_usuario.email))  # Evita resubmissão do formulário
        
    return render_template("cadastro_usuarios.html")

#Rota de para a página de confirmação do cadastros
@app.route('/cadastro_finalizar', methods=["POST", "GET"])
def cadastro_finalizar():
    email = request.args.get("email")
    return render_template("cadastro_finalizar.html", email=email)

#Rota para reenvio do e-mail no caso do usuário não receber o e-mail que é enviado ao final do cadastro.
@app.route('/reenviar_confirmacao/<email>', methods=['GET'])
def reenviar_confirmacao(email):
    usuario = Usuarios.query.filter_by(email=email).first()

    if not usuario:
        flash("Usuário não encontrado.", "danger")
        return redirect(url_for("cadastro_finalizar", email=email))

    if usuario.confirmado:
        flash("Este e-mail já foi confirmado.", "info")
        return redirect(url_for("login"))
    #variavel do envio
    salt='email-confirm'
    pagina = 'confirma_cadastro.html'
    nome_funcao = 'confirm_email'
    assunto = "Confirmação de cadastro"
    
    enviar_confirmacao(email,salt,pagina,nome_funcao, assunto)
    flash("E-mail de confirmação reenviado com sucesso!", "success")
    return redirect(url_for("cadastro_finalizar", email=email))

#Rota para a página central da aplicação
@app.route("/home")
def home():
    return render_template("home.html")

#Rota para a recuperação da senha
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
            salt = 'reset-password'
            pagina = 'email_senha.html'
            nome_funcao = 'nova_senha'
            assunto = "Redefinir nova senha"

            enviar_confirmacao(email, salt, pagina, nome_funcao, assunto)
            
            flash(f"E-mail enviado com sucesso.", "warning")
            print("email valido")
            return redirect(url_for("recuperar"))
    
    
    return render_template("recuperar_senha.html")

#Rota de confirmação para o cadastro
#Essa rota é chamada no pelo link do e-mail e quando utlizada confirma o cadastro do usuário
#Mudando o seu status no banco de dados para "confirmado=True" que permitirá o acesso ao site.
@app.route('/confirmar/<token>')
def confirm_email(token):
    s = Serializer(CHAVE_SECRETA)
    try:
        email = s.loads(token, salt='email-confirm', max_age=1800)  # 30 minutos 
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

#Rota de redefinição de nova senha
@app.route('/redefinir/<token>', methods=["GET", "POST"])
def nova_senha(token):
    s = Serializer(CHAVE_SECRETA)
    try:
        email = s.loads(token, salt='reset-password', max_age=1800)  # 30 minutos 
         # Consulta ao banco
        usuario = Usuarios.query.filter_by(email=email).first()

        if not usuario:
            flash("Usuário não encontrado.", "danger")
            return redirect(url_for('login'))

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
                return redirect(url_for("nova_senha",token=token))
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
                return redirect(url_for('login', token=token))

        return render_template("nova_senha.html",token=token)

    except SignatureExpired:
        flash("O link expirou. Solicite um novo.", "danger")
        return redirect(url_for('login'))
    except BadSignature:
        flash("Token inválido.", "danger")
        return redirect(url_for('login'))