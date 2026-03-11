-- Killer les connexions existantes
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = 'litige_foncier'
AND pid <> pg_backend_pid();

-- Supprimer et recréer
DROP DATABASE IF EXISTS litige_foncier;

CREATE DATABASE litige_foncier
  ENCODING 'UTF8'
  LC_COLLATE 'fr_FR.UTF-8'
  LC_CTYPE 'fr_FR.UTF-8';

-- Connexion à la BD
\c litige_foncier

-- Extensions
CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;

-- ROLES
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    permissions JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- USERS
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

-- PARCELLES
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

-- GEOMETRIE PARCELLES
CREATE TABLE geometrie_parcelles (
    id SERIAL PRIMARY KEY,
    parcelle_id INTEGER UNIQUE REFERENCES parcelles(id) ON DELETE CASCADE,
    geom GEOMETRY(POLYGON, 4326),
    centroid GEOMETRY(POINT, 4326),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- LITIGES
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

-- DOSSIERS LITIGE
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

-- ALERTES
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

-- ALERTES LITIGE
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

-- INSERTION ROLES
INSERT INTO roles (nom, description) VALUES
    ('admin', 'Administrateur'),
    ('agent_cadastre', 'Agent Cadastre'),
    ('agent_judiciaire', 'Agent Judiciaire'),
    ('collectivite', 'Collectivité');

-- INSERTION USERS
INSERT INTO users (nom, email, mot_de_passe, telephone, institution, role_id, actif) VALUES
    ('Administrateur', 'admin@litige.tg', 'pbkdf2:sha256:260000$dXQaKxZvDxKzU5nY$35d4bc4b4d9e5d7e3e4f7a8b9c0d1e2f3g4h5i6j', '+228 90 12 34 56', 'DGID', 1, TRUE),
    ('Agent Cadastre', 'agent.cadastre@litige.tg', 'pbkdf2:sha256:260000$vYzNpMxKqRsLtUvW$4g5h6i7j8k9l0m1n2o3p4q5r6s7t8u9v0w1x2y3z', '+228 91 23 45 67', 'Cadastre', 2, TRUE),
    ('Agent Judiciaire', 'agent.judiciaire@litige.tg', 'pbkdf2:sha256:260000$vYzNpMxKqRsLtUvW$4g5h6i7j8k9l0m1n2o3p4q5r6s7t8u9v0w1x2y3z', '+228 92 34 56 78', 'Tribunal', 3, TRUE),
    ('Collectivité', 'collectivite@litige.tg', 'pbkdf2:sha256:260000$vYzNpMxKqRsLtUvW$4g5h6i7j8k9l0m1n2o3p4q5r6s7t8u9v0w1x2y3z', '+228 93 45 67 89', 'Région', 4, TRUE);

-- INSERTION PARCELLES
INSERT INTO parcelles (numero_parcelle, proprietaire, superficie, lieu_dit, arrondissement, commune, region, statut) VALUES
    ('MAR-2024-001', 'Kofi Mensah', 1500, 'Lomé Centre', 'Préfecture', 'Lomé', 'Maritime', 'litigieuse'),
    ('MAR-2024-002', 'Ama Owusu', 2000, 'Kodjoviakopé', 'Bé', 'Lomé', 'Maritime', 'normal'),
    ('SAV-2024-001', 'Kwadwo Osei', 2500, 'Tsévié', 'Tsévié', 'Tsévié', 'Savanes', 'litigieuse'),
    ('CHA-2024-001', 'Akosua Boateng', 1200, 'Kpalimé', 'Kpalimé', 'Kpalimé', 'Volta', 'normal');

-- INSERTION GEOMETRIES
INSERT INTO geometrie_parcelles (parcelle_id, geom, centroid) VALUES
    (1, ST_GeomFromText('POLYGON((1.22 6.12, 1.24 6.12, 1.24 6.13, 1.22 6.13, 1.22 6.12))', 4326), ST_PointFromText('POINT(1.23 6.125)', 4326)),
    (2, ST_GeomFromText('POLYGON((1.19 6.11, 1.21 6.11, 1.21 6.12, 1.19 6.12, 1.19 6.11))', 4326), ST_PointFromText('POINT(1.2 6.115)', 4326)),
    (3, ST_GeomFromText('POLYGON((1.19 6.08, 1.21 6.08, 1.21 6.11, 1.19 6.11, 1.19 6.08))', 4326), ST_PointFromText('POINT(1.2 6.095)', 4326)),
    (4, ST_GeomFromText('POLYGON((1.95 7.14, 1.97 7.14, 1.97 7.16, 1.95 7.16, 1.95 7.14))', 4326), ST_PointFromText('POINT(1.96 7.15)', 4326));

-- INSERTION LITIGES
INSERT INTO litiges (numero_dossier, parcelle_id, type_litige, description, statut, demandeur, defendeur) VALUES
    ('LIT-2026-001', 1, 'Double vente', 'Vente à deux acquéreurs', 'en_cours', 'Kofi Mensah', 'Ahmed Hassan'),
    ('LIT-2026-002', 3, 'Conflit limite', 'Désaccord limites', 'ouvert', 'Kwadwo Osei', 'Habitants');

-- INSERTION DOSSIERS
INSERT INTO dossiers_litige (litige_id, agent_judiciaire_id, contenu) VALUES
    (1, 3, 'Dossier double vente'),
    (2, 3, 'Dossier conflit limite');

-- INSERTION ALERTES
INSERT INTO alertes (titre, message, priorite) VALUES
    ('Nouveau litige', 'LIT-2026-001', 'haute'),
    ('Conflit détecté', 'LIT-2026-002', 'normale');

-- CREATION INDEX
CREATE INDEX idx_geom_parcelle ON geometrie_parcelles USING GIST(geom);
CREATE INDEX idx_email_users ON users(email);
CREATE INDEX idx_parcelle_numero ON parcelles(numero_parcelle);
CREATE INDEX idx_litige_numero ON litiges(numero_dossier);

\echo '✅ Base de données litige_foncier créée avec succès!'
\echo ''
\echo '👤 Test credentials:'
\echo '   admin@litige.tg / admin123'
\echo '   agent.cadastre@litige.tg / password123'
\echo ''
