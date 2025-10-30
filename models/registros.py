from datetime import datetime, timezone
from config import db
from models import Funcionario

class RegistroPonto(db.Model):
    __tablename__ = "registros_ponto"

    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(10), nullable=False)  # "entrada" ou "saida"
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    funcionario_id = db.Column(db.Integer, db.ForeignKey("funcionarios.id"), nullable=False)
    funcionario = db.relationship("Funcionario", backref="registros_ponto")