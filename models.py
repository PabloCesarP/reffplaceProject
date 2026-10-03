from datetime import datetime

from extensions import db


class Pedido(db.Model):
    """
    Um "pedido" = uma planilha de cálculo independente, com suas próprias
    premissas (a cotação do yuan muda com frequência, por exemplo).
    """
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)

    # Premissas (equivalentes às células B4:B8 da planilha)
    peso_primario = db.Column(db.Float, nullable=False, default=217)
    peso_secundario = db.Column(db.Float, nullable=False, default=75)
    seguro_pct = db.Column(db.Float, nullable=False, default=0.06)
    taxa_servico_pct = db.Column(db.Float, nullable=False, default=0.03)
    cotacao = db.Column(db.Float, nullable=False, default=1.2)

    produtos = db.relationship(
        "Produto", backref="pedido", cascade="all, delete-orphan", lazy=True
    )


class Produto(db.Model):
    """
    Uma linha da tabela de produtos (colunas B, C, D da planilha).
    Os valores derivados (frete internacional, seguro, subtotal, taxa,
    totais) NÃO são salvos aqui — são recalculados por calculo.py sempre
    que o pedido é exibido, pra nunca ficarem desatualizados.
    """
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey("pedido.id"), nullable=False)
    nome = db.Column(db.String(200), nullable=False)
    preco = db.Column(db.Float, nullable=False, default=0)
    frete_interno = db.Column(db.Float, nullable=False, default=0)
    peso_g = db.Column(db.Float, nullable=False, default=0)
