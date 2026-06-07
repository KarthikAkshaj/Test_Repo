from flask import Flask
from .config import Config
from .utils.db import db


def create_app(config_class: type = Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    from .routes.auth import auth_bp
    from .routes.tasks import tasks_bp
    from .routes.projects import projects_bp

    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(tasks_bp, url_prefix='/api/v1/tasks')
    app.register_blueprint(projects_bp, url_prefix='/api/v1/projects')

    return app
