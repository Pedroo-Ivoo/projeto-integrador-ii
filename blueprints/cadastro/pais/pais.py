from flask import Blueprint, jsonify, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError
from config import db
from models import Pais, Regioes, Usuarios
from utils import cadastro_ativo, perfis_permitidos, formatar_nome, verifica_email, geocodificar_endereco

pais_bp = Blueprint('pais', __name__)

@pais_bp.route('/cadastro_pais', methods=['GET', 'POST'])
@login_required
@cadastro_ativo
@perfis_permitidos(['Admin', 'Pais'])
def cadastro_pais():
    try:
        perfil = current_user.perfilAcesso
        nome_usuario = current_user.nome
        
        #Ao acessa a rota via GET, renderiza o template de cadastro se o pefil de acessso for pais cai no primeiro if e carrega os dados do usuário logado
        #Se for admin cai no else e carrega o template vazio
        if request.method == "GET":
            if current_user.perfilAcesso == "Pais":
                nome = current_user.nome
                sobrenome = current_user.sobrenome
                email = current_user.email
                
                return render_template('cadastro_pais.html', nome=nome, sobrenome=sobrenome, email=email, perfil=perfil, nome_usuario=nome_usuario)
            else:
                return render_template('cadastro_pais.html', perfil=perfil, nome_usuario=nome_usuario)
        # Qyuando a rota é acessada via POST, ou seja, quando o formulário é submetido, processa os dados recebidos por via JSON
        elif request.method == "POST":
            data = request.get_json()
            nome_recebido = data.get('nome', "").strip()
            sobrenome_recebido = data.get('sobrenome', "").strip()
            email = data.get('email', "").strip().lower()
            telefone = data.get('telefone', "").strip()
            cep =  data.get('cep', "").strip()
            rua_recebido = data.get('rua', "").strip()
            numero = data.get('numero', "").strip()
            complemento_recebido = data.get('complemento', "").strip()
            cidade = data.get('cidade', "").strip().title()
            estado = data.get('estado', "").strip().upper()
            bairro_recebido = data.get('bairro', "").strip()
            regiao = data.get('regiao').title()

            
            nome = formatar_nome(nome_recebido)
            sobrenome = formatar_nome(sobrenome_recebido)
            rua = formatar_nome(rua_recebido)
            complemento = formatar_nome(complemento_recebido)
            bairro = formatar_nome(bairro_recebido)
            # (nome=nome,sobrenome=sobrenome, email=email, telefone=telefone, cep=cep, rua=rua, complemento=complemento,bairro=bairro, regiao=regiao, regiao_obj= regiao_obj, usuario_obj =usuario_obj)
            ##---------------------------------------Validações---------------------------------------##
            #Nos campos obrigatórios se precisamos informar ao usuário qual campo foi preenchido de forma incorreta.
            #Assim as validações deve ser individualizadas e ao final, caso existam erros, retornar os erros ao usuário.
            #Inicia com um verificador de erros que será uma lista vazia, já que irá armazenar os erros e depois exibir no html
            erros= []
            
            #Verifica se o nome está preenchido
            if not nome:
                erros.append("O campo 'Nome' é obrigatório.") 
                
            #Verifica se o sobrenome está preenchido
            if not sobrenome:
                erros.append("O campo 'Sobrenome' é obrigatório.") 
                           
            #Verifica se email está preenchido e se o formato está correto
            if not email:
                erros.append("O campo 'E-mail' é obrigatório.")  
                  
            #Verifica se no input o formato do e-mail está correto. Não estando retorna um aviso ao usuário
            elif not verifica_email(email):
                erros.append("O e-mail não corresponde ao padrão de e-mail:'exemplo@email.com'")    
            
            #Verifica se o telefone está preenchido            
            if not telefone:
                erros.append("O campo 'Telefone' é obrigatório.")
                
            #Verifica se o cep está preenchido            
            if not cep:
                erros.append("O campo 'CEP' é obrigatório.")
                
            #Verifica se a rua está preenchida
            if not rua:
                erros.append("O campo 'Rua' é obrigatório.")
                
            #Verifica se o número está preenchido
            if not numero:        
                erros.append("O campo 'Número' é obrigatório.")
                
            #Verifica se o bairro está preenchido
            if not bairro:
                erros.append("O campo 'Bairro' é obrigatório.")
                
            #Verifica se a cidade está preenchida
            if not cidade:
                erros.append("O campo 'Cidade' é obrigatório.")
            #Verifica se o estado está preenchido
            if not estado:
                erros.append("O campo 'Estado' é obrigatório.")
            #Verifica se a região está preenchida
            if not regiao:
                erros.append("O campo 'Região' é obrigatório.") 
            #Verifica se o e-mail já está cadastrado
            email_existente = Pais.query.filter_by(email=email).first()
            if email_existente:
                erros.append(f"O e-mail '{email}' já está cadastrado para outro responsável. Informe um e-mail único.")
               
            
            #Verifica se todos os campos foram preenchidos. Se não forem não realiza o cadastro e retorna uma informação ao usuário.
            #Na existencia de erro irá redirecionar para a página cadastro com as informações.            
            if erros:
                return jsonify({"erros": erros}), 400

            #-------------------------------------Segundo nivel de verificação--------------------------------------#
            #Busca do Banco de dados se há usuario com o mesmo nome
            cadastro_existente = Pais.query.filter_by(nome=nome, sobrenome=sobrenome).first() #realiza a consulta no banco.
            
            #Verifica se o nome cadastrado já se encontra no banco de dados, se já constar retornará um aviso ao usuário
            if cadastro_existente:
                return jsonify({"erros": ["Pai ou Responsável já cadastrado."]}), 409
            

            #-------------------------------------------------------------------------------------------------------#
            
            ## -------------------------- NOVO PASSO: GEOCODIFICAÇÃO ----------------------------- ##
            
            # 1. Monta o endereço o mais completo possível
            # Ajuste esta string para refletir os campos que você tem no seu formulário/DB
            endereco_para_api = f"{rua} {numero}, {bairro}, {cep}, Brasil" # Adicione cidade/estado se disponíveis
            
            # 2. Chama a função de geocodificação (assumindo que você a importou)
            latitude, longitude = geocodificar_endereco(endereco_para_api)
            
            # 3. Valida se a geocodificação foi bem-sucedida
            if latitude is None or longitude is None:
                erros.append("Não foi possível localizar o endereço no mapa. Verifique se o endereço (Rua, Número, CEP) está correto.")
                return jsonify({"erros": erros}), 400

            ## -------------------------- FIM: GEOCODIFICAÇÃO ----------------------------- ##
            
            
            
            #Caso não haja cadastro existente, realiza o cadastro
            
            regiao_obj = Regioes.query.filter_by(regiao=regiao).first()
            usuario_obj = Usuarios.query.get(current_user.id)
            novo_pai = Pais(nome=nome,sobrenome=sobrenome, email=email, telefone=telefone, cep=cep, rua=rua, numero=numero, complemento=complemento,bairro=bairro,cidade=cidade, estado=estado ,latitude=latitude,longitude=longitude, regiao=regiao, regiao_obj= regiao_obj, usuario_obj =usuario_obj)
            
            db.session.add(novo_pai)
            db.session.commit()
            #Variaveis para o envio da confirmação
            

            
            return jsonify({"mensagem": "Cadastro realizado!"}), 201
        
    except Exception as e:
           return jsonify({"erro": str(e)}), 500
        

    #Edição do cadastro dos pais
