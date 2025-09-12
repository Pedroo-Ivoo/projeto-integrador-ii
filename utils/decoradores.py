# Decorador
from functools import wraps

from flask import flash, redirect, url_for
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
                flash("Acesso negado para este perfil.", "danger")
                return redirect(url_for("home.home"))
            return func(*args, **kwargs)
        return wrapper
    return decorador