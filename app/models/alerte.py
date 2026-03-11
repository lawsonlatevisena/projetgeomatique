from app import db
from datetime import datetime

class Alerte(db.Model):
    __tablename__ = 'alertes'
    
    id = db.Column(db.Integer, primary_key=True)
    titre = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text)
    type_alerte = db.Column(db.String(100))  # risque_foncier, conflit_limite, etc.
    priorite = db.Column(db.String(20), default="normal")
    region = db.Column(db.String(100))
    commune = db.Column(db.String(100))
    active = db.Column(db.Boolean, default=True)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_resolution = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<Alerte {self.id}>'