@pais_bp.route('/lista_pais', methods=["GET", "POST"])
@login_required
@cadastro_ativo
@perfis_permitidos(['Admin', 'Pais'])
def lista_pais():
    try:
        perfil = current_user.perfilAcesso
        nome_usuario = current_user.nome
        if request.method == "GET":
            pais = Pais.query.all()
            return render_template("lista_pais_editar.html", perfil=perfil, nome_usuario=nome_usuario, pais=pais)
    except Exception as e:
           return jsonify({"erro": str(e)}), 500
            
 #   Edição do cadastro dos motoristas           
@pais_bp.route('/<int:id>/editar_pai', methods=["GET", "PUT"])
@login_required
@cadastro_ativo
@perfis_permitidos(['Admin', 'Pais'])
def editar_pai(id):
    try:
        perfil = current_user.perfilAcesso
        nome_usuario = current_user.nome
        pai = Pais.query.get(id)
        if not pai:
            return jsonify({"erro": "Pai não encontrado"}), 404
        if request.method == "GET":
            nome = pai.nome
            sobrenome  = pai.sobrenome
            email = pai.email
            telefone = pai.telefone
            cep =  pai.cep
            rua = pai.rua
            numero = pai.numero
            complemento = pai.complemento
            bairro = pai.bairro
            cidade = pai.cidade
            estado = pai.estado
            regiao = pai.regiao
            
            return render_template('editar_pais.html', nome=nome, sobrenome=sobrenome, email=email, telefone=telefone, cep=cep, rua=rua, numero=numero, complemento=complemento,bairro=bairro, cidade=cidade, estado=estado, regiao=regiao, perfil=perfil, nome_usuario=nome_usuario, pai=pai)
                
            
                
        elif request.method == "PUT":
            data = request.get_json()
            nome_recebido = data.get('nome', "").strip()
            sobrenome_recebido = data.get('sobrenome', "").strip()
            email = data.get('email', "").strip().lower()
            telefone = data.get('telefone', "").strip()
            cep =  data.get('cep', "").strip()
            rua_recebido = data.get('rua', "").strip()
            numero = data.get('numero', "").strip()
            complemento_recebido = data.get('complemento', "").strip()
            bairro_recebido = data.get('bairro', "").strip()
            regiao = data.get('regiao').title()

            
            nome = formatar_nome(nome_recebido)
            sobrenome = formatar_nome(sobrenome_recebido)
            rua = formatar_nome(rua_recebido)
            complemento = formatar_nome(complemento_recebido)
            bairro = formatar_nome(bairro_recebido)
            
            ##---------------------------------------Validações---------------------------------------##
            #Nos campos obrigatórios se precisamos informar ao usuário qual campo foi preenchido de forma incorreta.
            #Assim as validações deve ser individualizadas e ao final, caso existam erros, retornar os erros ao usuário.
            #Inicia com um verificador de erros que será uma lista vazia, já que irá armazenar os erros e depois exibir no html
            erros= []
            
            #Verifica se o nome está preenchido
            if not nome:
                erros.append("O campo 'Nome' é obrigatório.") 
                
            #Verifica se o sobrenome está preenchido
            if not sobrenome:
                erros.append("O campo 'Sobrenome' é obrigatório.") 
                           
            #Verifica se email está preenchido e se o formato está correto
            if not email:
                erros.append("O campo 'E-mail' é obrigatório.")  
                  
            #Verifica se no input o formato do e-mail está correto. Não estando retorna um aviso ao usuário
            elif not verifica_email(email):
                erros.append("O e-mail não corresponde ao padrão de e-mail:'exemplo@email.com'")    
            
            #Verifica se o telefone está preenchido            
            if not telefone:
                erros.append("O campo 'Telefone' é obrigatório.")
                
            #Verifica se o cep está preenchido            
            if not cep:
                erros.append("O campo 'CEP' é obrigatório.")
                
            #Verifica se a rua está preenchida
            if not rua:
                erros.append("O campo 'Rua' é obrigatório.")
                
            #Verifica se o número está preenchido
            if not numero:        
                erros.append("O campo 'Número' é obrigatório.")
                
            #Verifica se o bairro está preenchido
            if not bairro:
                erros.append("O campo 'Bairro' é obrigatório.")
                
            #Verifica se a região está preenchida
            if not regiao:
                erros.append("O campo 'Região' é obrigatório.") 
               
            
            #Verifica se todos os campos foram preenchidos. Se não forem não realiza o cadastro e retorna uma informação ao usuário.
            #Na existencia de erro irá redirecionar para a página cadastro com as informações.            
            if erros:
                return jsonify({"erros": erros}), 400

            #-------------------------------------------------------------------------------------------------------#
            
            ## -------------------------- INÍCIO: GEOCODIFICAÇÃO CORRIGIDA ----------------------------- ##
        
        # 1. Inicializa latitude e longitude com os valores ATUAIS do banco de dados
            latitude = pai.latitude
            longitude = pai.longitude

            # 2. Só chama a API Geocoding se o CEP for diferente
            if cep != pai.cep:
                
                endereco_para_api = f"{rua} {numero}, {bairro}, {cep}, Brasil"
                
                # Chama a função de geocodificação (assumindo que você a importou)
                nova_latitude, nova_longitude = geocodificar_endereco(endereco_para_api)
                
                # Valida se a geocodificação foi bem-sucedida
                if nova_latitude is None or nova_longitude is None:
                    erros.append("Não foi possível localizar o endereço no mapa. Verifique se o endereço (Rua, Número, CEP) está correto.")
                    return jsonify({"erros": erros}), 400
                    
                # Se bem-sucedido, atualiza as variáveis a serem salvas
                latitude = nova_latitude
                longitude = nova_longitude

            ## -------------------------- FIM: GEOCODIFICAÇÃO ----------------------------- ##
            
            
          
            pai.nome = nome
            pai.sobrenome = sobrenome
            pai.email = email
            pai.telefone = telefone
            pai.cep = cep
            pai.rua = rua
            pai.numero = numero
            pai.complemento = complemento
            pai.bairro = bairro
            pai.regiao = regiao
            pai.latitude = latitude
            pai.longitude = longitude
            
            db.session.commit()
            #Variaveis para o envio da confirmação
            

            
            return jsonify({"mensagem": "Cadastro Atualizdo!"}), 200
        
    except Exception as e:
           return jsonify({"erro": str(e)}), 500
            
           
        
