from app import db
from datetime import datetime
from geoalchemy2 import Geometry

class Parcelle(db.Model):
    __tablename__ = 'parcelles'
    
    id = db.Column(db.Integer, primary_key=True)
    numero_parcelle = db.Column(db.String(50), unique=True, nullable=False)
    proprietaire = db.Column(db.String(200))
    superficie = db.Column(db.Float)  # en mètres carrés
    lieu_dit = db.Column(db.String(200))
    arrondissement = db.Column(db.String(100))
    commune = db.Column(db.String(100))
    region = db.Column(db.String(100), default="Maritime")
    numero_titre = db.Column(db.String(50))
    date_titre = db.Column(db.Date)
    statut = db.Column(db.String(50), default="normal")  # normal, litigieuse, bloquee
    etat_juridique = db.Column(db.String(200))  # foncier, domanial, collectif, etc.
    observations = db.Column(db.Text)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    date_modification = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relations
    geometrie = db.relationship('GeometrieParcelle', backref='parcelle', uselist=False, cascade='all, delete-orphan')
    litiges = db.relationship('Litige', backref='parcelle', lazy=True)
    alertes = db.relationship('AlerteLitige', backref='parcelle', lazy=True)
    
    def __repr__(self):
        return f'<Parcelle {self.numero_parcelle}>'

class GeometrieParcelle(db.Model):
    __tablename__ = 'geometrie_parcelles'
    
    id = db.Column(db.Integer, primary_key=True)
    parcelle_id = db.Column(db.Integer, db.ForeignKey('parcelles.id'), nullable=False, unique=True)
    geom = db.Column(Geometry('POLYGON', srid=4326))  # Format GeoJSON WGS84
    centroid = db.Column(Geometry('POINT', srid=4326))
    
    def __repr__(self):
        return f'<GeometrieParcelle {self.parcelle_id}>'
