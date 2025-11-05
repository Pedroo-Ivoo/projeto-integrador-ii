from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError
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
    
#Edição das relações de alocação de viagens
@rotas_bp.route('/lista_alocaviagens', methods=["GET", "POST"])
@login_required
@cadastro_ativo
@perfis_permitidos(['Admin', 'Motorista'])
def lista_alocaviagens():
    try:
        perfil = current_user.perfilAcesso
        nome_usuario = current_user.nome
        
        if request.method == "GET":
            if current_user.perfilAcesso == "Motorista":
                motorista_logado = Motoristas.query.filter_by(id_usuario=current_user.id).first()
                
                relacoes = AlocacaoViagens.query.filter_by(id_motorista=motorista_logado.id).all()
                veiculos_livres = Veiculos.query.filter(~Veiculos.id.in_(db.session.query(AlocacaoViagens.id_veiculo))).all()
                
                return render_template('lista_alocacaoviagens_editar.html', perfil=perfil, nome_usuario=nome_usuario, relacoes=relacoes, veiculos_livres=veiculos_livres)
            else:
                relacoes = AlocacaoViagens.query.all()
                motoristas_livres = Motoristas.query.filter(~Motoristas.id.in_(db.session.query(AlocacaoViagens.id_motorista))).all()
                veiculos_livres = Veiculos.query.filter(~Veiculos.id.in_(db.session.query(AlocacaoViagens.id_veiculo))).all()

                return render_template('lista_alocacaoviagens_editar.html', perfil=perfil, nome_usuario=nome_usuario, relacoes=relacoes, motoristas_livres=motoristas_livres, veiculos_livres=veiculos_livres)
    except Exception as e:
        print(e)
        return jsonify({"erro": str(e)}), 500
       
            
 # Edição do cadastro dos alunos           
@rotas_bp.route('/<int:id>/editar_alocacaoviagem', methods=["GET", "PUT"])
@login_required
@cadastro_ativo
@perfis_permitidos(['Admin', 'Motorista'])
def editar_alocacaoviagem(id):
    try:
        perfil = current_user.perfilAcesso
        nome_usuario = current_user.nome
        relacoes = AlocacaoViagens.query.get(id)
        veiculos_livres = Veiculos.query.filter(~Veiculos.id.in_(db.session.query(AlocacaoViagens.id_veiculo))).all()
        motoristas_livres = Motoristas.query.filter(~Motoristas.id.in_(db.session.query(AlocacaoViagens.id_motorista))).all()
        if not relacoes:
            return jsonify({"erro": "Relação não encontrado"}), 404
        if request.method == "GET":
            motorista = relacoes.id_motorista
            veiculo = relacoes.id_veiculo
            
            
            return render_template('editar_alocacaoviagem.html', perfil=perfil, nome_usuario=nome_usuario, relacoes=relacoes, motorista=motorista, veiculo=veiculo, veiculos_livres=veiculos_livres, motoristas_livres=motoristas_livres)
  
        elif request.method == "PUT":
            data = request.get_json()
            motorista = data.get('motorista', "").strip()
            veiculo = data.get('transporte', "").strip()   
            
            
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
                relacoes.id_motorista = motorista
                relacoes.id_veiculo = veiculo
                db.session.commit()
                print("comitei aqui")
                #Variaveis para o envio da confirmação
                return jsonify({"mensagem": "Cadastro Atualizado!"}), 201

            
    except Exception as e:
        print(f"Erro ao processar a requisição: {e}")
        return jsonify({"erro": str(e)}), 500
            
           
           
        
