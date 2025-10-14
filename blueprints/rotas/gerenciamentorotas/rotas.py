from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from config import db
from models import Motoristas, Veiculos, AlocacaoViagens, Alunos, AlocacaoAlunos
from utils import cadastro_ativo, perfis_permitidos, formatar_nome, verifica_email

rotas_bp = Blueprint('rotas', __name__)
#Função para calcular as vagas disponíveis em uma alocação
def calcular_vagas_disponiveis(alocacao_id):
    alocacao = AlocacaoViagens.query.get(alocacao_id)
    veiculo = Veiculos.query.get(alocacao.id_veiculo)
    vagas_totais = veiculo.vagas
    vagas_ocupadas = AlocacaoAlunos.query.filter_by(id_alocacaoViagem=alocacao.id).count()
    return vagas_totais - vagas_ocupadas



@rotas_bp.route('/gerenciamento_rotas', methods=['GET', 'POST'])
@login_required
@cadastro_ativo
@perfis_permitidos(['Admin', 'Motorista'])
def gerenciamento_rotas():
    try:
        if request.method == "GET":
            perfil = current_user.perfilAcesso
            nome_usuario = current_user.nome
            if perfil == "Motorista":
                motoristas = Motoristas.query.filter_by(id_usuario=current_user.id).filter(~Motoristas.id.in_(db.session.query(AlocacaoViagens.id_motorista))).first()
                
                veiculos = Veiculos.query.filter(~Veiculos.id.in_(db.session.query(AlocacaoViagens.id_veiculo))).all() 
                return render_template('gerenciamento_rotas.html', perfil=perfil, nome_usuario=nome_usuario, motoristas=motoristas, veiculos=veiculos)
                
            else:
                motoristas = Motoristas.query.filter(~Motoristas.id.in_(db.session.query(AlocacaoViagens.id_motorista))).all()
                veiculos = Veiculos.query.filter(~Veiculos.id.in_(db.session.query(AlocacaoViagens.id_veiculo))).all()

                return render_template('gerenciamento_rotas.html', perfil=perfil, nome_usuario=nome_usuario, motoristas=motoristas, veiculos=veiculos)
            
                
        if request.method == "POST":
            data = request.get_json()
            motorista = data.get('motorista', "").strip()
            veiculo = data.get('transporte', "").strip()           
            print(data)
            ##---------------------------------------Validações---------------------------------------##
            #Nos campos obrigatórios se precisamos informar ao usuário qual campo foi preenchido de forma incorreta.
            #Assim as validações deve ser individualizadas e ao final, caso existam erros, retornar os erros ao usuário.
            #Inicia com um verificador de erros que será uma lista vazia, já que irá armazenar os erros e depois exibir no html
            erros= []
            
            #Verifica se o motorista está preenchido
            if not motorista:
                erros.append("O campo 'Motorista' é obrigatório.") 
                
            #Verifica se o veiculo está preenchido
            if not veiculo:
                erros.append("O campo 'Veiculo' é obrigatório.")  
            #Verifica se todos os campos foram preenchidos. Se não forem não realiza o cadastro e retorna uma informação ao usuário.
            #Na existencia de erro irá redirecionar para a página cadastro com as informações.            
            if erros:
                return jsonify({"erros": erros}), 400
            
            #Caso não haja cadastro existente, realiza o cadastro
            else:
                # novo_alocacao = AlocacaoViagens(motorista=motorista, veiculo=veiculo)
                novo_alocacao = AlocacaoViagens(id_motorista=motorista, id_veiculo=veiculo)
                db.session.add(novo_alocacao)
                db.session.commit()
                print("comitei aqui")
                #Variaveis para o envio da confirmação
                return jsonify({"mensagem": "Cadastro realizado!"}), 201

            
    except Exception as e:
        print(f"Erro ao processar a requisição: {e}")
        return jsonify({"erro": str(e)}), 500
    
    
@rotas_bp.route('/relacao_rotas', methods=['GET', 'POST'])
@login_required
@cadastro_ativo
@perfis_permitidos(['Admin', 'Motorista'])
def relacao_rotas():
    try:
        if request.method == "GET":
            perfil = current_user.perfilAcesso
            nome_usuario = current_user.nome
            motorista_logado = current_user.motoristas[0].id
            


            if perfil == "Motorista":
                vagas = AlocacaoViagens.query.all()
                motoristas = AlocacaoViagens.query.filter_by(id_motorista=motorista_logado).all()
                alunos = Alunos.query.filter(~Alunos.id.in_(db.session.query(AlocacaoAlunos.id_aluno)
                )).all()
                
                vagas_por_alocacao = { alocacao.id: calcular_vagas_disponiveis(alocacao.id)
                for alocacao in vagas}
                
                return render_template('relacao_rotas.html', perfil=perfil, nome_usuario=nome_usuario, motoristas=motoristas, alunos=alunos, vagas_por_alocacao=vagas_por_alocacao)
                
                
            else:
                motoristas = AlocacaoViagens.query.all()
                alunos = Alunos.query.filter(~Alunos.id.in_(db.session.query(AlocacaoAlunos.id_aluno)
                )
            ).all()
                vagas_por_alocacao = { alocacao.id: calcular_vagas_disponiveis(alocacao.id)
                for alocacao in motoristas}
                
                
                return render_template('relacao_rotas.html', perfil=perfil, nome_usuario=nome_usuario, motoristas=motoristas, alunos=alunos, vagas_por_alocacao=vagas_por_alocacao)
        
        elif request.method == "POST":
            data = request.get_json()
            motorista = data.get('motorista', "").strip()
            alunos_selecionados = data.get('alunos', [])
            vagas_disponiveis = calcular_vagas_disponiveis(motorista)
            
            print(data)           
            ##---------------------------------------Validações---------------------------------------##
            #Nos campos obrigatórios se precisamos informar ao usuário qual campo foi preenchido de forma incorreta.
            #Assim as validações deve ser individualizadas e ao final, caso existam erros, retornar os erros ao usuário.
            #Inicia com um verificador de erros que será uma lista vazia, já que irá armazenar os erros e depois exibir no html
            erros= []
            
            #Verifica se o motorista está preenchido
            if not motorista:
                erros.append("O campo 'Motorista' é obrigatório.") 
                
            #Verifica se o veiculo está preenchido
            if not alunos_selecionados:
                erros.append("É preciso selecionar ao menos um aluno.")  
            #Verifica se todos os campos foram preenchidos. Se não forem não realiza o cadastro e retorna uma informação ao usuário.
            #Na existencia de erro irá redirecionar para a página cadastro com as informações.            
            if erros:
                return jsonify({"erros": erros}), 400
            
            #Verifica se o número de alunos selecionados não excede as vagas disponíveis
            if len(alunos_selecionados) > vagas_disponiveis:
                return jsonify({"erros": ["Número de alunos excede as vagas disponíveis."]}), 400

            
            #Caso não haja cadastro existente, realiza o cadastro
            else:
                for aluno_id in alunos_selecionados:
                    novo_alocacao = AlocacaoAlunos(id_alocacaoViagem=motorista, id_aluno=aluno_id)
                    db.session.add(novo_alocacao)
                db.session.commit()
                print("comitei aqui")
                #Variaveis para o envio da confirmação
                return jsonify({"mensagem": "Cadastro realizado!"}), 201
 
    except Exception as e:
        print(f"Erro ao processar a requisição: {e}")
        return jsonify({"erro": str(e)}), 500