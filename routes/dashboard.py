from flask import Blueprint, render_template

from models import Pedido

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def inicio():
    total_pedidos = Pedido.query.count()
    return render_template("index.html", total_pedidos=total_pedidos)
