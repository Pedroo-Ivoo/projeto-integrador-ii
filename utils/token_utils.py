from flask import url_for, render_template
from itsdangerous import URLSafeTimedSerializer as Serializer
import os
from utils import enviar_email
#--------------------------------------------------------------------------------------------------------#
#Funções para geração e envio de token para confirmação de cadastro e recuperação de senha#

#Função que gera um token seguro para a confirmação de cadastro ou refazer a senha

def gerador_serializer():
    chave = os.getenv("CHAVESEGURA")
    if not chave:
        raise ValueError("CHAVESEGURA não definida! Verifique o arquivo .env ou variáveis de ambiente.")
    return Serializer(chave)


def gerador_token(email, salt):
    s = gerador_serializer()
    token = s.dumps(email, salt )
    return token

def enviar_confirmacao(email, salt, pagina, nome_funcao, assunto):
    token = gerador_token(email, salt)
    confirm_url = url_for(nome_funcao, token=token, _external=True)
    html = render_template(pagina, confirm_url=confirm_url)
    # Aqui você chama sua função de envio de e-mail
    enviar_email(email, html, assunto)