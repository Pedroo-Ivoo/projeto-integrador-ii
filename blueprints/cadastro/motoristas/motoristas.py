from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from config import db
from models import Motoristas, Regioes, Usuarios
from utils import cadastro_ativo, perfis_permitidos, formatar_nome, verifica_email


motoritas_bp = Blueprint('motoristas', __name__)


@motoritas_bp.route('/cadastro_motoristas', methods=['GET', 'POST'])
@login_required
@cadastro_ativo
@perfis_permitidos(['Admin', 'Motorista'])
def cadastro_motoristas():
    try:
        perfil = current_user.perfilAcesso
        nome_usuario = current_user.nome
        
        if request.method == "GET":
            if current_user.perfilAcesso == "Motorista":
                nome = current_user.nome
                sobrenome = current_user.sobrenome
                email = current_user.email
                return render_template('cadastro_motoristas.html', nome=nome, sobrenome=sobrenome, email=email, perfil=perfil, nome_usuario=nome_usuario)
            else:
                return render_template('cadastro_motoristas.html', perfil=perfil, nome_usuario=nome_usuario)
        elif request.method == "POST":
            data = request.get_json()
            nome_recebido = data.get('nome', "").strip()
            sobrenome_recebido = data.get('sobrenome', "").strip()
            email = data.get('email', "").strip().lower()
            telefone = data.get('telefone', "").strip()

            
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
            #Verifica se email está preenchido e se o formato está correto
            if not email:
                erros.append("O campo 'E-mail' é obrigatório.")    
            #Verifica se no input o formato do e-mail está correto. Não estando retorna um aviso ao usuário
            elif not verifica_email(email):
                erros.append("O e-mail não corresponde ao padrão de e-mail:'exemplo@email.com'")    
            
            #Verifica se o telefone está preenchido            
            if not telefone:
                erros.append("O campo 'Telefone' é obrigatório.")   
            
            #Verifica se todos os campos foram preenchidos. Se não forem não realiza o cadastro e retorna uma informação ao usuário.
            #Na existencia de erro irá redirecionar para a página cadastro com as informações.            
            if erros:
                return jsonify({"erros": erros}), 400

            #-------------------------------------------------------------------------------------------------------#
            #-------------------------------------Segundo nivel de verificação--------------------------------------#
            #Busca do Banco de dados se há usuario com o mesmo nome
            cadastro_existente = Motoristas.query.filter_by(nome=nome, sobrenome=sobrenome).first() #realiza a consulta no banco.
            
            #Verifica se o nome cadastrado já se encontra no banco de dados, se já constar retornará um aviso ao usuário
            if cadastro_existente:
                return jsonify({"erros": ["Motorista já cadastrado."]}), 409
            #Caso não haja cadastro existente, realiza o cadastro
            else:
                usuario = Usuarios.query.get(current_user.id)
                novo_motorista = Motoristas(nome=nome,sobrenome=sobrenome, email=email, telefone=telefone, usuario =usuario)
                
                db.session.add(novo_motorista)
                db.session.commit()
                print("comitei aqui")
                #Variaveis para o envio da confirmação
                

                
                return jsonify({"mensagem": "Cadastro realizado!"}), 201
            
    except Exception as e:
           return jsonify({"erro": str(e)}), 500
        
    #Edição do cadastro dos motoristas
@motoritas_bp.route('/lista_motorista', methods=["GET", "POST"])
@login_required
@cadastro_ativo
@perfis_permitidos(['Admin', 'Motorista'])
def lista_motorista():
    try:
        perfil = current_user.perfilAcesso
        nome_usuario = current_user.nome
        if request.method == "GET":
            if perfil =="Admin":
                motoristas = Motoristas.query.all()
                return render_template("lista_motoristas_editar.html", perfil=perfil, nome_usuario=nome_usuario, motoristas=motoristas)
            else:
                motoristas = Motoristas.query.filter_by(usuario_id=current_user.id).all()
                return render_template("lista_motoristas_editar.html", perfil=perfil, nome_usuario=nome_usuario, motoristas=motoristas)
    except Exception as e:
           return jsonify({"erro": str(e)}), 500
            
 #   Edição do cadastro dos motoristas           
