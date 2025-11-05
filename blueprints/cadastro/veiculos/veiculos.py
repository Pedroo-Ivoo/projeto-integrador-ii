from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError

from config import db
from models import Motoristas, Regioes, Usuarios, Pais, Alunos, Veiculos
from utils import cadastro_ativo, perfis_permitidos, formatar_nome, verifica_email

veiculos_bp = Blueprint('veiculos', __name__)

# Cadastro de Veículos
@veiculos_bp.route('/cadastro_veiculos', methods=['GET', 'POST'])
@login_required
@cadastro_ativo
@perfis_permitidos(['Admin', 'Motorista'])
def cadastro_veiculos():
    try:
        perfil = current_user.perfilAcesso
        nome_usuario = current_user.nome
        
        if request.method == "GET":
            return render_template('cadastro_veiculos.html', perfil=perfil, nome_usuario=nome_usuario)
                
        if request.method == "POST":
            data = request.get_json()
            placa = data.get('placa', "").strip().upper()
            modelo = data.get('modelo', "").strip().title()           
            ano_fabricacao = data.get('ano_fabricacao', "").strip()         
            tipo = data.get('tipo', "").strip().title()
            vagas = data.get('vagas', "").strip()
        
            
            
            ##---------------------------------------Validações---------------------------------------##
            #Nos campos obrigatórios se precisamos informar ao usuário qual campo foi preenchido de forma incorreta.
            #Assim as validações deve ser individualizadas e ao final, caso existam erros, retornar os erros ao usuário.
            #Inicia com um verificador de erros que será uma lista vazia, já que irá armazenar os erros e depois exibir no html
            erros= []
            
            #Verifica se o Placa está preenchido
            if not placa:
                erros.append("O campo 'Placa' é obrigatório.") 
                
            #Verifica se o Modelo está preenchido
            if not modelo:
                erros.append("O campo 'Modelo' é obrigatório.")
            
            #Verifica se o Ano de Fabricação está preenchido
            if not ano_fabricacao:
                erros.append("O campo 'Ano de Fabricação' é obrigatório.") 
            
            #Verifica se o tipo do veículo está preenchido
            if not tipo:
                erros.append("O campo 'Tipo' é obrigatório.")           
           
           #Verifica se o campo vagas foi preenchido
            if not vagas:
                erros.append("O campo 'Vagas' é obrigatório")
          
               
            
            #Verifica se todos os campos foram preenchidos. Se não forem não realiza o cadastro e retorna uma informação ao usuário.
            #Na existencia de erro irá redirecionar para a página cadastro com as informações.            
            if erros:
                return jsonify({"erros": erros}), 400

            #-------------------------------------------------------------------------------------------------------#
            #-------------------------------------Segundo nivel de verificação--------------------------------------#
            #Busca do Banco de dados se há um aluno com o mesmo nome
            cadastro_existente = Veiculos.query.filter_by(placa=placa).first() #realiza a consulta no banco.
            
            
            #Verifica se o nome cadastrado já se encontra no banco de dados, se já constar retornará um aviso ao usuário
            if cadastro_existente:
                return jsonify({"erros": ["Veículo já cadastrado."]}), 409
           
            #Caso não haja cadastro existente, realiza o cadastro
            else:
                novo_veiculo = Veiculos(placa=placa, modelo=modelo, ano_fabricacao=ano_fabricacao,tipo=tipo, vagas=vagas)
                
                db.session.add(novo_veiculo)
                db.session.commit()
                print("comitei aqui")
                #Variaveis para o envio da confirmação
                

                
                return jsonify({"mensagem": "Cadastro realizado!"}), 201
            
    except Exception as e:
           return jsonify({"erro": str(e)}), 500
        
    #Edição do cadastro dos veiculos
@veiculos_bp.route('/lista_veiculos', methods=["GET", "POST"])
@login_required
@cadastro_ativo
@perfis_permitidos(['Admin', 'Motorista'])
def lista_veiculos():
    try:
        perfil = current_user.perfilAcesso
        nome_usuario = current_user.nome
        if request.method == "GET":
            veiculo = Veiculos.query.all()
            return render_template("lista_veiculo_editar.html", perfil=perfil, nome_usuario=nome_usuario, veiculos=veiculo)
    except Exception as e:
           return jsonify({"erro": str(e)}), 500
            
 #   Edição do cadastro dos veiculos           
