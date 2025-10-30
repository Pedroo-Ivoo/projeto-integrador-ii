from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import distinct
from flask_login import login_required, current_user
from config import db
from models import Motoristas, Veiculos, AlocacaoViagens, Alunos, AlocacaoAlunos
from utils import cadastro_ativo, perfis_permitidos, formatar_nome, verifica_email
import googlemaps
from config import gmaps, API_KEY
exiberotas_bp = Blueprint('exiberotas', __name__)

@exiberotas_bp.route('/exibicao_rotas', methods=['GET', 'POST'])
@login_required
@cadastro_ativo
def exibicao_rotas():
    try:
        if request.method == 'GET':
            perfil = current_user.perfilAcesso
            nome_usuario = current_user.nome
            # motoristas = Motoristas.query.all()
            motoristas =db.session.query(Motoristas).join(AlocacaoViagens).join(AlocacaoAlunos).distinct(Motoristas.id).order_by(Motoristas.id,Motoristas.nome).all()
            
            return render_template('exibicao_rotas.html', motoristas=motoristas, perfil=perfil, nome_usuario=nome_usuario)
        
        if request.method == 'POST':
            rotas = AlocacaoAlunos.query.filter_by(id_alocacaoViagem=request.json.get('motorista')).all()
            data = request.get_json()
            motorista = data.get('motorista', "").strip()
            print(data)
            print(rotas)
            
            url_destino = url_for('exiberotas.resultado', motorista=motorista)
            # url_destino = url_for('exiberotas.resultado')
            return jsonify({"redirect_url": url_destino}), 200
        


    
    except Exception as e:
        print(f"Erro ao processar a requisição: {e}")
        return jsonify({"erro": str(e)}), 500
    
    
@exiberotas_bp.route('/resultado/<int:motorista>', methods=['GET', 'POST'])
@login_required
@cadastro_ativo
def resultado(motorista):
    try:
        if request.method == 'GET':
            motorista = motorista
            perfil = current_user.perfilAcesso
            nome_usuario = current_user.nome
            # 'rotas' (lista de objetos AlocacaoAlunos) já existe e está correta
            rotas = AlocacaoAlunos.query.filter_by(id_alocacaoViagem=motorista).all()
            
            ESCOLA_COORDENADAS = "-22.176439315824982, -49.96360257116418" # Coordenadas da Escola
            ENDERECOS_ALUNOS = []
            for endereco in rotas:
                endereco_aluno = f'{endereco.aluno.pais.latitude},{endereco.aluno.pais.longitude}'
                ENDERECOS_ALUNOS.append(endereco_aluno)
            print(rotas)
            print(ENDERECOS_ALUNOS)
            
            # A lista de waypoints (paradas)
            waypoints = ENDERECOS_ALUNOS 

            # 1. Monta a requisição para a Directions API
            directions_result = gmaps.directions(
                origin=ESCOLA_COORDENADAS,
                destination=ESCOLA_COORDENADAS,
                waypoints=waypoints,
                optimize_waypoints=True,
                mode="driving" 
            )

            # 2. Processa o resultado
            if not directions_result:
                return jsonify({"erro": "Não foi possível encontrar a rota."}), 404

            # O resultado contém várias 'routes', pegamos a primeira (a otimizada)
            rota_otimizada = directions_result[0]
            
            # Sequência otimizada:
            waypoint_order = rota_otimizada.get('waypoint_order')
            
            # Distância e Duração Total:
            distance_meters = sum(leg['distance']['value'] for leg in rota_otimizada['legs'])
            duration_seconds = sum(leg['duration']['value'] for leg in rota_otimizada['legs'])

            
            # =========================================================================
            #  CRIAÇÃO DA LISTA DE ORDEM DE PARADAS COMPLETA
            # =========================================================================
            
            # Reorganiza a lista de objetos 'rotas' (alunos) usando o índice otimizado
            # 'rotas' é a sua lista original de AlocacaoAlunos
            paradas_otimizadas_objetos = [rotas[i] for i in waypoint_order]

            lista_ordem_final = []

            # Adiciona a escola como ponto de SAÍDA (Partida)
            lista_ordem_final.append({
                "tipo": "Saída da Escola",
                "detalhes": "Partida da escola",
                "coordenadas": ESCOLA_COORDENADAS,
                "numero_parada": 0
            })

            # Adiciona as paradas dos alunos na ordem otimizada
            # O índice 'i' aqui será a numeração sequencial após a escola (1, 2, 3...)
            for i, alocacao in enumerate(paradas_otimizadas_objetos):
                lista_ordem_final.append({
                    "tipo": "Parada do Aluno",
                    "nome_aluno": alocacao.aluno.nome,
                    "sobrenome_aluno": alocacao.aluno.sobrenome,
                    "endereco": f'{alocacao.aluno.pais.rua}, {alocacao.aluno.pais.numero}',
                    "coordenadas": f'{alocacao.aluno.pais.latitude},{alocacao.aluno.pais.longitude}',
                    "numero_parada": i + 1 # Começa em 1 (depois da escola 0)
                })
                
            # Adiciona a escola como ponto de CHEGADA (Retorno)
            lista_ordem_final.append({
                "tipo": "Chegada à Escola",
                "detalhes": "Final da Rota",
                "coordenadas": ESCOLA_COORDENADAS,
                "numero_parada": len(paradas_otimizadas_objetos) + 1
            })

            # 3. Formata a Resposta (Incluindo a nova lista)
            resposta_rota = {
                "origem": ESCOLA_COORDENADAS,
                "destino": ESCOLA_COORDENADAS,
                "paradas_originais": ENDERECOS_ALUNOS,
                "ordem_otimizada_indices": waypoint_order, 
                "distancia_total_km": round(distance_meters / 1000, 2),
                "duracao_total_minutos": round(duration_seconds / 60, 2),
                "polyline_para_desenhar_no_mapa": rota_otimizada['overview_polyline']['points'],
                "rota_otimizada_json": directions_result[0],
                # NOVO CAMPO
                "lista_paradas_completa": lista_ordem_final 
            }

            # 4. Renderiza o Template
            # Todas as variáveis existentes (perfil, nome_usuario, rotas, dados_da_rota, API_KEY)
            # foram mantidas, apenas 'dados_da_rota' ganhou um novo campo.
            return render_template('resultado_rota.html', 
                                   perfil=perfil, 
                                   nome_usuario=nome_usuario, 
                                   rotas=rotas,
                                   dados_da_rota=resposta_rota, 
                                   API_KEY=API_KEY)

    except Exception as e:
        print(f"Erro ao processar a requisição: {e}")
        return jsonify({"erro": str(e)}), 500
    except googlemaps.exceptions.ApiError as e:
        return jsonify({"erro_api": str(e), "mensagem": "Verifique se a sua API Key está correta e se a Directions API está habilitada."}), 500