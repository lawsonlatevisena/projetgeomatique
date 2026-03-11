# -*- coding: utf-8 -*-
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_jwt_extended import JWTManager
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()
jwt = JWTManager()

def create_app():
    """Creer et configurer l'application Flask"""
    # Déterminer le chemin correct pour les templates
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    app = Flask(__name__, template_folder=template_dir)
    
    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key')
    app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key')
    
    # Initialiser extensions
    db.init_app(app)
    login_manager.init_app(app)
    jwt.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    # Configurer le user_loader pour Flask-Login
    from app.models.user import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Enregistrer les routes (Blueprints)
    try:
        from app.routes.auth import auth_bp
        from app.routes.cadastre import cadastre_bp
        from app.routes.litige import litige_bp
        from app.routes.collectivite import collectivite_bp
        from app.routes.admin import admin_bp
        
        app.register_blueprint(auth_bp, url_prefix='/api/auth')
        app.register_blueprint(cadastre_bp, url_prefix='/api/cadastre')
        app.register_blueprint(litige_bp, url_prefix='/api/litige')
        app.register_blueprint(collectivite_bp, url_prefix='/api/collectivite')
        app.register_blueprint(admin_bp, url_prefix='/api/admin')
    except Exception as e:
        print("Warning: Blueprints not loaded: {}".format(e))
    
    return app
