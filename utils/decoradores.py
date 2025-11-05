# Decorador
from functools import wraps

from flask import flash, redirect, url_for, request, jsonify
from flask_login import current_user

#Decorador para verificar se o cadastro do usuário está ativo (confirmado)
def cadastro_ativo(func):
    @wraps(func)
    def ativo(*args, **kwargs):
        if current_user.confirmado == False:
            flash("Por favor, confirme seu e-mail para acessar essa página.", "warning")
            return redirect(url_for("usuarios.validar"))
    

        return func(*args, **kwargs)
    return ativo


#Decorador para verificar se o perfil do usuário está na lista de perfis permitidos
# Ele recebe uma lista de perfis permitidos como argumento
def perfis_permitidos(perfis_permitidos):
    #Aqui definimos o decorador real
    def decorador(func):
        #Aqui definimos o wrapper que envolve a função original
        @wraps(func)
        def wrapper(*args, **kwargs):
            #Verifica se o perfil do usuário atual está na lista de perfis permitidos
            if current_user.perfilAcesso not in perfis_permitidos:
                
                # -------------------------------------------------------------------
                # NOVO: VERIFICAÇÃO SIMPLIFICADA E MAIS ROBUSTA PARA AJAX/API
                
                # Se for um método que tipicamente NÃO renderiza páginas (DELETE, PUT)
                # OU se o cliente explicitamente solicitou JSON
                is_api_call = request.method in ['DELETE', 'PUT', 'PATCH'] or \
                              (request.method == 'POST' and request.is_json) or \
                              request.headers.get('X-Requested-With') == 'XMLHttpRequest' 
                              
                # Na sua rota de exclusão DELETE, a primeira condição (request.method in ['DELETE', ...]) já é True.
                # Para uma rota GET de página, essa condição será False.

                if is_api_call:
                    # Se for uma chamada de API (AJAX), retorna um JSON de erro
                    return jsonify({"erro": "Acesso negado para este perfil. Operação não autorizada."}), 403 # 403 Forbidden
                else:
                    # Se for uma requisição normal (GET de página, POST de formulário), redireciona
                    flash("Acesso negado para este perfil.", "danger")
                    return redirect(url_for("home.home"))
                # -------------------------------------------------------------------

            return func(*args, **kwargs)
        return wrapper
    return decorador