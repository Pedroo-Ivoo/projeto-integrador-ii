
from flask import Blueprint, render_template
from flask_login import current_user, login_required

from utils import cadastro_ativo, perfis_permitidos


home_bp = Blueprint('home', __name__)

#Rota para a página central da aplicação
@home_bp.route("/home")
@login_required
@cadastro_ativo
def home(): 
    perfil = current_user.perfilAcesso
    nome_usuario = current_user.nome
    return render_template("home.html", nome_usuario=nome_usuario, perfil=perfil)

@home_bp.route("/cadastros")
@login_required
@cadastro_ativo
def cadastros(): 
    perfil = current_user.perfilAcesso
    nome_usuario = current_user.nome
    return render_template("cadastros.html", nome_usuario=nome_usuario, perfil=perfil)

@home_bp.route("/rotas")
@login_required
@cadastro_ativo
def rotas(): 
    perfil = current_user.perfilAcesso
    nome_usuario = current_user.nome
    return render_template("rotas.html", nome_usuario=nome_usuario, perfil=perfil)

@home_bp.route("/recursoshumanos")
@login_required
@cadastro_ativo
@perfis_permitidos(['Admin', 'Motorista'])
def recursoshumanos(): 
    perfil = current_user.perfilAcesso
    nome_usuario = current_user.nome
    return render_template("recursoshumanos.html", nome_usuario=nome_usuario, perfil=perfil)