from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from app.models.user import User, Role

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Authentifier un utilisateur
    Body: {email, mot_de_passe}
    """
    data = request.get_json()
    
    if not data.get('email') or not data.get('mot_de_passe'):
        return jsonify({'message': 'Email et mot de passe requis'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['mot_de_passe']):
        return jsonify({'message': 'Identifiants invalides'}), 401
    
    if not user.actif:
        return jsonify({'message': 'Compte désactivé'}), 403
    
    access_token = create_access_token(identity=user.id)
    
    return jsonify({
        'message': 'Connexion réussie',
        'access_token': access_token,
        'user': {
            'id': user.id,
            'nom': user.nom,
            'email': user.email,
            'role': user.role.nom
        }
    }), 200

@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Créer un nouveau compte utilisateur
    """
    data = request.get_json()
    
    # Validation
    if not all(k in data for k in ['email', 'mot_de_passe', 'nom', 'role_id']):
        return jsonify({'message': 'Données manquantes'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'message': 'Email déjà utilisé'}), 409
    
    user = User(
        email=data['email'],
        nom=data['nom'],
        telephone=data.get('telephone'),
        institution=data.get('institution'),
        role_id=data['role_id']
    )
    user.set_password(data['mot_de_passe'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify({
        'message': 'Utilisateur créé avec succès',
        'user_id': user.id
    }), 201

@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """
    Récupérer le profil de l'utilisateur connecté
    """
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    
    if not user:
        return jsonify({'message': 'Utilisateur non trouvé'}), 404
    
    return jsonify({
        'id': user.id,
        'nom': user.nom,
        'email': user.email,
        'telephone': user.telephone,
        'institution': user.institution,
        'role': user.role.nom,
        'actif': user.actif
    }), 200

@auth_bp.route('/logout', methods=['POST', 'GET'])
@jwt_required(optional=True)
def logout():
    """
    Déconnexion (côté client: supprimer le token)
    """
    return jsonify({'message': 'Déconnexion réussie', 'redirect': '/'}), 200
