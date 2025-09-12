
from flask import Blueprint, render_template
from flask_login import current_user, login_required

from utils import cadastro_ativo, exibir_nome


home_bp = Blueprint('home', __name__)

#Rota para a página central da aplicação
@home_bp.route("/home")
@login_required
@cadastro_ativo
def home(): 
    perfil = current_user.perfilAcesso
    print(perfil)
    nome_formatado = exibir_nome(current_user)
    return render_template("home.html", nome_formatado=nome_formatado, perfil=perfil)