@veiculos_bp.route('/<int:id>/editar_veiculo', methods=["GET", "PUT"])
@login_required
@cadastro_ativo
@perfis_permitidos(['Admin', 'Motorista'])
def editar_veiculo(id):
    try:
        perfil = current_user.perfilAcesso
        nome_usuario = current_user.nome
        veiculo = Veiculos.query.get(id)
        if not veiculo:
            return jsonify({"erro": "Veiculo não encontrado"}), 404
        if request.method == "GET":
            placa = veiculo.placa
            modelo = veiculo.modelo           
            ano_fabricacao = veiculo.ano_fabricacao
            tipo = veiculo.tipo
            vagas = veiculo.vagas
            return render_template('editar_veiculos.html', placa=placa, modelo=modelo, ano_fabricacao=ano_fabricacao, tipo=tipo, vagas=vagas, perfil=perfil, nome_usuario=nome_usuario, veiculo=veiculo)
                
            
                
        elif request.method == "PUT":
            data = request.get_json()
            placa = data.get('placa', "").strip().upper()
            modelo = data.get('modelo', "").strip().title()           
            ano_fabricacao = data.get('ano_fabricacao', "").strip()         
            tipo = data.get('tipo', "").strip().title()
            vagas = data.get('vagas', "").strip()
            
            
             ##---------------------------------------Validações---------------------------------------##
            #Nos campos obrigatórios se precisamos informar ao usuário qual campo foi preenchido de forma incorreta.
            #Assim as validações deve ser individualizadas e ao final, caso existam erros, retornar os erros ao usuário.
            #Inicia com um verificador de erros que será uma lista vazia, já que irá armazenar os erros e depois exibir no html
            erros= []
            
            #Verifica se o Placa está preenchido
            if not placa:
                erros.append("O campo 'Placa' é obrigatório.") 
                
            #Verifica se o Modelo está preenchido
            if not modelo:
                erros.append("O campo 'Modelo' é obrigatório.")
            
            #Verifica se o Ano de Fabricação está preenchido
            if not ano_fabricacao:
                erros.append("O campo 'Ano de Fabricação' é obrigatório.") 
            
            #Verifica se o tipo do veículo está preenchido
            if not tipo:
                erros.append("O campo 'Tipo' é obrigatório.")           
           
           #Verifica se o campo vagas foi preenchido
            if not vagas:
                erros.append("O campo 'Vagas' é obrigatório")
          
               
            
            #Verifica se todos os campos foram preenchidos. Se não forem não realiza o cadastro e retorna uma informação ao usuário.
            #Na existencia de erro irá redirecionar para a página cadastro com as informações.            
            if erros:
                return jsonify({"erros": erros}), 400

            #-------------------------------------------------------------------------------------------------------#
            
            
           
            #Caso não haja cadastro existente, realiza o cadastro
            else:
                veiculo.placa = placa
                veiculo.modelo = modelo
                veiculo.ano_fabricacao = ano_fabricacao
                veiculo.tipo = tipo
                veiculo.vagas = vagas
                
                db.session.commit()
                print("comitei aqui")
                #Variaveis para o envio da confirmação
                

                
                return jsonify({"mensagem": "Cadastro atualizado!"}), 201
            
    except Exception as e:
           return jsonify({"erro": str(e)}), 500
           
        
#    Rota para deletar Veículo
@veiculos_bp.route('/<int:id>/excluir_veiculo', methods=["DELETE"])
@login_required
@cadastro_ativo
@perfis_permitidos(['Admin'])
def excluir_veiculo(id):
    veiculo = Veiculos.query.get(id)
    if not veiculo:
        return jsonify({"erro": "Veículo não encontrado"}), 404

    try:
        db.session.delete(veiculo)
        db.session.commit()
        return jsonify({"mensagem": "Veículo excluído com sucesso!"}), 200
    except IntegrityError as e:
        # Se houver um erro de integridade (restrição de chave estrangeira, NOT NULL, etc.)
        db.session.rollback() # MUITO IMPORTANTE: Reverter a transação em caso de erro

        # Log do erro para depuração
        print(f"Erro de Integridade ao excluir {veiculo}: {e}")
        
        # Verifica a origem do erro (opcional, mas bom para mensagens específicas)
        # O erro 'NotNullViolation' indica que há registros dependentes.
        # Log do erro para depuração (Mantenha o log para identificar qual tabela causou o erro)
        print(f"Erro de Integridade ao excluir: {e}") 
        
        # Mensagem única e abrangente para todas as violações de integridade (Foreign Key, Not Null, etc.)
        mensagem_erro = "Não foi possível excluir o Veículo. Ele está vinculado a um Motorista na 'Vinculação do Motorista - Transporte' e deve ser desassociado primeiro. Obs. Se ele estiver em alguma rota com alunos é preciso remover essas vinculações antes de excluir o veículo."

        return jsonify({"erro": mensagem_erro}), 409

    except Exception as e:
        # Tratar outros erros inesperados
        db.session.rollback()
        return jsonify({"erro": f"Erro inesperado no servidor: {e}"}), 500