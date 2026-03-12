from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.parcelle import Parcelle, GeometrieParcelle
from app.models.litige import Litige, AlerteLitige
from sqlalchemy import func

cadastre_bp = Blueprint('cadastre', __name__)

@cadastre_bp.route('/authenticate', methods=['POST'])
@jwt_required()
def authenticate():
    """
    Vérifier l'authentification (agent du cadastre)
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or user.role.nom != 'agent_cadastre':
        return jsonify({'message': 'Accès refusé'}), 403
    
    return jsonify({'message': 'Authentifié'}), 200

@cadastre_bp.route('/carte', methods=['GET'])
@jwt_required()
def consulter_carte():
    """
    Consulter la carte cadastrale avec GeoJSON
    """
    parcelles = Parcelle.query.all()
    
    features = []
    for parcelle in parcelles:
        feature = {
            'type': 'Feature',
            'id': parcelle.id,
            'properties': {
                'numero': parcelle.numero_parcelle,
                'proprietaire': parcelle.proprietaire,
                'statut': parcelle.statut,
                'etat_juridique': parcelle.etat_juridique,
                'alerte': parcelle.statut == 'litigieuse'
            },
            'geometry': {
                'type': 'Polygon',
                'coordinates': []  # À remplir avec les coordonnées PostGIS
            }
        }
        features.append(feature)
    
    return jsonify({
        'type': 'FeatureCollection',
        'features': features
    }), 200

@cadastre_bp.route('/parcelle/<int:parcelle_id>', methods=['GET'])
@jwt_required()
def consulter_parcelle(parcelle_id):
    """
    Consulter une parcelle spécifique
    """
    parcelle = Parcelle.query.get(parcelle_id)
    
    if not parcelle:
        return jsonify({'message': 'Parcelle non trouvée'}), 404
    
    litiges = Litige.query.filter_by(parcelle_id=parcelle_id).all()
    alertes = AlerteLitige.query.filter_by(parcelle_id=parcelle_id, active=True).all()
    
    return jsonify({
        'id': parcelle.id,
        'numero_parcelle': parcelle.numero_parcelle,
        'proprietaire': parcelle.proprietaire,
        'superficie': parcelle.superficie,
        'lieu_dit': parcelle.lieu_dit,
        'commune': parcelle.commune,
        'statut': parcelle.statut,
        'etat_juridique': parcelle.etat_juridique,
        'litiges_count': len(litiges),
        'litiges': [{'id': l.id, 'numero_dossier': l.numero_dossier} for l in litiges],
        'alertes_count': len(alertes)
    }), 200

@cadastre_bp.route('/rechercher', methods=['GET'])
@jwt_required()
def rechercher_parcelle():
    """
    Rechercher une parcelle par numéro ou propriétaire
    """
    numero = request.args.get('numero')
    proprietaire = request.args.get('proprietaire')
    commune = request.args.get('commune')
    
    query = Parcelle.query
    
    if numero:
        query = query.filter(Parcelle.numero_parcelle.ilike(f'%{numero}%'))
    if proprietaire:
        query = query.filter(Parcelle.proprietaire.ilike(f'%{proprietaire}%'))
    if commune:
        query = query.filter(Parcelle.commune.ilike(f'%{commune}%'))
    
    parcelles = query.all()
    
    return jsonify({
        'count': len(parcelles),
        'parcelles': [{
            'id': p.id,
            'numero_parcelle': p.numero_parcelle,
            'proprietaire': p.proprietaire,
            'commune': p.commune,
            'statut': p.statut
        } for p in parcelles]
    }), 200

@cadastre_bp.route('/operation', methods=['POST'])
@jwt_required()
def enregistrer_operation():
    """
    Enregistrer une opération cadastrale
    (avec vérification automatique des bloques)
    """
    user_id = get_jwt_identity()
    data = request.get_json()
    
    if not data.get('parcelle_id'):
        return jsonify({'message': 'parcelle_id requis'}), 400
    
    parcelle = Parcelle.query.get(data['parcelle_id'])
    if not parcelle:
        return jsonify({'message': 'Parcelle non trouvée'}), 404
    
    # Vérifier si la parcelle est bloquée (alerte active)
    alerte_active = AlerteLitige.query.filter_by(
        parcelle_id=parcelle.id, 
        active=True
    ).first()
    
    if alerte_active:
        return jsonify({
            'message': 'Opération bloquée',
            'raison': 'Une alerte de litige active existe pour cette parcelle',
            'alerte_id': alerte_active.id
        }), 409
    
    # Enregistrer l'opération
    # (À implémenter selon les besoins spécifiques)
    
    return jsonify({
        'message': 'Opération enregistrée avec succès',
        'parcelle_id': parcelle.id
    }), 201

@cadastre_bp.route('/parcelles', methods=['GET'])
@jwt_required()
def lister_parcelles():
    """
    Lister toutes les parcelles avec filtres optionnels
    ?numero=... &proprietaire=... &commune=... &statut=...
    """
    numero = request.args.get('numero')
    proprietaire = request.args.get('proprietaire')
    commune = request.args.get('commune')
    statut = request.args.get('statut')
    search = request.args.get('search')  # recherche générique

    query = Parcelle.query
    if search:
        query = query.filter(
            Parcelle.numero_parcelle.ilike(f'%{search}%') |
            Parcelle.proprietaire.ilike(f'%{search}%') |
            Parcelle.commune.ilike(f'%{search}%')
        )
    if numero:
        query = query.filter(Parcelle.numero_parcelle.ilike(f'%{numero}%'))
    if proprietaire:
        query = query.filter(Parcelle.proprietaire.ilike(f'%{proprietaire}%'))
    if commune:
        query = query.filter(Parcelle.commune.ilike(f'%{commune}%'))
    if statut:
        query = query.filter(Parcelle.statut == statut)

    parcelles = query.all()

    return jsonify({
        'count': len(parcelles),
        'parcelles': [{
            'id': p.id,
            'numero_parcelle': p.numero_parcelle,
            'proprietaire': p.proprietaire,
            'superficie': p.superficie,
            'lieu_dit': p.lieu_dit,
            'commune': p.commune,
            'region': p.region,
            'statut': p.statut,
            'etat_juridique': p.etat_juridique,
            'nombre_litiges': len(p.litiges)
        } for p in parcelles]
    }), 200


@cadastre_bp.route('/bloquer-contentieux', methods=['POST'])
@jwt_required()
def bloquer_contentieux():
    """
    Bloquer toutes les opérations d'immatriculation liées à un dossier litigieux.
    Place la parcelle et ses litiges actifs au contentieux (statut 'bloquee').
    Réservé à l'agent du cadastre.
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user or user.role.nom != 'agent_cadastre':
        return jsonify({'message': 'Accès refusé'}), 403

    data = request.get_json()

    # Accepter parcelle_id (int) ou numero_parcelle (str)
    pid = data.get('parcelle_id')
    parcelle = None
    if pid:
        if str(pid).isdigit():
            parcelle = Parcelle.query.get(int(pid))
        else:
            parcelle = Parcelle.query.filter_by(numero_parcelle=str(pid)).first()

    if not parcelle:
        return jsonify({'message': 'Parcelle non trouvée'}), 404

    if parcelle.statut == 'bloquee':
        return jsonify({'message': f'La parcelle {parcelle.numero_parcelle} est déjà placée au contentieux'}), 409

    motif = data.get('motif', 'Blocage suite à dossier litigieux')

    # 1. Bloquer la parcelle
    parcelle.statut = 'bloquee'
    parcelle.etat_juridique = 'contentieux'
    if data.get('observations'):
        parcelle.observations = data['observations']

    # 2. Passer tous les litiges actifs en cours de traitement
    litiges_bloques = []
    litiges_actifs = Litige.query.filter(
        Litige.parcelle_id == parcelle.id,
        Litige.statut.in_(['ouvert'])
    ).all()

    for litige in litiges_actifs:
        litige.statut = 'en_cours'
        litiges_bloques.append({'id': litige.id, 'numero_dossier': litige.numero_dossier})

    # 3. Créer une alerte de blocage
    alerte = AlerteLitige(
        parcelle_id=parcelle.id,
        litige_id=litiges_actifs[0].id if litiges_actifs else (
            Litige.query.filter_by(parcelle_id=parcelle.id)
                        .order_by(Litige.date_enregistrement.desc()).first().id
            if Litige.query.filter_by(parcelle_id=parcelle.id).count() > 0 else None
        ),
        type_alerte='blocage_operation',
        message=f'Parcelle {parcelle.numero_parcelle} placée au contentieux. Motif : {motif}',
        priorite='haute',
        active=True
    )

    if alerte.litige_id is None:
        # Pas de litige existant : on ne peut pas créer l'alerte (FK obligatoire)
        db.session.add(parcelle)
        db.session.commit()
        return jsonify({
            'message': f'Parcelle {parcelle.numero_parcelle} bloquée au contentieux (aucun litige lié, alerte non créée)',
            'parcelle_id': parcelle.id,
            'litiges_bloques': litiges_bloques
        }), 200

    db.session.add(alerte)
    db.session.commit()

    return jsonify({
        'message': f'Parcelle {parcelle.numero_parcelle} placée au contentieux avec succès',
        'parcelle_id': parcelle.id,
        'numero_parcelle': parcelle.numero_parcelle,
        'litiges_bloques': litiges_bloques,
        'alerte_id': alerte.id,
        'motif': motif
    }), 200


@cadastre_bp.route('/etat-juridique/<int:parcelle_id>', methods=['GET'])
@jwt_required()
def consulter_etat_juridique(parcelle_id):
    """
    Consulter l'état juridique d'une parcelle
    """
    parcelle = Parcelle.query.get(parcelle_id)
    
    if not parcelle:
        return jsonify({'message': 'Parcelle non trouvée'}), 404
    
    return jsonify({
        'numero_parcelle': parcelle.numero_parcelle,
        'etat_juridique': parcelle.etat_juridique,
        'numero_titre': parcelle.numero_titre,
        'date_titre': parcelle.date_titre.isoformat() if parcelle.date_titre else None,
        'statut_litige': parcelle.statut == 'litigieuse',
        'observations': parcelle.observations
    }), 200
