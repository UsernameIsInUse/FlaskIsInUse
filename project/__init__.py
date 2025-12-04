from flask import Flask
from config import Config
from project.extensions import flashy, ipban, csrf, db, migrate, admin, login, squeeze, toolbar, authorize, mail, api
import flask_noai

def create_app(config_class=Config):
  app = Flask(__name__)
  app.config.from_object(config_class)
  
  # Init extensions
  flask_noai.noai(app)
  squeeze.init_app(app)
  ipban.init_app(app)
  csrf.init_app(app)
  db.init_app(app)
  migrate.init_app(app, db)
  admin.init_app(app)
  login.init_app(app)
  flashy.init_app(app)
  toolbar.init_app(app)
  authorize.init_app(app)
  mail.init_app(app)
  api.init_app(app)
  
  # Additional configurations
  ipban.load_nuisances()
  db.session.expire_on_commit = False
  login.login_view = 'login'
  login.session_protection = "basic"
  login.login_view = "views.login"
  
  # Register blueprints
  from project.views import bp as views_bp
  app.register_blueprint(views_bp)
  
  from project.admin import bp as admin_bp
  app.register_blueprint(admin_bp)
  
  from project.apis.v1 import bps as api_bps
  for api_bp in api_bps:
    api.register_blueprint(api_bp)
  
  # Inject common variables
  @app.context_processor
  def inject_common_vars():
    """Injects common variables into the template context."""
    return dict(
      version=app.config['APP_VERSION'],
      app_name=app.config['APP_NAME'],
      font_awesome=app.config['FA'],
      typekit=app.config['TYPEKIT']
    )
  
  return app

