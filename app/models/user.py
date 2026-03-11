from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from enum import Enum
from datetime import datetime

class RoleEnum(Enum):
    ADMIN = "admin"
    AGENT_CADASTRE = "agent_cadastre"
    AGENT_JUDICIAIRE = "agent_judiciaire"
    COLLECTIVITE = "collectivite"

class Role(db.Model):
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(255))
    permissions = db.Column(db.JSON, default={})
    
    users = db.relationship('User', backref='role', lazy=True)
    
    def __repr__(self):
        return f'<Role {self.nom}>'

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    mot_de_passe = db.Column(db.String(255), nullable=False)
    telephone = db.Column(db.String(20))
    institution = db.Column(db.String(200))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    actif = db.Column(db.Boolean, default=True)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_modification = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_password(self, password):
        self.mot_de_passe = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.mot_de_passe, password)
    
    def __repr__(self):
        return f'<User {self.email}>'
