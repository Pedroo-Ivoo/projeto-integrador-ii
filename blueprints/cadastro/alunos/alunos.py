from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from config import db
from models import Motoristas, Regioes, Usuarios, Pais, Alunos
from utils import cadastro_ativo, perfis_permitidos, formatar_nome, verifica_email

alunos_bp = Blueprint('alunos', __name__)


@alunos_bp.route('/cadastro_alunos', methods=['GET', 'POST'])
@login_required
@cadastro_ativo
@perfis_permitidos(['Admin', 'Pais'])
def cadastro_alunos():
    try:
        perfil = current_user.perfilAcesso
        nome_usuario = current_user.nome
        
        if request.method == "GET":
            if current_user.perfilAcesso == 'Pais':
                responsavel = Pais.query.filter_by(id_usuario=current_user.id).first()
                return render_template('cadastro_alunos.html', perfil=perfil, nome_usuario=nome_usuario, responsavel=responsavel)
            else:
                responsavel = Pais.query.all()
                return render_template('cadastro_alunos.html', perfil=perfil, nome_usuario=nome_usuario, responsavel=responsavel)
        elif request.method == "POST":
            data = request.get_json()
            nome_recebido = data.get('nome', "").strip()
            sobrenome_recebido = data.get('sobrenome', "").strip()
            id_responsavel = data.get('id_responsavel', "").strip() 

            
            nome = formatar_nome(nome_recebido)
            sobrenome = formatar_nome(sobrenome_recebido)
            
            
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
            
            #Verifica se o responsavel está preenchido
            if not id_responsavel:
                erros.append("O campo 'Responsável' é obrigatório.")            
           
            
            #Verifica se todos os campos foram preenchidos. Se não forem não realiza o cadastro e retorna uma informação ao usuário.
            #Na existencia de erro irá redirecionar para a página cadastro com as informações.            
            if erros:
                return jsonify({"erros": erros}), 400

            #-------------------------------------------------------------------------------------------------------#
            #-------------------------------------Segundo nivel de verificação--------------------------------------#
            #Busca do Banco de dados se há um aluno com o mesmo nome
            cadastro_existente = Alunos.query.filter_by(nome=nome, sobrenome=sobrenome).first() #realiza a consulta no banco.
            
            #Verifica se o nome cadastrado já se encontra no banco de dados, se já constar retornará um aviso ao usuário
            if cadastro_existente:
                return jsonify({"erros": ["Aluno já cadastrado."]}), 409
            #Caso não haja cadastro existente, realiza o cadastro
            else:
                novo_aluno = Alunos(nome=nome,sobrenome=sobrenome, id_pais=id_responsavel)
                
                db.session.add(novo_aluno)
                db.session.commit()
                print("comitei aqui")
                #Variaveis para o envio da confirmação
                

                
                return jsonify({"mensagem": "Cadastro realizado!"}), 201
            
    except Exception as e:
           return jsonify({"erro": str(e)}), 500
        