#    Rota para deletar Alocacão de Viagem
@rotas_bp.route('/<int:id>/excluir_alocacaoviagem', methods=["DELETE"])
@login_required
@cadastro_ativo
@perfis_permitidos(['Admin'])
def excluir_alocacaoviagem(id):
    relacoes = AlocacaoViagens.query.get(id)
    if not relacoes:
        return jsonify({"erro": "Alocação não encontrado"}), 404
    try:
        db.session.delete(relacoes)
        db.session.commit()
        return jsonify({"mensagem": "Veículo excluído com sucesso!"}), 200
    except IntegrityError as e:
        # Se houver um erro de integridade (restrição de chave estrangeira, NOT NULL, etc.)
        db.session.rollback() # MUITO IMPORTANTE: Reverter a transação em caso de erro

        # Log do erro para depuração
        print(f"Erro de Integridade ao excluir {relacoes}: {e}")
        
        # Verifica a origem do erro (opcional, mas bom para mensagens específicas)
        # O erro 'NotNullViolation' indica que há registros dependentes.
        # Log do erro para depuração (Mantenha o log para identificar qual tabela causou o erro)
        print(f"Erro de Integridade ao excluir: {e}") 
        
        # Mensagem única e abrangente para todas as violações de integridade (Foreign Key, Not Null, etc.)
        mensagem_erro = "Não foi possível excluir a vinculação do motorista com o veículo. Ele está vinculado a uma rota'Criação das rotas' e deve ser desassociado primeiro. Obs. É preciso remover os alunos vinculados a essa rota antes de excluir a alocação."

        return jsonify({"erro": mensagem_erro}), 409

    except Exception as e:
        # Tratar outros erros inesperados
        db.session.rollback()
        return jsonify({"erro": f"Erro inesperado no servidor: {e}"}), 500

