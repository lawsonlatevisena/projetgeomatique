# -*- coding: utf-8 -*-
import os
from app import create_app, db
from app.models.user import Role, User, RoleEnum
from flask import jsonify, render_template, request
from flask_login import login_required, current_user
from datetime import datetime

app = create_app()

@app.route('/')
def index():
    """Page d'accueil avec formulaire de connexion"""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Dashboard utilisateur - rendu selon le rôle"""
    user_role = request.args.get('role', 'admin')
    user_name = request.args.get('name', 'Utilisateur')
    
    # Mapping des rôles vers les templates
    role_templates = {
        'admin': 'dashboard_admin.html',
        'agent_cadastre': 'dashboard_cadastre.html',
        'agent_judiciaire': 'dashboard_judiciaire.html',
        'collectivite': 'dashboard_collectivite.html'
    }
    
    template = role_templates.get(user_role, 'dashboard_admin.html')
    return render_template(template, user_name=user_name, user_role=user_role)

@app.route('/dashboard.html')
def dashboard_alt():
    """Alias pour /dashboard.html"""
    return dashboard()

@app.shell_context_processor
def make_shell_context():
    """Contexte pour flask shell"""
    return {'db': db, 'User': User, 'Role': Role}

@app.cli.command()
def init_db():
    """Initialiser la base de données avec les rôles par défaut"""
    # Créer les tables
    db.create_all()
    
    # Créer les rôles
    roles_data = [
        {
            'nom': 'admin',
            'description': 'Administrateur du système',
            'permissions': {'all': True}
        },
        {
            'nom': 'agent_cadastre',
            'description': 'Agent du cadastre',
            'permissions': {
                'consulter_carte': True,
                'rechercher_parcelle': True,
                'consulter_etat_juridique': True,
                'enregistrer_operation': True,
                'recevoir_alerte': True
            }
        },
        {
            'nom': 'agent_judiciaire',
            'description': 'Agent judiciaire / Tribunal',
            'permissions': {
                'enregistrer_dossier_litige': True,
                'mettre_a_jour_litige': True,
                'associer_litige_parcelle': True,
                'consulter_parcelles_contentieuses': True
            }
        },
        {
            'nom': 'collectivite',
            'description': 'Collectivité territoriale',
            'permissions': {
                'consulter_carte_fonciere': True,
                'consulter_parcelles_risque': True,
                'consulter_alertes': True,
                'voir_statistiques': True
            }
        }
    ]
    
    for role_data in roles_data:
        if not Role.query.filter_by(nom=role_data['nom']).first():
            role = Role(
                nom=role_data['nom'],
                description=role_data['description'],
                permissions=role_data['permissions']
            )
            db.session.add(role)
    
    db.session.commit()
    print('Base de données initialisée avec succès!')

@app.cli.command()
def create_admin():
    """Créer un utilisateur administrateur"""
    email = input('Email: ')
    nom = input('Nom: ')
    password = input('Mot de passe: ')
    
    if User.query.filter_by(email=email).first():
        print('Cet email existe déjà!')
        return
    
    admin_role = Role.query.filter_by(nom='admin').first()
    if not admin_role:
        print('Le rôle admin n\'existe pas. Exécutez d\'abord: flask init-db')
        return
    
    user = User(
        email=email,
        nom=nom,
        role_id=admin_role.id,
        actif=True
    )
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    print('Administrateur {} cree avec succes!'.format(email))

@app.route('/diagnose')
def diagnose():
    """Diagnostic complet"""
    from app.models.user import User
    from app.models.parcelle import Parcelle
    from app.models.litige import Litige
    from app.models.alerte import Alerte
    
    users = db.session.query(User).count()
    parcelles = db.session.query(Parcelle).count()
    litiges = db.session.query(Litige).count()
    alertes = db.session.query(Alerte).count()
    
    admin = db.session.query(User).filter_by(email='admin@litige.tg').first()
    admin_pwd_ok = admin.check_password('admin123') if admin else False
    
    users_ok = "" if users > 0 else ""
    admin_ok = "OK" if admin else "NO"
    pwd_ok = "OK" if admin_pwd_ok else "NO"
    parcelles_ok = "OK" if parcelles > 0 else "NO"
    litiges_ok = "OK" if litiges > 0 else "NO"
    alertes_ok = "OK" if alertes > 0 else "NO"
    
    admin_email = admin.email if admin else "N/A"
    admin_status = "OUI" if admin else "NON"
    pwd_status = "CORRECT" if admin_pwd_ok else "INCORRECT"
    
    pwd_line = "<p>Password admin123: {}</p>".format(pwd_status) if admin else ""
    email_line = "<p>Email: {}</p>".format(admin_email) if admin else ""
    
    html_content = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Diagnostic</title>
    <style>
        body { font-family: monospace; background: #1e1e1e; color: #d4d4d4; padding: 20px; }
        .card { background: #252526; border-left: 4px solid #007acc; padding: 15px; margin: 10px 0; }
        .ok { color: #4ec9b0; }
        .error { color: #f48771; }
        h2 { color: #4ec9b0; }
        button { padding: 10px 20px; background: #007acc; color: white; border: none; cursor: pointer; margin: 5px; }
    </style>
</head>
<body>
    <h1>DIAGNOSTIC SYSTEME</h1>
    
    <div class="card">
        <h2>Donnees en BD</h2>
        <p>Users: {}</p>
        <p>Parcelles: {}</p>
        <p>Litiges: {}</p>
        <p>Alertes: {}</p>
    </div>
    
    <div class="card">
        <h2>Admin User</h2>
        <p>Admin existe: {}</p>
        {}
        {}
    </div>
    
    <div class="card">
        <button onclick="init()">Initialiser donnees</button>
        <button onclick="test()">Tester login</button>
        <button onclick="location.reload()">Rafraichir</button>
        <pre id="result"></pre>
    </div>
    
    <script>
        async function init() {
            document.getElementById('result').textContent = 'Initialisation...';
            const r = await fetch('/api/init-data', {'method': 'POST'});
            const d = await r.json();
            document.getElementById('result').textContent = JSON.stringify(d, null, 2);
            setTimeout(() => location.reload(), 2000);
        }
        
        async function test() {
            document.getElementById('result').textContent = 'Test login...';
            const r = await fetch('/api/auth/login', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({'email': 'admin@litige.tg', 'mot_de_passe': 'admin123'})
            });
            const d = await r.json();
            document.getElementById('result').textContent = 'Status: ' + r.status + '\\n' + JSON.stringify(d, null, 2);
        }
    </script>
</body>
</html>""".format(users, parcelles, litiges, alertes, admin_status, pwd_line, email_line)
    
    return html_content

