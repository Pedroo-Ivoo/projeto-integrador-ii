from config import db

class Regioes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    regiao = db.Column(db.String(50), nullable=False, unique=True)
