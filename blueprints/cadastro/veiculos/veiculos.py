from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from config import db
from models import Motoristas, Regioes, Usuarios, Pais, Alunos, Veiculos
from utils import cadastro_ativo, perfis_permitidos, formatar_nome, verifica_email

veiculos_bp = Blueprint('veiculos', __name__)


@veiculos_bp.route('/cadastro_veiculos', methods=['GET', 'POST'])
@login_required
@cadastro_ativo
@perfis_permitidos(['Admin', 'Motoristas'])
def cadastro_veiculos():
    try:
        perfil = current_user.perfilAcesso
        nome_usuario = current_user.nome
        
        if request.method == "GET":
            lista_motoristas = Motoristas.query.all()
            if len(lista_motoristas) >0:
                return render_template('cadastro_veiculos.html', perfil=perfil, nome_usuario=nome_usuario, lista_motoristas=lista_motoristas)
            else:
                return render_template('cadastro_veiculos.html', perfil=perfil, nome_usuario=nome_usuario)
                
        elif request.method == "POST":
            data = request.get_json()
            placa = data.get('placa', "").strip().upper()
            modelo = data.get('modelo', "").strip().title()           
            ano_fabricacao = data.get('ano_fabricacao', "").strip()         
            tipo = data.get('tipo', "").strip().title()
            vagas = data.get('vagas', "").strip()
            id_motorista = data.get('motorista', "").strip()
        
            
            
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
           #Verifica se o campo vagas foi preenchido
            if not id_motorista:
                erros.append("O campo 'Motorista' é obrigatório")
               
            
            #Verifica se todos os campos foram preenchidos. Se não forem não realiza o cadastro e retorna uma informação ao usuário.
            #Na existencia de erro irá redirecionar para a página cadastro com as informações.            
            if erros:
                return jsonify({"erros": erros}), 400

            #-------------------------------------------------------------------------------------------------------#
            #-------------------------------------Segundo nivel de verificação--------------------------------------#
            #Busca do Banco de dados se há um aluno com o mesmo nome
            cadastro_existente = Veiculos.query.filter_by(placa=placa).first() #realiza a consulta no banco.
            
            motorista_cadastrado = Veiculos.query.filter_by(id_motorista =id_motorista).first() #realiza a consulta no banco.
            
            #Verifica se o nome cadastrado já se encontra no banco de dados, se já constar retornará um aviso ao usuário
            if cadastro_existente:
                return jsonify({"erros": ["Veículo já cadastrado."]}), 409
            elif motorista_cadastrado:
                return jsonify({"erros": ["Motorista já vinculado a um veículo."]}), 409
            #Caso não haja cadastro existente, realiza o cadastro
            else:
                novo_veiculo = Veiculos(placa=placa, modelo=modelo, ano_fabricacao=ano_fabricacao,tipo=tipo, vagas=vagas, id_motorista=id_motorista)
                
                db.session.add(novo_veiculo)
                db.session.commit()
                print("comitei aqui")
                #Variaveis para o envio da confirmação
                

                
                return jsonify({"mensagem": "Cadastro realizado!"}), 201
            
    except Exception as e:
           return jsonify({"erro": str(e)}), 500
        