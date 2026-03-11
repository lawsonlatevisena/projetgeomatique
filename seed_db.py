#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script d'initialisation des données de test pour le projet SIG
Exécuter après flask init-db
"""

from app import create_app, db
from app.models.user import User, Role
from app.models.parcelle import Parcelle, GeometrieParcelle
from app.models.litige import Litige, DossierLitige, AlerteLitige
from app.models.alerte import Alerte
from datetime import datetime, timedelta

app = create_app()

def seed_data():
    """Créer les données de test"""
    
    with app.app_context():
        # Vérifier si les données existent déjà
        if User.query.first():
            print(" Données existantes. Utilisation des données existantes.")
            print(" Base de données prête !")
            return
        
        print(" Création des tables...")
        db.create_all()
        
        # 1. Créer les rôles
        print(" Création des rôles...")
        roles = [
            Role(
                nom='admin',
                description='Administrateur du système',
                permissions={'all': True}
            ),
            Role(
                nom='agent_cadastre',
                description='Agent du cadastre',
                permissions={
                    'consulter_carte': True,
                    'rechercher_parcelle': True,
                    'enregistrer_operation': True
                }
            ),
            Role(
                nom='agent_judiciaire',
                description='Agent judiciaire / Tribunal',
                permissions={
                    'enregistrer_dossier': True,
                    'mettre_a_jour_litige': True
                }
            ),
            Role(
                nom='collectivite',
                description='Collectivité territoriale',
                permissions={
                    'consulter_carte_fonciere': True,
                    'voir_alertes': True
                }
            )
        ]
        
        for role in roles:
            db.session.add(role)
        db.session.commit()
        
        # 2. Créer les utilisateurs
        print("‍ Création des utilisateurs...")
        users = []
        
        # Admin
        admin = User(
            email='admin@litige.tg',
            nom='Administrateur Système',
            telephone='+228 90 00 00 01',
            institution='Direction du Cadastre',
            role_id=roles[0].id,
            actif=True
        )
        admin.set_password('admin123')
        users.append(admin)
        
        # Agent Cadastre
        agent_cadastre = User(
            email='agent.cadastre@litige.tg',
            nom='Koffi Agbesi',
            telephone='+228 90 11 22 33',
            institution='Cadastre Région Maritime',
            role_id=roles[1].id,
            actif=True
        )
        agent_cadastre.set_password('password123')
        users.append(agent_cadastre)
        
        # Agent Judiciaire
        agent_jud = User(
            email='agent.judiciaire@litige.tg',
            nom='Marie Mensah',
            telephone='+228 90 44 55 66',
            institution='Tribunal 1ère Instance Lomé',
            role_id=roles[2].id,
            actif=True
        )
        agent_jud.set_password('password123')
        users.append(agent_jud)
        
        # Collectivité
        collectivite = User(
            email='collectivite@litige.tg',
            nom='Samuel Atabidze',
            telephone='+228 90 77 88 99',
            institution='Mairie de Lomé',
            role_id=roles[3].id,
            actif=True
        )
        collectivite.set_password('password123')
        users.append(collectivite)
        
        for user in users:
            db.session.add(user)
        db.session.commit()
        
        # 3. Créer les parcelles de test
        print("️  Création des parcelles...")
        parcelles_data = [
            {
                'numero_parcelle': 'MAR-2024-001',
                'proprietaire': 'Jean Dupont',
                'superficie': 5000,
                'lieu_dit': 'Logozadakpa',
                'commune': 'Lomé',
                'region': 'Maritime',
                'numero_titre': 'TF-001/2020',
                'statut': 'normal',
                'etat_juridique': 'foncier'
            },
            {
                'numero_parcelle': 'MAR-2024-002',
                'proprietaire': 'Marie Martin',
                'superficie': 8000,
                'lieu_dit': 'Adidogomé',
                'commune': 'Lomé',
                'region': 'Maritime',
                'numero_titre': 'TF-002/2020',
                'statut': 'litigieuse',
                'etat_juridique': 'foncier'
            },
            {
                'numero_parcelle': 'MAR-2024-003',
                'proprietaire': 'Kofi Mensah',
                'superficie': 3500,
                'lieu_dit': 'Akodessewa',
                'commune': 'Lacs',
                'region': 'Maritime',
                'numero_titre': 'TF-003/2021',
                'statut': 'litigieuse',
                'etat_juridique': 'collectif'
            },
            {
                'numero_parcelle': 'MAR-2024-004',
                'proprietaire': 'SARL Commerce Plus',
                'superficie': 15000,
                'lieu_dit': 'Kodjoviakopé',
                'commune': 'Lomé',
                'region': 'Maritime',
                'numero_titre': 'TF-004/2021',
                'statut': 'normal',
                'etat_juridique': 'domanial'
            }
        ]
        
        parcelles = []
        for data in parcelles_data:
            parcelle = Parcelle(**data)
            parcelles.append(parcelle)
            db.session.add(parcelle)
        
        db.session.commit()
        
        # 4. Créer des litiges
        print("️  Création des litiges...")
        litige1 = Litige(
            numero_dossier='LIT-2026-001',
            parcelle_id=parcelles[1].id,
            type_litige='double_vente',
            description='Deux titres de propriété émis pour la même parcelle par l\'administration cadastrale',
            statut='ouvert',
            demandeur='Marie Martin',
            defendeur='Pierre Durand',
            tribunal_competent='Tribunal 1ère Instance de Lomé'
        )
        
        litige2 = Litige(
            numero_dossier='LIT-2026-002',
            parcelle_id=parcelles[2].id,
            type_litige='conflit_limite',
            description='Conflit sur les limites de la parcelle avec le voisin',
            statut='en_cours',
            demandeur='Kofi Mensah',
            defendeur='Amedom Adigon',
            tribunal_competent='Tribunal 1ère Instance de Lacs'
        )
        
        db.session.add(litige1)
        db.session.add(litige2)
        db.session.commit()
        
        # 5. Créer des alertes
        print(" Création des alertes...")
        alertes = [
            AlerteLitige(
                parcelle_id=parcelles[1].id,
                litige_id=litige1.id,
                type_alerte='double_vente',
                message='Double vente détectée: bloquer toute nouvelle opération',
                priorite='haute',
                active=True
            ),
            AlerteLitige(
                parcelle_id=parcelles[2].id,
                litige_id=litige2.id,
                type_alerte='conflit_limite',
                message='Conflit de limites: consulter dossier tribunal',
                priorite='normale',
                active=True
            )
        ]
        
        for alerte in alertes:
            db.session.add(alerte)
        db.session.commit()
        
        # 6. Créer des alertes génériques
        print(" Création des alertes génériques...")
        alertes_generiques = [
            Alerte(
                titre='Parcelles à risque identifiées',
                message='3 parcelles en zone à risque nécessitent une vérification',
                type_alerte='zone_risque',
                priorite='haute',
                region='Maritime',
                commune='Lomé',
                active=True
            ),
            Alerte(
                titre='Mise à jour cadastrale requise',
                message='10 parcelles doivent être mises à jour',
                type_alerte='maj_cadastre',
                priorite='normale',
                region='Maritime',
                active=True
            )
        ]
        
        for alerte in alertes_generiques:
            db.session.add(alerte)
        db.session.commit()
        
        print(" Base de données initialisée avec succès !")
        print("\n Données créées:")
        print(f"   - {len(users)} utilisateurs")
        print(f"   - {len(parcelles)} parcelles")
        print(f"   - 2 litiges")
        print(f"   - 2 alertes litige + 2 alertes génériques")
        
        print("\n Identifiants de test:")
        print("   Admin: admin@litige.tg / admin123")
        print("   Agent Cadastre: agent.cadastre@litige.tg / password123")
        print("   Agent Judiciaire: agent.judiciaire@litige.tg / password123")
        print("   Collectivité: collectivite@litige.tg / password123")

if __name__ == '__main__':
    seed_data()
