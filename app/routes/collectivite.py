from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.parcelle import Parcelle
from app.models.alerte import Alerte
from sqlalchemy import and_

collectivite_bp = Blueprint('collectivite', __name__)

@collectivite_bp.route('/carte-fonciere', methods=['GET'])
@jwt_required()
def consulter_carte_fonciere():
    """
    Consulter la carte foncière (collectivité territoriale)
    Retourne les parcelles avec leurs données SIG
    """
    region = request.args.get('region')
    commune = request.args.get('commune')
    
    query = Parcelle.query
    
    if region:
        query = query.filter_by(region=region)
    if commune:
        query = query.filter_by(commune=commune)
    
    parcelles = query.all()
    
    features = []
    for parcelle in parcelles:
        feature = {
            'type': 'Feature',
            'id': parcelle.id,
            'properties': {
                'numero_parcelle': parcelle.numero_parcelle,
                'proprietaire': parcelle.proprietaire,
                'superficie': parcelle.superficie,
                'commune': parcelle.commune,
                'region': parcelle.region,
                'statut': parcelle.statut,
                'etat_juridique': parcelle.etat_juridique,
                'a_risque': parcelle.statut == 'litigieuse'
            }
        }
        features.append(feature)
    
    return jsonify({
        'type': 'FeatureCollection',
        'count': len(features),
        'features': features
    }), 200

@collectivite_bp.route('/parcelles-a-risque', methods=['GET'])
@jwt_required()
def consulter_parcelles_risque():
    """
    Consulter les parcelles à risque (litiges, contenieux)
    """
    region = request.args.get('region')
    commune = request.args.get('commune')
    
    query = Parcelle.query.filter(Parcelle.statut.in_(['litigieuse', 'bloquee']))
    
    if region:
        query = query.filter_by(region=region)
    if commune:
        query = query.filter_by(commune=commune)
    
    parcelles = query.all()
    
    return jsonify({
        'count': len(parcelles),
        'parcelles': [{
            'id': p.id,
            'numero_parcelle': p.numero_parcelle,
            'proprietaire': p.proprietaire,
            'commune': p.commune,
            'region': p.region,
            'statut': p.statut,
            'observations': p.observations
        } for p in parcelles]
    }), 200

@collectivite_bp.route('/alertes-actives', methods=['GET'])
@jwt_required()
def consulter_alertes_actives():
    """
    Consulter les alertes actives (région, commune)
    """
    region = request.args.get('region')
    commune = request.args.get('commune')
    
    query = Alerte.query.filter_by(active=True)
    
    if region:
        query = query.filter_by(region=region)
    if commune:
        query = query.filter_by(commune=commune)
    
    alertes = query.all()
    
    return jsonify({
        'count': len(alertes),
        'alertes': [{
            'id': a.id,
            'titre': a.titre,
            'message': a.message,
            'type_alerte': a.type_alerte,
            'priorite': a.priorite,
            'region': a.region,
            'commune': a.commune,
            'date_creation': a.date_creation.isoformat()
        } for a in alertes]
    }), 200

@collectivite_bp.route('/statistiques', methods=['GET'])
@jwt_required()
def consulter_statistiques():
    """
    Consulter les statistiques foncières par région/commune
    """
    region = request.args.get('region', 'Maritime')
    
    parcelles_total = Parcelle.query.filter_by(region=region).count()
    parcelles_litigieuses = Parcelle.query.filter(
        and_(Parcelle.region == region, Parcelle.statut == 'litigieuse')
    ).count()
    superficie_total = db.session.query(
        db.func.sum(Parcelle.superficie)
    ).filter_by(region=region).scalar() or 0
    
    return jsonify({
        'region': region,
        'parcelles_total': parcelles_total,
        'parcelles_litigieuses': parcelles_litigieuses,
        'pourcentage_litige': round((parcelles_litigieuses / parcelles_total * 100) if parcelles_total > 0 else 0, 2),
        'superficie_total_ha': round(superficie_total / 10000, 2)
    }), 200
