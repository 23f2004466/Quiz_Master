from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os  # For chart upload folder
from models import db, create_admin
from models.user import User  
from controllers.auth import auth_bp
from controllers.admin import admin_bp
from controllers.user import user_bp


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'app123'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mentiquiz.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['CHART_FOLDER'] = os.path.join(app.root_path, 'static', 'charts')
    os.makedirs(app.config['CHART_FOLDER'], exist_ok=True)

    db.init_app(app)

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"  
    # load user for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User,int(user_id))  

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp)

    with app.app_context():
        db.create_all()
        create_admin()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