@motoritas_bp.route('/<int:id>/editar_motorista', methods=["GET", "PUT"])
@login_required
@cadastro_ativo
@perfis_permitidos(['Admin', 'Motorista'])
def editar_motorista(id):
    try:
        perfil = current_user.perfilAcesso
        nome_usuario = current_user.nome
        motorista = Motoristas.query.get(id)
        if not motorista:
            return jsonify({"erro": "Motorista não encontrado"}), 404
        if request.method == "GET":
            if current_user.perfilAcesso == "Motorista":
                nome = motorista.nome
                sobrenome = motorista.sobrenome
                email = motorista.email
                telefone = motorista.telefone
                return render_template('editar_motoristas.html', nome=nome, sobrenome=sobrenome, email=email, perfil=perfil, nome_usuario=nome_usuario, telefone=telefone, motorista=motorista)
            else:
                nome = motorista.nome
                sobrenome = motorista.sobrenome
                email = motorista.email
                telefone = motorista.telefone
                return render_template('editar_motoristas.html', nome=nome, sobrenome=sobrenome, email=email, perfil=perfil, nome_usuario=nome_usuario, telefone=telefone, motorista=motorista)
                
        elif request.method == "PUT":
            data = request.get_json()
            nome_recebido = data.get('nome', "").strip()
            sobrenome_recebido = data.get('sobrenome', "").strip()
            email = data.get('email', "").strip().lower()
            telefone = data.get('telefone', "").strip()

            
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
            #Verifica se email está preenchido e se o formato está correto
            if not email:
                erros.append("O campo 'E-mail' é obrigatório.")    
            #Verifica se no input o formato do e-mail está correto. Não estando retorna um aviso ao usuário
            elif not verifica_email(email):
                erros.append("O e-mail não corresponde ao padrão de e-mail:'exemplo@email.com'")    
            
            #Verifica se o telefone está preenchido            
            if not telefone:
                erros.append("O campo 'Telefone' é obrigatório.")   
            
            #Verifica se todos os campos foram preenchidos. Se não forem não realiza o cadastro e retorna uma informação ao usuário.
            #Na existencia de erro irá redirecionar para a página cadastro com as informações.            
            if erros:
                return jsonify({"erros": erros}), 400

            #-------------------------------------------------------------------------------------------------------#
            #-------------------------------------Segundo nivel de verificação--------------------------------------#
            #Verifica se o usuario é o mesmo  do cadastro para poder editar
            if perfil == "Motorista" and motorista.usuario.id != current_user.id:
                return jsonify({"erro": "Acesso negado"}), 403
            #Caso não haja cadastro existente, realiza o cadastro
            else:
                motorista.nome = nome
                motorista.sobrenome = sobrenome 
                motorista.email = email
                motorista.telefone = telefone
                
                db.session.commit()
                print("comitei aqui")
                #Variaveis para o envio da confirmação
                

                
                return jsonify({"mensagem": "Cadastro atualizado!"}), 200
            
    except Exception as e:
           return jsonify({"erro": str(e)}), 500
        
#    Rota para deletar motorista
@motoritas_bp.route('/<int:id>/excluir_motorista', methods=["DELETE"])
@login_required
@cadastro_ativo
@perfis_permitidos(['Admin'])
def excluir_motorista(id):
    motorista = Motoristas.query.get(id)
    if not motorista:
        return jsonify({"erro": "Motorista não encontrado"}), 404

    # if motorista.onibus or motorista.viagens or motorista.rotas:
    #     return jsonify({"erro": "Este motorista está vinculado a outros registros e não pode ser excluído."}), 400

    db.session.delete(motorista)
    db.session.commit()
    return jsonify({"mensagem": "Motorista excluído com sucesso!"}), 200