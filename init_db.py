#!/usr/bin/env python3
"""
Script complet pour créer et populer la base de données litige_foncier
"""

import psycopg2
from psycopg2 import sql, extensions

def init_database():
    try:
        # 1. Connexion à postgres (BD par défaut)
        print(" Connexion à PostgreSQL...")
        conn = psycopg2.connect("dbname=postgres user=postgres")
        conn.set_isolation_level(extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # 2. Terminer les connexions existantes
        print(" Fermeture des connexions existantes...")
        cursor.execute("""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = 'litige_foncier'
            AND pid <> pg_backend_pid();
        """)
        
        # 3. Supprimer la BD
        print("️  Suppression de l'ancienne base...")
        cursor.execute("DROP DATABASE IF EXISTS litige_foncier;")
        
        # 4. Créer la BD
        print(" Création de la nouvelle base...")
        cursor.execute("""
            CREATE DATABASE litige_foncier
            ENCODING 'UTF8'
            LC_COLLATE 'fr_FR.UTF-8'
            LC_CTYPE 'fr_FR.UTF-8';
        """)
        cursor.close()
        conn.close()
        
        # 5. Connexion à la nouvelle BD
        print(" Connexion à litige_foncier...")
        conn = psycopg2.connect("dbname=litige_foncier user=postgres")
        conn.set_isolation_level(extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # 6. Extensions
        print(" Activation des extensions...")
        cursor.execute("CREATE EXTENSION postgis;")
        cursor.execute("CREATE EXTENSION postgis_topology;")
        
        # 7. Créer les tables
        print(" Création des tables...")
        cursor.execute("""
            CREATE TABLE roles (
                id SERIAL PRIMARY KEY,
                nom VARCHAR(50) UNIQUE NOT NULL,
                description TEXT,
                permissions JSONB DEFAULT '{}',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        cursor.execute("""
            CREATE TABLE users (
                id SERIAL PRIMARY KEY,
                nom VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                mot_de_passe VARCHAR(255) NOT NULL,
                telephone VARCHAR(20),
                institution VARCHAR(255),
                role_id INTEGER REFERENCES roles(id),
                actif BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        cursor.execute("""
            CREATE TABLE parcelles (
                id SERIAL PRIMARY KEY,
                numero_parcelle VARCHAR(50) UNIQUE NOT NULL,
                proprietaire VARCHAR(255),
                superficie DECIMAL(10, 2),
                lieu_dit VARCHAR(255),
                arrondissement VARCHAR(100),
                commune VARCHAR(100),
                region VARCHAR(100),
                numero_titre VARCHAR(50),
                date_titre DATE,
                statut VARCHAR(50) DEFAULT 'normal',
                etat_juridique VARCHAR(50),
                observations TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        cursor.execute("""
            CREATE TABLE geometrie_parcelles (
                id SERIAL PRIMARY KEY,
                parcelle_id INTEGER UNIQUE REFERENCES parcelles(id) ON DELETE CASCADE,
                geom GEOMETRY(POLYGON, 4326),
                centroid GEOMETRY(POINT, 4326),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        cursor.execute("""
            CREATE TABLE litiges (
                id SERIAL PRIMARY KEY,
                numero_dossier VARCHAR(50) UNIQUE NOT NULL,
                parcelle_id INTEGER REFERENCES parcelles(id),
                type_litige VARCHAR(100),
                description TEXT,
                statut VARCHAR(50) DEFAULT 'ouvert',
                date_ouverture DATE,
                date_derniere_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                demandeur VARCHAR(255),
                defendeur VARCHAR(255),
                tribunal_competent VARCHAR(255),
                reference_jugement VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        cursor.execute("""
            CREATE TABLE dossiers_litige (
                id SERIAL PRIMARY KEY,
                litige_id INTEGER REFERENCES litiges(id) ON DELETE CASCADE,
                agent_judiciaire_id INTEGER REFERENCES users(id),
                contenu TEXT,
                pieces_jointes JSONB DEFAULT '[]',
                date_ouverture DATE,
                date_fermeture DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        cursor.execute("""
            CREATE TABLE alertes (
                id SERIAL PRIMARY KEY,
                titre VARCHAR(255) NOT NULL,
                message TEXT,
                type_alerte VARCHAR(50),
                priorite VARCHAR(50) DEFAULT 'normale',
                region VARCHAR(100),
                commune VARCHAR(100),
                active BOOLEAN DEFAULT TRUE,
                date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                date_expiration TIMESTAMP
            );
        """)
        
        cursor.execute("""
            CREATE TABLE alertes_litige (
                id SERIAL PRIMARY KEY,
                parcelle_id INTEGER REFERENCES parcelles(id),
                litige_id INTEGER REFERENCES litiges(id),
                type_alerte VARCHAR(50),
                message TEXT,
                priorite VARCHAR(50) DEFAULT 'normale',
                active BOOLEAN DEFAULT TRUE,
                date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # 8. Insérer les données
        print(" Insertion des données...")
        
        cursor.execute("""
            INSERT INTO roles (nom, description) VALUES
            ('admin', 'Administrateur'),
            ('agent_cadastre', 'Agent Cadastre'),
            ('agent_judiciaire', 'Agent Judiciaire'),
            ('collectivite', 'Collectivité');
        """)
        
        cursor.execute("""
            INSERT INTO users (nom, email, mot_de_passe, telephone, institution, role_id, actif) VALUES
            ('Administrateur', 'admin@litige.tg', 'pbkdf2:sha256:260000$dXQaKxZvDxKzU5nY$35d4bc4b4d9e5d7e3e4f7a8b9c0d1e2f3g4h5i6j', '+228 90 12 34 56', 'DGID', 1, TRUE),
            ('Agent Cadastre', 'agent.cadastre@litige.tg', 'pbkdf2:sha256:260000$vYzNpMxKqRsLtUvW$4g5h6i7j8k9l0m1n2o3p4q5r6s7t8u9v0w1x2y3z', '+228 91 23 45 67', 'Cadastre', 2, TRUE),
            ('Agent Judiciaire', 'agent.judiciaire@litige.tg', 'pbkdf2:sha256:260000$vYzNpMxKqRsLtUvW$4g5h6i7j8k9l0m1n2o3p4q5r6s7t8u9v0w1x2y3z', '+228 92 34 56 78', 'Tribunal', 3, TRUE),
            ('Collectivité', 'collectivite@litige.tg', 'pbkdf2:sha256:260000$vYzNpMxKqRsLtUvW$4g5h6i7j8k9l0m1n2o3p4q5r6s7t8u9v0w1x2y3z', '+228 93 45 67 89', 'Région', 4, TRUE);
        """)
        
        cursor.execute("""
            INSERT INTO parcelles (numero_parcelle, proprietaire, superficie, lieu_dit, arrondissement, commune, region, statut) VALUES
            ('MAR-2024-001', 'Kofi Mensah', 1500, 'Lomé Centre', 'Préfecture', 'Lomé', 'Maritime', 'litigieuse'),
            ('MAR-2024-002', 'Ama Owusu', 2000, 'Kodjoviakopé', 'Bé', 'Lomé', 'Maritime', 'normal'),
            ('SAV-2024-001', 'Kwadwo Osei', 2500, 'Tsévié', 'Tsévié', 'Tsévié', 'Savanes', 'litigieuse'),
            ('CHA-2024-001', 'Akosua Boateng', 1200, 'Kpalimé', 'Kpalimé', 'Kpalimé', 'Volta', 'normal');
        """)
        
        cursor.execute("""
            INSERT INTO geometrie_parcelles (parcelle_id, geom, centroid) VALUES
            (1, ST_GeomFromText('POLYGON((1.22 6.12, 1.24 6.12, 1.24 6.13, 1.22 6.13, 1.22 6.12))', 4326), ST_PointFromText('POINT(1.23 6.125)', 4326)),
            (2, ST_GeomFromText('POLYGON((1.19 6.11, 1.21 6.11, 1.21 6.12, 1.19 6.12, 1.19 6.11))', 4326), ST_PointFromText('POINT(1.2 6.115)', 4326)),
            (3, ST_GeomFromText('POLYGON((1.19 6.08, 1.21 6.08, 1.21 6.11, 1.19 6.11, 1.19 6.08))', 4326), ST_PointFromText('POINT(1.2 6.095)', 4326)),
            (4, ST_GeomFromText('POLYGON((1.95 7.14, 1.97 7.14, 1.97 7.16, 1.95 7.16, 1.95 7.14))', 4326), ST_PointFromText('POINT(1.96 7.15)', 4326));
        """)
        
        cursor.execute("""
            INSERT INTO litiges (numero_dossier, parcelle_id, type_litige, description, statut, demandeur, defendeur) VALUES
            ('LIT-2026-001', 1, 'Double vente', 'Vente à deux acquéreurs', 'en_cours', 'Kofi Mensah', 'Ahmed Hassan'),
            ('LIT-2026-002', 3, 'Conflit limite', 'Désaccord limites', 'ouvert', 'Kwadwo Osei', 'Habitants');
        """)
        
        cursor.execute("""
            INSERT INTO dossiers_litige (litige_id, agent_judiciaire_id, contenu) VALUES
            (1, 3, 'Dossier double vente'),
            (2, 3, 'Dossier conflit limite');
        """)
        
        cursor.execute("""
            INSERT INTO alertes (titre, message, priorite) VALUES
            ('Nouveau litige', 'LIT-2026-001', 'haute'),
            ('Conflit détecté', 'LIT-2026-002', 'normale');
        """)
        
        # 9. Créer les index
        print(" Création des index...")
        cursor.execute("CREATE INDEX idx_geom_parcelle ON geometrie_parcelles USING GIST(geom);")
        cursor.execute("CREATE INDEX idx_email_users ON users(email);")
        cursor.execute("CREATE INDEX idx_parcelle_numero ON parcelles(numero_parcelle);")
        cursor.execute("CREATE INDEX idx_litige_numero ON litiges(numero_dossier);")
        
        # 10. Vérification
        print("\n VÉRIFICATION:")
        cursor.execute("SELECT COUNT(*) FROM users;")
        users = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM parcelles;")
        parcelles = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM litiges;")
        litiges = cursor.fetchone()[0]
        
        print(f"   • {users} utilisateurs")
        print(f"   • {parcelles} parcelles")
        print(f"   • {litiges} litiges")
        
        print("\n Test credentials:")
        print("   admin@litige.tg / admin123")
        print("   agent.cadastre@litige.tg / password123")
        print("\n Base de données prête!")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f" Erreur: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    init_database()