@app.route('/api/init-data', methods=['POST'])
def init_data():
    """Initialiser les donnees de test"""
    try:
        from app.models.parcelle import Parcelle
        from app.models.litige import Litige
        from app.models.alerte import Alerte
        
        # Verifier si donnees existent
        existing = db.session.query(User).count()
        if existing > 0:
            return jsonify({'message': '{} utilisateurs presents'.format(existing), 'exists': True})
        
        # Creer roles
        roles = {}
        for nom in ['admin', 'agent_cadastre', 'agent_judiciaire', 'collectivite']:
            role = Role(nom=nom, description=nom)
            db.session.add(role)
            db.session.flush()
            roles[nom] = role
        
        # Creer utilisateurs
        users_data = [
            ('Admin', 'admin@litige.tg', 'admin123', 'admin'),
            ('Agent Cadastre', 'agent.cadastre@litige.tg', 'password123', 'agent_cadastre'),
            ('Agent Judiciaire', 'agent.judiciaire@litige.tg', 'password123', 'agent_judiciaire'),
            ('Collectivite', 'collectivite@litige.tg', 'password123', 'collectivite'),
        ]
        
        for nom, email, pwd, role_nom in users_data:
            u = User(nom=nom, email=email, role_id=roles[role_nom].id)
            u.set_password(pwd)
            db.session.add(u)
        db.session.flush()
        
        # Creer parcelles
        parcelles = {}
        for num in ['MAR-2024-001', 'MAR-2024-002', 'SAV-2024-001', 'CHA-2024-001']:
            p = Parcelle(
                numero_parcelle=num, 
                proprietaire='Test', 
                superficie=500, 
                commune='Lome', 
                region='Togo', 
                statut='normal', 
                etat_juridique='Normal'
            )
            db.session.add(p)
            db.session.flush()
            parcelles[num] = p
        
        # Creer litiges
        for i in range(2):
            l = Litige(
                numero_dossier='LIT-2026-{:03d}'.format(i+1),
                parcelle_id=list(parcelles.values())[i].id,
                type_litige='double_vente' if i == 0 else 'conflit_limite',
                description='Litige de test {}'.format(i+1),
                statut='ouvert',
                demandeur='Demandeur Test {}'.format(i+1),
                defendeur='Defendeur Test {}'.format(i+1)
            )
            db.session.add(l)

        # Creer alertes
        for i in range(2):
            a = Alerte(
                titre='Alerte test {}'.format(i+1),
                type_alerte='test',
                priorite='haute',
                region='Togo',
                active=True,
                date_creation=datetime.now()
            )
            db.session.add(a)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Donnees creees',
            'users': 4, 
            'parcelles': 4, 
            'litiges': 2, 
            'alertes': 2
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
