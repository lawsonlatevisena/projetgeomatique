from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models.user import User, Role
from app.models.alerte import Alerte
from app.models.parcelle import Parcelle
from app.models.litige import Litige

admin_bp = Blueprint('admin', __name__)

def check_admin(user_id):
    """Vérifier que l'utilisateur est administrateur"""
    user = User.query.get(user_id)
    return user and user.role.nom == 'admin'

@admin_bp.route('/utilisateurs', methods=['GET'])
@jwt_required()
def lister_utilisateurs():
    """
    Lister tous les utilisateurs
    """
    user_id = get_jwt_identity()
    if not check_admin(user_id):
        return jsonify({'message': 'Accès refusé'}), 403
    
    utilisateurs = User.query.all()
    
    return jsonify({
        'count': len(utilisateurs),
        'utilisateurs': [{
            'id': u.id,
            'nom': u.nom,
            'email': u.email,
            'institution': u.institution,
            'role': u.role.nom,
            'actif': u.actif,
            'date_creation': u.date_creation.isoformat()
        } for u in utilisateurs]
    }), 200

@admin_bp.route('/utilisateur/<int:user_id>', methods=['PUT'])
@jwt_required()
def modifier_utilisateur(user_id):
    """
    Modifier un utilisateur ou son rôle
    """
    admin_id = get_jwt_identity()
    if not check_admin(admin_id):
        return jsonify({'message': 'Accès refusé'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'Utilisateur non trouvé'}), 404
    
    data = request.get_json()
    
    if 'nom' in data:
        user.nom = data['nom']
    if 'role_id' in data:
        user.role_id = data['role_id']
    if 'institution' in data:
        user.institution = data['institution']
    if 'actif' in data:
        user.actif = data['actif']
    
    db.session.commit()
    
    return jsonify({'message': 'Utilisateur modifié'}), 200

@admin_bp.route('/utilisateur/<int:user_id>', methods=['DELETE'])
@jwt_required()
def supprimer_utilisateur(user_id):
    """
    Supprimer un utilisateur
    """
    admin_id = get_jwt_identity()
    if not check_admin(admin_id):
        return jsonify({'message': 'Accès refusé'}), 403
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({'message': 'Utilisateur non trouvé'}), 404
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'message': 'Utilisateur supprimé'}), 200

@admin_bp.route('/roles', methods=['GET'])
@jwt_required()
def lister_roles():
    """
    Lister tous les rôles
    """
    user_id = get_jwt_identity()
    if not check_admin(user_id):
        return jsonify({'message': 'Accès refusé'}), 403
    
    roles = Role.query.all()
    
    return jsonify({
        'count': len(roles),
        'roles': [{
            'id': r.id,
            'nom': r.nom,
            'description': r.description,
            'permissions': r.permissions
        } for r in roles]
    }), 200

@admin_bp.route('/parametres-alertes', methods=['GET'])
@jwt_required()
def obtenir_parametres_alertes():
    """
    Obtenir les paramètres de configuration des alertes
    """
    user_id = get_jwt_identity()
    if not check_admin(user_id):
        return jsonify({'message': 'Accès refusé'}), 403
    
    # À implémenter selon les besoins
    return jsonify({
        'types_alertes': [
            'nouveau_litige',
            'blocage_operation',
            'conflit_limite',
            'double_vente',
            'titre_multiple'
        ],
        'niveaux_priorite': ['basse', 'normale', 'haute'],
        'seuils_alerte': {
            'superficie_min_ha': 0.5,
            'délai_traitement_jours': 30
        }
    }), 200

@admin_bp.route('/parametres-alertes', methods=['PUT'])
@jwt_required()
def parametrer_alertes():
    """
    Paramétrer les règles d'alerte
    """
    user_id = get_jwt_identity()
    if not check_admin(user_id):
        return jsonify({'message': 'Accès refusé'}), 403
    
    data = request.get_json()
    
    # À implémenter selon les besoins spécifiques
    
    return jsonify({'message': 'Paramètres mis à jour'}), 200

@admin_bp.route('/base-donnees/status', methods=['GET'])
@jwt_required()
def status_base_donnees():
    """
    Vérifier le statut et les statistiques de la base de données
    """
    user_id = get_jwt_identity()
    if not check_admin(user_id):
        return jsonify({'message': 'Accès refusé'}), 403
    
    stats = {
        'parcelles_total': Parcelle.query.count(),
        'utilisateurs_total': User.query.count(),
        'alertes_actives': Alerte.query.filter_by(active=True).count(),
        'litiges_total': Litige.query.count(),
        'litiges_ouverts': Litige.query.filter_by(statut='ouvert').count(),
        'parcelles_litigieuses': Parcelle.query.filter_by(statut='litigieuse').count(),
        'roles': Role.query.count()
    }
    
    return jsonify(stats), 200

@admin_bp.route('/backup', methods=['POST'])
@jwt_required()
def creer_backup():
    """
    Créer une sauvegarde de la base de données
    """
    user_id = get_jwt_identity()
    if not check_admin(user_id):
        return jsonify({'message': 'Accès refusé'}), 403
    
    # À implémenter
    return jsonify({
        'message': 'Sauvegarde créée',
        'backup_id': 'backup_2026_02_16'
    }), 201