#    Rota para deletar motorista
@pais_bp.route('/<int:id>/excluir_pai', methods=["DELETE"])
@login_required
@cadastro_ativo
@perfis_permitidos(['Admin'])
def excluir_pai(id):
    pai = Pais.query.get(id)
    if not pai:
        return jsonify({"erro": "Pai não encontrado"}), 404
    try:
        db.session.delete(pai)
        db.session.commit()
        return jsonify({"mensagem": "Veículo excluído com sucesso!"}), 200
    except IntegrityError as e:
        # Se houver um erro de integridade (restrição de chave estrangeira, NOT NULL, etc.)
        db.session.rollback() # MUITO IMPORTANTE: Reverter a transação em caso de erro

        # Log do erro para depuração
        print(f"Erro de Integridade ao excluir {pai}: {e}")
        
        # Verifica a origem do erro (opcional, mas bom para mensagens específicas)
        # O erro 'NotNullViolation' indica que há registros dependentes.
        # Log do erro para depuração (Mantenha o log para identificar qual tabela causou o erro)
        print(f"Erro de Integridade ao excluir: {e}") 
        
        # Mensagem única e abrangente para todas as violações de integridade (Foreign Key, Not Null, etc.)
        mensagem_erro = "Não foi possível excluir o Pai/Responsável. Ele está vinculado a um Aluno na 'Cadastro de Alunos' e deve ser desassociado primeiro. Obs. Se o aluno estiver associado a alguma rota é preciso remover essas vinculações antes de excluir o aluno e posteriormente o pai/responsável."

        return jsonify({"erro": mensagem_erro}), 409

    except Exception as e:
        # Tratar outros erros inesperados
        db.session.rollback()
        return jsonify({"erro": f"Erro inesperado no servidor: {e}"}), 500