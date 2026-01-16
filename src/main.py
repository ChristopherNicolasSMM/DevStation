"""
DevStation - Sistema de Gerenciamento de Dados com Auditoria.
"""

from __future__ import annotations

import os
from pathlib import Path

import click
from dotenv import load_dotenv
from flask import Flask, url_for
from flask.cli import with_appcontext
from flask_cors import CORS
from flask_login import LoginManager

from logs.setup_logging import configure_logging

# Carregar variáveis de ambiente
env_file = os.getenv("ENV_FILE")
if env_file:
    load_dotenv(env_file)
else:
    env_path = Path(".env")
    if not env_path.exists():
        env_path = Path("src") / ".env"
    load_dotenv(env_path)


def create_app():
    """Factory function para criar a aplicação Flask."""
    app = Flask(__name__, template_folder="templates", static_folder="static")

    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    app.config["DEBUG"] = os.getenv("DEBUG", "True").lower() == "true"
    app.config["UPLOAD_FOLDER"] = os.getenv("UPLOAD_FOLDER", "uploads")
    app.config["MAX_CONTENT_LENGTH"] = int(os.getenv("MAX_CONTENT_LENGTH", 16777216))
    app.config["FLASK_ENV"] = os.getenv("FLASK_ENV", "DEV")

    configure_logging(app)

    from db.database import init_db
    from utils.dev_setup import ensure_dev_admin

    init_db(app)
    
    # Garantir admin em desenvolvimento
    with app.app_context():
        ensure_dev_admin()

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Por favor, faça login para acessar esta página."
    login_manager.login_message_category = "info"

    @login_manager.user_loader
    def load_user(user_id):
        from model.user import User
        from db.database import db

        return db.session.get(User, int(user_id))

    CORS(app)
    
    # Registrar blueprints core
    register_core_blueprints(app)
    
    # Registrar context processors
    register_context_processors(app)
    
    # Registrar comandos CLI
    register_cli_commands(app)

    return app


def register_core_blueprints(app):
    """Registra os blueprints core."""
    try:
        from controller.auth import auth_bp
        from controller.web import web_bp
        from controller.admin import admin_bp
        from controller.crud import crud_bp
        #from controller.import import import_bp
        from api.routes.crud_routes import crud_api_bp
        from api.routes.export_routes import export_api_bp

        app.register_blueprint(web_bp)
        app.register_blueprint(auth_bp, url_prefix="/auth")
        app.register_blueprint(admin_bp, url_prefix="/admin")
        app.register_blueprint(crud_bp, url_prefix="/crud")
        #app.register_blueprint(import_bp, url_prefix="/import")
        app.register_blueprint(crud_api_bp, url_prefix="/api")
        app.register_blueprint(export_api_bp, url_prefix="/api")

        app.logger.info("Blueprints core registrados com sucesso.")
    except Exception as exc:
        app.logger.exception("Erro ao registrar blueprints core: %s", exc)
        raise


def register_context_processors(app):
    """Registra context processors."""

    @app.context_processor
    def inject_user():
        """Injeta informações do usuário atual."""
        from flask_login import current_user
        return {"current_user": current_user}


def register_cli_commands(app):
    """Registra comandos personalizados via Flask CLI."""

    @app.cli.command("init-admin")
    @click.option("--username", default="admin", show_default=True)
    @click.option("--email", default="admin@devstation.com", show_default=True)
    @click.option("--password", default="admin123", show_default=True)
    @with_appcontext
    def init_admin(username, email, password):
        from db.database import db
        from model.user import User, UserGroup

        # Inicializar grupos
        User.initialize_default_groups()
        
        admin = User.query.filter_by(username=username).first()
        if admin:
            click.echo(f"Usuário {username} já existe.")
            return

        admin_group = UserGroup.query.filter_by(name="Administrador").first()
        admin = User(
            username=username,
            email=email,
            is_admin=True,
            is_active=True,
            group_id=admin_group.id if admin_group else None
        )
        admin.set_password(password)
        db.session.add(admin)
        db.session.commit()
        click.echo(f"Usuário {username} criado com sucesso.")

    @app.cli.command("test-db")
    @with_appcontext
    def test_db():
        from db.database import test_connection

        if test_connection():
            click.echo("Conexão com o banco OK.")
        else:
            click.echo("Falha ao conectar com o banco.", err=True)


app = create_app()

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 5000))
    debug = os.getenv("DEBUG", "True").lower() == "true"

    app.logger.info("Iniciando DevStation em http://%s:%s (debug=%s)", host, port, debug)
    app.run(host=host, port=port, debug=debug)
