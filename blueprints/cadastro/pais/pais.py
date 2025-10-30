from flask import Blueprint, jsonify, render_template, request, redirect, url_for
from flask_login import login_required, current_user
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
                
            #Verifica se a região está preenchida
            if not regiao:
                erros.append("O campo 'Região' é obrigatório.") 
               
            
            #Verifica se todos os campos foram preenchidos. Se não forem não realiza o cadastro e retorna uma informação ao usuário.
            #Na existencia de erro irá redirecionar para a página cadastro com as informações.            
            if erros:
                return jsonify({"erros": erros}), 400

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
            
            #-------------------------------------Segundo nivel de verificação--------------------------------------#
            #Busca do Banco de dados se há usuario com o mesmo nome
            cadastro_existente = Pais.query.filter_by(nome=nome, sobrenome=sobrenome).first() #realiza a consulta no banco.
            
            #Verifica se o nome cadastrado já se encontra no banco de dados, se já constar retornará um aviso ao usuário
            if cadastro_existente:
                return jsonify({"erros": ["Pai ou Responsável já cadastrado."]}), 409
            #Caso não haja cadastro existente, realiza o cadastro
            else:
                regiao_obj = Regioes.query.filter_by(regiao=regiao).first()
                usuario_obj = Usuarios.query.get(current_user.id)
                novo_pai = Pais(nome=nome,sobrenome=sobrenome, email=email, telefone=telefone, cep=cep, rua=rua, numero=numero, complemento=complemento,bairro=bairro,latitude=latitude,longitude=longitude, regiao=regiao, regiao_obj= regiao_obj, usuario_obj =usuario_obj)
                
                db.session.add(novo_pai)
                db.session.commit()
                print("comitei aqui")
                #Variaveis para o envio da confirmação
                

                
                return jsonify({"mensagem": "Cadastro realizado!"}), 201
            
    except Exception as e:
           return jsonify({"erro": str(e)}), 500
        