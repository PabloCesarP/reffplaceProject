from flask import Blueprint, flash, redirect, render_template, request, url_for

from calculo import calcular_pedido
from extensions import db
from models import Pedido, Produto

pedidos_bp = Blueprint("pedidos", __name__, url_prefix="/pedidos")


def _float(form, campo, padrao=0.0):
    valor = form.get(campo, "").strip().replace(",", ".")
    return float(valor) if valor else padrao


@pedidos_bp.route("/")
def historico():
    pedidos = Pedido.query.order_by(Pedido.data_criacao.desc()).all()
    return render_template("pedidos/historico.html", pedidos=pedidos)


@pedidos_bp.route("/novo", methods=["GET", "POST"])
def novo():
    if request.method == "POST":
        pedido = Pedido(
            nome=request.form["nome"],
            peso_primario=_float(request.form, "peso_primario", 217),
            peso_secundario=_float(request.form, "peso_secundario", 75),
            seguro_pct=_float(request.form, "seguro_pct", 0.06),
            taxa_servico_pct=_float(request.form, "taxa_servico_pct", 0.03),
            cotacao=_float(request.form, "cotacao", 1.2),
        )
        db.session.add(pedido)
        db.session.commit()
        flash(f'Pedido "{pedido.nome}" criado.')
        return redirect(url_for("pedidos.detalhe", pedido_id=pedido.id))
    return render_template("pedidos/novo.html")


@pedidos_bp.route("/<int:pedido_id>")
def detalhe(pedido_id):
    pedido = Pedido.query.get_or_404(pedido_id)
    linhas, totais = calcular_pedido(pedido)
    return render_template(
        "pedidos/detalhe.html", pedido=pedido, linhas=linhas, totais=totais
    )


@pedidos_bp.route("/<int:pedido_id>/produto", methods=["POST"])
def add_produto(pedido_id):
    pedido = Pedido.query.get_or_404(pedido_id)
    produto = Produto(
        pedido_id=pedido.id,
        nome=request.form["nome"],
        preco=_float(request.form, "preco", 0),
        frete_interno=_float(request.form, "frete_interno", 0),
        peso_g=_float(request.form, "peso_g", 0),
    )
    db.session.add(produto)
    db.session.commit()
    return redirect(url_for("pedidos.detalhe", pedido_id=pedido.id))


@pedidos_bp.route("/<int:pedido_id>/produto/<int:produto_id>/excluir", methods=["POST"])
def excluir_produto(pedido_id, produto_id):
    produto = Produto.query.get_or_404(produto_id)
    db.session.delete(produto)
    db.session.commit()
    return redirect(url_for("pedidos.detalhe", pedido_id=pedido_id))


@pedidos_bp.route("/<int:pedido_id>/excluir", methods=["POST"])
def excluir_pedido(pedido_id):
    pedido = Pedido.query.get_or_404(pedido_id)
    db.session.delete(pedido)
    db.session.commit()
    flash("Pedido excluído.")
    return redirect(url_for("pedidos.historico"))
