import os

from flask import Flask

from config import Config
from extensions import db
from routes.dashboard import dashboard_bp
from routes.pedidos import pedidos_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    os.makedirs(os.path.join(app.root_path, "instance"), exist_ok=True)

    db.init_app(app)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(pedidos_bp)

    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
