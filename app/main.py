import os
from flasgger import Swagger
from dotenv import load_dotenv

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, jsonify

from db.models import *
from db.extensions import db

load_dotenv()

mysql_host_port = os.getenv("MYSQL_HOST_PORT")
mysql_password=os.getenv("MYSQL_PASSWORD")
mysql_db=os.getenv("MYSQL_DATABASE")
mysql_user=os.getenv("MYSQL_USER")


def create_app():

    """
    Creates and configures the Flask app with:
    - Swagger API docs,
    - MySQL connection via SQLAlchemy,
    - DB migrations support,
    - Registers all application blueprints for auth, AI search, management, wallet,
      profile, products, and subscriptions,
    - Returns the configured Flask app instance.
    """

    app = Flask(__name__)
    swagger = Swagger(app)

    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f"mysql+mysqlconnector://{mysql_user}:{mysql_password}"
        f"@{mysql_host_port}/{mysql_db}"
    )
    db.init_app(app)
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    Migrate(app, db)

    from api.views.auth import auth_bp
    from api.views.ai import ai_search_bp
    from api.views.manage import manage_bp
    from api.views.wallet import wallet_bp
    from api.views.profile import profile_bp
    from api.views.products import product_bp
    from api.views.subscription import subscription_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(manage_bp)
    app.register_blueprint(wallet_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(product_bp)
    app.register_blueprint(ai_search_bp)
    app.register_blueprint(subscription_bp)

    return app


app = create_app()
with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
