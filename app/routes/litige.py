from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User
from app.models.parcelle import Parcelle
from app.models.litige import Litige, DossierLitige, AlerteLitige
from datetime import datetime

litige_bp = Blueprint('litige', __name__)

@litige_bp.route('/dossier', methods=['POST'])
@jwt_required()
def enregistrer_dossier():
    """
    Enregistrer un dossier de litige (agent judiciaire)
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user or user.role.nom != 'agent_judiciaire':
        return jsonify({'message': 'Accès refusé'}), 403
    
    data = request.get_json()
    
    # Validation
    required_fields = ['numero_dossier', 'parcelle_id', 'type_litige', 'description']
    if not all(k in data for k in required_fields):
        return jsonify({'message': 'Données manquantes'}), 400
    
    # Chercher la parcelle par ID ou par numéro
    pid = data.get('parcelle_id')
    parcelle = None
    if pid and str(pid).isdigit():
        parcelle = Parcelle.query.get(int(pid))
    elif pid:
        parcelle = Parcelle.query.filter_by(numero_parcelle=str(pid)).first()
    if not parcelle:
        return jsonify({'message': 'Parcelle non trouvée'}), 404
    
    # Créer le litige
    litige = Litige(
        numero_dossier=data['numero_dossier'],
        parcelle_id=parcelle.id,
        type_litige=data['type_litige'],
        description=data['description'],
        demandeur=data.get('demandeur'),
        defendeur=data.get('defendeur'),
        tribunal_competent=data.get('tribunal_competent')
    )
    
    # Mettre à jour le statut de la parcelle
    parcelle.statut = 'litigieuse'
    
    db.session.add(litige)
    db.session.commit()
    
    # Créer une alerte automatique
    alerte = AlerteLitige(
        parcelle_id=parcelle.id,
        litige_id=litige.id,
        type_alerte='nouveau_litige',
        message=f'Nouveau litige enregistré: {data["type_litige"]}',
        priorite='haute'
    )
    db.session.add(alerte)
    db.session.commit()
    
    return jsonify({
        'message': 'Dossier enregistré avec succès',
        'litige_id': litige.id,
        'alerte_id': alerte.id
    }), 201

@litige_bp.route('/dossier/<int:dossier_id>', methods=['PUT'])
@jwt_required()
def mettre_a_jour_litige(dossier_id):
    """
    Mettre à jour le statut d'un litige
    """
    litige = Litige.query.get(dossier_id)
    
    if not litige:
        return jsonify({'message': 'Litige non trouvé'}), 404
    
    data = request.get_json()
    
    if 'statut' in data:
        litige.statut = data['statut']
        
        # Si le litige est résolu, mettre à jour la parcelle
        if data['statut'] == 'resolu':
            litige.date_resolution = datetime.utcnow()
            parcelle = litige.parcelle
            
            # Désactiver les alertes liées
            alertes = AlerteLitige.query.filter_by(litige_id=litige.id).all()
            for alerte in alertes:
                alerte.active = False
                alerte.date_resolution = datetime.utcnow()
            
            # Si pas d'autres litiges actifs, restaurer le statut de la parcelle
            other_litiges = Litige.query.filter(
                Litige.parcelle_id == parcelle.id,
                Litige.id != litige.id,
                Litige.statut.in_(['ouvert', 'en_cours'])
            ).count()
            
            if other_litiges == 0:
                parcelle.statut = 'normal'
    
    if 'reference_jugement' in data:
        litige.reference_jugement = data['reference_jugement']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Litige mis à jour',
        'litige_id': litige.id
    }), 200

@litige_bp.route('/dossier/<int:litige_id>/parcelles', methods=['GET'])
@jwt_required()
def consulter_parcelles_contentieuses(litige_id):
    """
    Consulter les parcelles en contentieux associées à un litige
    """
    litige = Litige.query.get(litige_id)
    
    if not litige:
        return jsonify({'message': 'Litige non trouvé'}), 404
    
    parcelle = litige.parcelle
    
    return jsonify({
        'litige_id': litige.id,
        'numero_dossier': litige.numero_dossier,
        'parcelles': [{
            'id': parcelle.id,
            'numero_parcelle': parcelle.numero_parcelle,
            'proprietaire': parcelle.proprietaire,
            'superficie': parcelle.superficie,
            'commune': parcelle.commune,
            'statut': parcelle.statut
        }]
    }), 200

@litige_bp.route('/alertes', methods=['GET'])
@jwt_required()
def consulter_alertes():
    """
    Consulter les alertes de litiges actives
    """
    alertes = AlerteLitige.query.filter_by(active=True).all()
    
    return jsonify({
        'count': len(alertes),
        'alertes': [{
            'id': alerte.id,
            'parcelle_id': alerte.parcelle_id,
            'litige_id': alerte.litige_id,
            'type_alerte': alerte.type_alerte,
            'message': alerte.message,
            'priorite': alerte.priorite,
            'date_creation': alerte.date_creation.isoformat()
        } for alerte in alertes]
    }), 200

@litige_bp.route('/dossiers', methods=['GET'])
@jwt_required()
def lister_dossiers():
    """
    Lister tous les dossiers de litige
    ?statut=ouvert|en_cours|resolu
    """
    statut = request.args.get('statut')
    query = Litige.query
    if statut:
        query = query.filter(Litige.statut == statut)
    litiges = query.order_by(Litige.date_enregistrement.desc()).all()

    return jsonify({
        'count': len(litiges),
        'dossiers': [{
            'id': l.id,
            'numero_dossier': l.numero_dossier,
            'type_litige': l.type_litige,
            'description': l.description,
            'statut': l.statut,
            'demandeur': l.demandeur,
            'defendeur': l.defendeur,
            'tribunal_competent': l.tribunal_competent,
            'parcelle_id': l.parcelle_id,
            'parcelle_numero': l.parcelle.numero_parcelle if l.parcelle else None,
            'date_ouverture': l.date_enregistrement.isoformat() if l.date_enregistrement else None,
            'date_resolution': l.date_resolution.isoformat() if l.date_resolution else None
        } for l in litiges]
    }), 200


@litige_bp.route('/litiges', methods=['GET'])
@jwt_required()
def lister_litiges():
    """
    Alias /litiges — même données que /dossiers, format allégé
    """
    litiges = Litige.query.order_by(Litige.date_enregistrement.desc()).all()
    return jsonify({
        'count': len(litiges),
        'litiges': [{
            'id': l.id,
            'numero_dossier': l.numero_dossier,
            'type': l.type_litige,
            'statut': l.statut,
            'parcelle_id': l.parcelle_id,
            'demandeur': l.demandeur,
            'defendeur': l.defendeur,
            'date_creation': l.date_enregistrement.isoformat() if l.date_enregistrement else None
        } for l in litiges]
    }), 200


@litige_bp.route('/alerte/<int:alerte_id>', methods=['PUT'])
@jwt_required()
def resoudre_alerte(alerte_id):
    """
    Marquer une alerte comme résolue
    """
    alerte = AlerteLitige.query.get(alerte_id)
    
    if not alerte:
        return jsonify({'message': 'Alerte non trouvée'}), 404
    
    alerte.active = False
    alerte.date_resolution = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': 'Alerte résolue'}), 200
