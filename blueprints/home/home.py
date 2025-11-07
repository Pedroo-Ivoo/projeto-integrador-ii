
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
from models import Motoristas, Pais
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

@home_bp.route("/editar_cadastros")
@login_required
@cadastro_ativo
def editar_cadastros(): 
    perfil = current_user.perfilAcesso
    nome_usuario = current_user.nome
    if current_user.perfilAcesso == 'Motorista':
        motorista = Motoristas.query.filter_by(id_usuario=current_user.id).first()
        if motorista is None:
            # Envia uma mensagem informativa
            flash("Seu cadastro de Motorista ainda não foi preenchido. Por favor, complete o cadastro para as páginas de edição.", "warning")
            # Redireciona para a rota de cadastro (Ajuste a URL se o nome da rota for diferente)
            return redirect(url_for('motoristas.cadastro_motoristas'))
        return render_template("cadastros_editar.html", nome_usuario=nome_usuario, perfil=perfil, motorista=motorista)
    elif current_user.perfilAcesso == 'Pais':
        pai = Pais.query.filter_by(id_usuario=current_user.id).first()
        # Se o cadastro de Pai não existe, redireciona para o cadastro. 
        if pai is None:
            # Envia uma mensagem informativa
            flash("Seu cadastro de Pai/Responsável ainda não foi preenchido. Por favor, complete o cadastro para poder editá-lo.", "warning")
            # Redireciona para a rota de cadastro (Ajuste a URL se o nome da rota for diferente)
            return redirect(url_for('pais.cadastro_pais'))
        return render_template("cadastros_editar.html", nome_usuario=nome_usuario, perfil=perfil, pai=pai)
    else:
        return render_template("cadastros_editar.html", nome_usuario=nome_usuario, perfil=perfil)
        

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

@home_bp.route('/op_rota')
@login_required
@cadastro_ativo
@perfis_permitidos(['Admin', 'Motorista'])
def op_rota():
    perfil = current_user.perfilAcesso
    nome_usuario = current_user.nome
    return render_template('op_rota.html', perfil=perfil, nome_usuario=nome_usuario)
