from app import db
from datetime import datetime
from enum import Enum

class StatutLitige(Enum):
    OUVERT = "ouvert"
    EN_COURS_DE_TRAITEMENT = "en_cours"
    RESOLU = "resolu"
    SUSPENDU = "suspendu"
    REJET = "rejet"

class Litige(db.Model):
    __tablename__ = 'litiges'
    
    id = db.Column(db.Integer, primary_key=True)
    numero_dossier = db.Column(db.String(50), unique=True, nullable=False)
    parcelle_id = db.Column(db.Integer, db.ForeignKey('parcelles.id'), nullable=False)
    type_litige = db.Column(db.String(100))  # double vente, conflit limite, etc.
    description = db.Column(db.Text, nullable=False)
    statut = db.Column(db.String(50), default=StatutLitige.OUVERT.value)
    date_enregistrement = db.Column(db.DateTime, default=datetime.utcnow)
    date_resolution = db.Column(db.DateTime)
    demandeur = db.Column(db.String(200))
    defendeur = db.Column(db.String(200))
    tribunal_competent = db.Column(db.String(200))
    reference_jugement = db.Column(db.String(100))
    
    # Relations
    dossier = db.relationship('DossierLitige', backref='litige', uselist=False, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Litige {self.numero_dossier}>'

class DossierLitige(db.Model):
    __tablename__ = 'dossiers_litige'
    
    id = db.Column(db.Integer, primary_key=True)
    litige_id = db.Column(db.Integer, db.ForeignKey('litiges.id'), nullable=False, unique=True)
    agent_judiciaire_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    contenu = db.Column(db.Text)
    pieces_jointes = db.Column(db.JSON, default=[])  # Chemins des fichiers
    date_ouverture = db.Column(db.DateTime, default=datetime.utcnow)
    date_fermeture = db.Column(db.DateTime)
    
    # Relations
    agent_judiciaire = db.relationship('User', backref='dossiers_litige')
    
    def __repr__(self):
        return f'<DossierLitige {self.id}>'

class AlerteLitige(db.Model):
    __tablename__ = 'alertes_litige'
    
    id = db.Column(db.Integer, primary_key=True)
    parcelle_id = db.Column(db.Integer, db.ForeignKey('parcelles.id'), nullable=False)
    litige_id = db.Column(db.Integer, db.ForeignKey('litiges.id'), nullable=False)
    type_alerte = db.Column(db.String(100))  # blocage_operation, nouvelle_action, etc.
    message = db.Column(db.Text)
    priorite = db.Column(db.String(20), default="normal")  # haute, normale, basse
    active = db.Column(db.Boolean, default=True)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_resolution = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<AlerteLitige {self.id}>'
