import os
from flask import Flask
from config import config
from app.extensions import db, migrate, login_manager

def create_app(config_name=None):
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')

    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from app.models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from app.routes.public    import public_bp
    from app.routes.auth      import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.meetings  import meetings_bp
    from app.routes.members   import members_bp
    from app.routes.actions   import actions_bp
    from app.routes.admin     import admin_bp

    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(meetings_bp)
    app.register_blueprint(members_bp)
    app.register_blueprint(actions_bp)
    app.register_blueprint(admin_bp)

    return app
