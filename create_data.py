#!/usr/bin/env python3
"""
Script de création rapide des utilisateurs de test
À exécuter une seule fois pour initialiser les données
"""

if __name__ == '__main__':
    import sys
    import os
    
    # Ajouter le chemin du projet
    sys.path.insert(0, '/home/lawson/Documents/PROJETGEOMATIQUE')
    os.chdir('/home/lawson/Documents/PROJETGEOMATIQUE')
    
    from app import create_app, db
    from app.models.user import User, Role, RoleEnum
    from app.models.parcelle import Parcelle, GeometrieParcelle
    from app.models.litige import Litige, DossierLitige
    from app.models.alerte import Alerte, AlerteLitige
    from sqlalchemy.orm import sessionmaker
    from datetime import datetime, timedelta
    
    print("\n" + "="*60)
    print(" INITIALISATION DES DONNÉES DE TEST")
    print("="*60)
    
    # Créer l'app
    app = create_app()
    ctx = app.app_context()
    ctx.push()
    
    try:
        # Vérifier si les données existent déjà
        existing_users = db.session.query(User).count()
        if existing_users > 0:
            print(f"\n {existing_users} utilisateurs déjà présents")
            print("Arrêt pour éviter les doublons")
            sys.exit(0)
        
        print("\n1️⃣  Création des rôles...")
        
        # Créer les rôles
        roles_data = [
            {'nom': 'admin', 'description': 'Administrateur système'},
            {'nom': 'agent_cadastre', 'description': 'Agent du cadastre'},
            {'nom': 'agent_judiciaire', 'description': 'Agent judiciaire'},
            {'nom': 'collectivite', 'description': 'Collectivité territoriale'},
        ]
        
        roles = {}
        for role_data in roles_data:
            role = db.session.query(Role).filter_by(nom=role_data['nom']).first()
            if not role:
                role = Role(nom=role_data['nom'], description=role_data['description'])
                db.session.add(role)
            roles[role_data['nom']] = role
        
        db.session.commit()
        print("    Rôles créés")
        
        print("\n2️⃣  Création des utilisateurs...")
        
        # Créer les utilisateurs
        users_data = [
            {
                'nom': 'Administrateur Système',
                'email': 'admin@litige.tg',
                'mot_de_passe': 'admin123',
                'role': 'admin'
            },
            {
                'nom': 'Agent Cadastre',
                'email': 'agent.cadastre@litige.tg',
                'mot_de_passe': 'password123',
                'role': 'agent_cadastre'
            },
            {
                'nom': 'Agent Judiciaire',
                'email': 'agent.judiciaire@litige.tg',
                'mot_de_passe': 'password123',
                'role': 'agent_judiciaire'
            },
            {
                'nom': 'Collectivité Territoriale',
                'email': 'collectivite@litige.tg',
                'mot_de_passe': 'password123',
                'role': 'collectivite'
            },
        ]
        
        for user_data in users_data:
            user = User(
                nom=user_data['nom'],
                email=user_data['email'],
                role_id=roles[user_data['role']].id
            )
            user.set_password(user_data['mot_de_passe'])
            db.session.add(user)
            print(f"    {user_data['nom']}")
        
        db.session.commit()
        print("\n3️⃣  Création des parcelles...")
        
        # Créer des parcelles
        parcelles_data = [
            {
                'numero_parcelle': 'MAR-2024-001',
                'proprietaire': 'Jean Doe',
                'superficie': 500.5,
                'lieu_dit': 'Quartier Administratif',
                'commune': 'Lomé',
                'region': 'Région Maritime',
                'statut': 'normal',
                'etat_juridique': 'Normal'
            },
            {
                'numero_parcelle': 'MAR-2024-002',
                'proprietaire': 'Marie Dupont',
                'superficie': 750.0,
                'lieu_dit': 'Quartier Kégué',
                'commune': 'Lomé',
                'region': 'Région Maritime',
                'statut': 'litigieuse',
                'etat_juridique': 'Double vente'
            },
            {
                'numero_parcelle': 'SAV-2024-001',
                'proprietaire': 'Pierre Martin',
                'superficie': 1000.0,
                'lieu_dit': 'Zone Industrielle',
                'commune': 'Tsévié',
                'region': 'Région Maritime',
                'statut': 'litigieuse',
                'etat_juridique': 'Conflit de limite'
            },
            {
                'numero_parcelle': 'CHA-2024-001',
                'proprietaire': 'Anne Kofi',
                'superficie': 250.0,
                'lieu_dit': 'Centre Ville',
                'commune': 'Kpalimé',
                'region': 'Région des Plateaux',
                'statut': 'normal',
                'etat_juridique': 'Normal'
            },
        ]
        
        parcelles = {}
        for p_data in parcelles_data:
            parcelle = Parcelle(
                numero_parcelle=p_data['numero_parcelle'],
                proprietaire=p_data['proprietaire'],
                superficie=p_data['superficie'],
                lieu_dit=p_data['lieu_dit'],
                commune=p_data['commune'],
                region=p_data['region'],
                statut=p_data['statut'],
                etat_juridique=p_data['etat_juridique']
            )
            db.session.add(parcelle)
            db.session.flush()
            parcelles[p_data['numero_parcelle']] = parcelle
            print(f"    {p_data['numero_parcelle']}")
        
        db.session.commit()
        print("\n4️⃣  Création des litiges...")
        
        # Créer des litiges
        litiges_data = [
            {
                'numero_dossier': 'LIT-2026-001',
                'parcelle_id': parcelles['MAR-2024-002'].id,
                'type_litige': 'Double vente',
                'description': 'Parcelle vendue deux fois par le même propriétaire',
                'statut': 'ouvert',
                'demandeur': 'Jean Kofi',
                'defendeur': 'Jean Doe'
            },
            {
                'numero_dossier': 'LIT-2026-002',
                'parcelle_id': parcelles['SAV-2024-001'].id,
                'type_litige': 'Conflit de limite',
                'description': 'Désaccord sur la délimitation des parcelles',
                'statut': 'ouvert',
                'demandeur': 'Pierre Martin',
                'defendeur': 'Propriétaire voisin'
            },
        ]
        
        litiges = {}
        for l_data in litiges_data:
            litige = Litige(
                numero_dossier=l_data['numero_dossier'],
                parcelle_id=l_data['parcelle_id'],
                type_litige=l_data['type_litige'],
                description=l_data['description'],
                statut=l_data['statut'],
                demandeur=l_data['demandeur'],
                defendeur=l_data['defendeur'],
                date_creation=datetime.now()
            )
            db.session.add(litige)
            db.session.flush()
            litiges[l_data['numero_dossier']] = litige
            print(f"    {l_data['numero_dossier']}")
        
        db.session.commit()
        print("\n5️⃣  Création des alertes...")
        
        # Créer des alertes
        alertes_data = [
            {
                'type_alerte': 'nouveau_litige',
                'priorite': 'haute',
                'region': 'Région Maritime',
                'commune': 'Lomé',
                'description': 'Double vente détectée'
            },
            {
                'type_alerte': 'conflit_limite',
                'priorite': 'normale',
                'region': 'Région Maritime',
                'commune': 'Tsévié',
                'description': 'Conflit de limite signalé'
            },
        ]
        
        for a_data in alertes_data:
            alerte = Alerte(
                type_alerte=a_data['type_alerte'],
                priorite=a_data['priorite'],
                region=a_data['region'],
                commune=a_data['commune'],
                description=a_data['description'],
                statut='active',
                date_creation=datetime.now()
            )
            db.session.add(alerte)
            print(f"    {a_data['type_alerte']} ({a_data['priorite']})")
        
        db.session.commit()
        
        # Résumé
        print("\n" + "="*60)
        print(" DONNÉES CRÉÉES AVEC SUCCÈS!")
        print("="*60)
        
        users = db.session.query(User).count()
        parcelles = db.session.query(Parcelle).count()
        litiges = db.session.query(Litige).count()
        alertes = db.session.query(Alerte).count()
        
        print(f"\n Résumé:")
        print(f"    {users} utilisateurs")
        print(f"   ️  {parcelles} parcelles")
        print(f"   ️  {litiges} litiges")
        print(f"    {alertes} alertes")
        
        print("\n Identifiants de test:")
        print("    Admin: admin@litige.tg / admin123")
        print("    Cadastre: agent.cadastre@litige.tg / password123")
        print("    Judiciaire: agent.judiciaire@litige.tg / password123")
        print("    Collectivité: collectivite@litige.tg / password123")
        
        print("\n Accédez à: http://127.0.0.1:5000")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n ERREUR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