#Rota para editar a relação de alunos em uma alocação
@rotas_bp.route('/relacao_editar_rotas', methods=['GET', 'PUT'])
@login_required
@cadastro_ativo
@perfis_permitidos(['Admin', 'Motorista'])
def relacao_editar_rotas():
    try:
        # --- Lógica GET (Exibir dados) ---
        if request.method == "GET":
            # (Seu código GET permanece inalterado, pois a exibição já estava correta)
            perfil = current_user.perfilAcesso
            nome_usuario = current_user.nome
            motorista_logado = Motoristas.query.filter_by(id_usuario=current_user.id).first()

            # Busca todos os alunos JÁ alocados
            todos_alunos = AlocacaoAlunos.query.all()

            if perfil == "Motorista":
                # Filtra apenas as alocações de viagem do motorista logado
                vagas = AlocacaoViagens.query.filter_by(id_motorista=motorista_logado.id).all()
                motoristas = vagas # Usando 'vagas' para a lista de transportes do motorista

            else: # Perfil Admin
                # Busca todas as alocações de viagem para o Admin
                motoristas = AlocacaoViagens.query.all()
                
            
            # Cálculo de vagas para todos os transportes/motoristas listados
            vagas_por_alocacao = { alocacao.id: calcular_vagas_disponiveis(alocacao.id)
                                  for alocacao in motoristas}
            
            # Preparação dos dados para o template (mantido do original)
            alunos_id_lista = [aluno.id_aluno for aluno in todos_alunos]
            transporte_id_lista = [aluno.id_alocacaoViagem for aluno in todos_alunos]
            
            return render_template('editar_relacao_rotas.html', 
                                   perfil=perfil, 
                                   nome_usuario=nome_usuario, 
                                   motoristas=motoristas, 
                                   vagas_por_alocacao=vagas_por_alocacao, 
                                   todos_alunos=todos_alunos, 
                                   alunos=alunos_id_lista, 
                                   transporte=transporte_id_lista)

        # --- Lógica PUT/POST (Atualizar alocação) ---
        # --- Lógica PUT (Atualizar Alocação de Alunos) ---
        elif request.method == "PUT":
            data = request.get_json()
            motorista_id_alocacao = int(data.get('motorista'))  # ID da NOVA Alocação de Viagem
            alunos_selecionados = [int(x) for x in data.get('alunos', [])]  # IDs dos alunos que devem estar na NOVA rota
            
            erros = []

            try:
                # 1. VERIFICAÇÃO INICIAL: Garante que a alocação de destino existe
                alocacao_destino = AlocacaoViagens.query.get(motorista_id_alocacao)
                if not alocacao_destino:
                    erros.append(f"Alocação de Viagem ID {motorista_id_alocacao} não encontrada.")
                    return jsonify({"erros": erros}), 400

                # 2. Processa as alocações em massa
                alunos_ja_alocados_lista = []
                
                # Cria um set de todos os IDs de alunos que já estão alocados em QUALQUER rota
                todos_alocados_anteriormente = AlocacaoAlunos.query.all()
                
                # 3. Itera sobre CADA aluno selecionado para a NOVA rota
                for aluno_id in alunos_selecionados:
                    
                    aluno_obj = Alunos.query.get(aluno_id)
                    if not aluno_obj:
                        erros.append(f"Aluno ID {aluno_id} não encontrado.")
                        continue

                    # Tenta encontrar a alocação ATUAL deste aluno (em qualquer rota)
                    alocacao_atual = AlocacaoAlunos.query.filter_by(id_aluno=aluno_id).first()
                    
                    if alocacao_atual:
                        # O aluno JÁ ESTÁ ALOCADO
                        
                        if alocacao_atual.id_alocacaoViagem == motorista_id_alocacao:
                            # Caso A: Aluno já estava alocado nesta mesma rota. Apenas mantém (não faz nada).
                            alunos_ja_alocados_lista.append(aluno_obj.nome)
                            
                        else:
                            # Caso B: Aluno está mudando de rota.
                            # 1. DELETA a alocação antiga (desvincula da rota anterior)
                            db.session.delete(alocacao_atual)
                            
                            # 2. CRIA uma nova alocação para a rota de destino
                            nova_alocacao = AlocacaoAlunos(id_aluno=aluno_id, id_alocacaoViagem=motorista_id_alocacao)
                            db.session.add(nova_alocacao)

                    else:
                        # Caso C: Aluno não estava alocado (primeira alocação).
                        nova_alocacao = AlocacaoAlunos(id_aluno=aluno_id, id_alocacaoViagem=motorista_id_alocacao)
                        db.session.add(nova_alocacao)
                        
                # 4. Finalização
                if erros:
                    db.session.rollback()
                    return jsonify({"erros": erros}), 400

                db.session.commit()
                
                mensagem = "Alocação(ões) atualizada(s) com sucesso!"
                if alunos_ja_alocados_lista:
                    mensagem += f" (Nota: Alguns alunos já estavam alocados neste transporte.)"
                        
                print("Alocações atualizadas com sucesso!")
                return jsonify({"mensagem": mensagem}), 200
            
            except Exception as e:
                db.session.rollback() # Reverte as alterações em caso de falha
                print(f"Erro ao atualizar alocações no DB: {e}")
                return jsonify({"erro": f"Erro interno ao atualizar: {str(e)}"}), 500

    except Exception as e:
        print(f"Erro ao processar a requisição principal: {e}")
        return jsonify({"erro": str(e)}), 500




# Rota para remover o aluno de uma alocação (desvinculação)
@rotas_bp.route('/<int:id>/excluir_alocacao_aluno', methods=["DELETE"])
@login_required
@cadastro_ativo
@perfis_permitidos(['Admin'])
def excluir_alocacao_aluno(id): # Renomeei a função para ser mais clara
    # O 'id' aqui é o id da linha na tabela AlocacaoAlunos que queremos apagar
    relacao = AlocacaoAlunos.query.get(id)
    
    if not relacao:
        print(f"AlocaçãoAlunos ID {id} não encontrada para exclusão.")
        return jsonify({"erro": "Associação aluno-rota não encontrada."}), 404
        
    try:
        db.session.delete(relacao)
        db.session.commit()
        
        # O aluno agora está "livre" para ser alocado em outra rota ou ter seu cadastro apagado.
        return jsonify({"mensagem": "Aluno desvinculado da rota com sucesso!"}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Erro ao excluir associação aluno-rota no DB: {e}")
        return jsonify({"erro": f"Erro interno ao excluir: {str(e)}"}), 500
    

    db.session.delete(relacoes)
    db.session.commit()
    return jsonify({"mensagem": "Alocação excluída com sucesso!"}), 200