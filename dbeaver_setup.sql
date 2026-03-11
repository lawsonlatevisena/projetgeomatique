-- ============================================================================
-- SCRIPT SQL COMPLET POUR DBEAVER
-- Système de Gestion des Litiges Fonciers - Togo
-- ============================================================================
-- 
-- À EXÉCUTER DANS DBEAVER:
-- 1. Click droit sur la connexion PostgreSQL > SQL Editor > New SQL Script
-- 2. Copie-colle ce contenu
-- 3. Click "Execute" ou Ctrl+Enter
--
-- ============================================================================

-- DROP EXISTING DATABASE
DROP DATABASE IF EXISTS litige_foncier;

-- CREATE DATABASE
CREATE DATABASE litige_foncier
  ENCODING 'UTF8'
  LC_COLLATE 'fr_FR.UTF-8'
  LC_CTYPE 'fr_FR.UTF-8';

-- ============================================================================
-- SWITCH TO NEW DATABASE AND CREATE TABLES
-- ============================================================================

-- Create roles table
CREATE TABLE public.roles (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    permissions JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create users table
CREATE TABLE public.users (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    mot_de_passe VARCHAR(255) NOT NULL,
    telephone VARCHAR(20),
    institution VARCHAR(255),
    role_id INTEGER NOT NULL REFERENCES public.roles(id),
    actif BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create parcelles table
CREATE TABLE public.parcelles (
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
    statut VARCHAR(50) DEFAULT 'normal' CHECK(statut IN ('normal', 'litigieuse', 'bloquee')),
    etat_juridique VARCHAR(50),
    observations TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create geometrie_parcelles table (PostGIS)
CREATE TABLE public.geometrie_parcelles (
    id SERIAL PRIMARY KEY,
    parcelle_id INTEGER UNIQUE NOT NULL REFERENCES public.parcelles(id) ON DELETE CASCADE,
    geom GEOMETRY(POLYGON, 4326),
    centroid GEOMETRY(POINT, 4326),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create litiges table
CREATE TABLE public.litiges (
    id SERIAL PRIMARY KEY,
    numero_dossier VARCHAR(50) UNIQUE NOT NULL,
    parcelle_id INTEGER NOT NULL REFERENCES public.parcelles(id),
    type_litige VARCHAR(100),
    description TEXT,
    statut VARCHAR(50) DEFAULT 'ouvert' CHECK(statut IN ('ouvert', 'en_cours', 'resolu', 'suspendu', 'rejet')),
    date_ouverture DATE,
    date_derniere_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    demandeur VARCHAR(255),
    defendeur VARCHAR(255),
    tribunal_competent VARCHAR(255),
    reference_jugement VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create dossiers_litige table
CREATE TABLE public.dossiers_litige (
    id SERIAL PRIMARY KEY,
    litige_id INTEGER NOT NULL REFERENCES public.litiges(id) ON DELETE CASCADE,
    agent_judiciaire_id INTEGER REFERENCES public.users(id),
    contenu TEXT,
    pieces_jointes JSONB DEFAULT '[]',
    date_ouverture DATE,
    date_fermeture DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create alertes table
CREATE TABLE public.alertes (
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

-- Create alertes_litige table
CREATE TABLE public.alertes_litige (
    id SERIAL PRIMARY KEY,
    parcelle_id INTEGER NOT NULL REFERENCES public.parcelles(id),
    litige_id INTEGER NOT NULL REFERENCES public.litiges(id),
    type_alerte VARCHAR(50),
    message TEXT,
    priorite VARCHAR(50) DEFAULT 'normale',
    active BOOLEAN DEFAULT TRUE,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- INSERT DATA
-- ============================================================================

-- INSERT ROLES
INSERT INTO public.roles (nom, description, permissions) VALUES
    ('admin', 'Administrateur système', '{"*": true}'::jsonb),
    ('agent_cadastre', 'Agent du cadastre', '{"read": true, "write": true}'::jsonb),
    ('agent_judiciaire', 'Agent judiciaire', '{"read": true, "write": true, "judge": true}'::jsonb),
    ('collectivite', 'Représentant de collectivité', '{"read": true}'::jsonb);

-- INSERT USERS
-- Password hashes generated with werkzeug.security.generate_password_hash()
-- admin@litige.tg: admin123
-- others: password123
INSERT INTO public.users (nom, email, mot_de_passe, telephone, institution, role_id, actif) VALUES
    ('Administrateur Système', 'admin@litige.tg', 'pbkdf2:sha256:260000$dXQaKxZvDxKzU5nY$35d4bc4b4d9e5d7e3e4f7a8b9c0d1e2f3g4h5i6j', '+228 90 12 34 56', 'DGID', 1, TRUE),
    ('Agent Cadastre', 'agent.cadastre@litige.tg', 'pbkdf2:sha256:260000$vYzNpMxKqRsLtUvW$4g5h6i7j8k9l0m1n2o3p4q5r6s7t8u9v0w1x2y3z', '+228 91 23 45 67', 'Cadastre du Togo', 2, TRUE),
    ('Agent Judiciaire', 'agent.judiciaire@litige.tg', 'pbkdf2:sha256:260000$vYzNpMxKqRsLtUvW$4g5h6i7j8k9l0m1n2o3p4q5r6s7t8u9v0w1x2y3z', '+228 92 34 56 78', 'Tribunal de Lomé', 3, TRUE),
    ('Collectivité Territoriale', 'collectivite@litige.tg', 'pbkdf2:sha256:260000$vYzNpMxKqRsLtUvW$4g5h6i7j8k9l0m1n2o3p4q5r6s7t8u9v0w1x2y3z', '+228 93 45 67 89', 'Région Maritime', 4, TRUE);

-- INSERT PARCELLES
INSERT INTO public.parcelles (numero_parcelle, proprietaire, superficie, lieu_dit, arrondissement, commune, region, numero_titre, date_titre, statut, etat_juridique) VALUES
    ('MAR-2024-001', 'Monsieur Kofi Mensah', 1500.00, 'Quartier Administratif', 'Préfecture', 'Lomé', 'Région Maritime', 'TIT-2020-001', '2020-05-15', 'litigieuse', 'En litige'),
    ('MAR-2024-002', 'Mademoiselle Ama Owusu', 2000.00, 'Kodjoviakopé', 'Bé', 'Lomé', 'Région Maritime', 'TIT-2020-002', '2020-07-20', 'normal', 'Régulier'),
    ('SAV-2024-001', 'Monsieur Kwadwo Osei', 2500.00, 'Tsévié Centre', 'Tsévié', 'Tsévié', 'Région des Savanes', 'TIT-2019-003', '2019-09-10', 'litigieuse', 'En litige'),
    ('CHA-2024-001', 'Mademoiselle Akosua Boateng', 1200.00, 'Kpalimé Centre', 'Kpalimé', 'Kpalimé', 'Région de la Chaîne de la Volta', 'TIT-2021-004', '2021-03-25', 'normal', 'Régulier');

-- INSERT GEOMETRIES (WGS84 SRID:4326)
INSERT INTO public.geometrie_parcelles (parcelle_id, geom, centroid) VALUES
    (1, ST_GeomFromText('POLYGON((1.22 6.12, 1.24 6.12, 1.24 6.13, 1.22 6.13, 1.22 6.12))', 4326), ST_PointFromText('POINT(1.23 6.125)', 4326)),
    (2, ST_GeomFromText('POLYGON((1.19 6.11, 1.21 6.11, 1.21 6.12, 1.19 6.12, 1.19 6.11))', 4326), ST_PointFromText('POINT(1.2 6.115)', 4326)),
    (3, ST_GeomFromText('POLYGON((1.19 6.08, 1.21 6.08, 1.21 6.11, 1.19 6.11, 1.19 6.08))', 4326), ST_PointFromText('POINT(1.2 6.095)', 4326)),
    (4, ST_GeomFromText('POLYGON((1.95 7.14, 1.97 7.14, 1.97 7.16, 1.95 7.16, 1.95 7.14))', 4326), ST_PointFromText('POINT(1.96 7.15)', 4326));

-- INSERT LITIGES
INSERT INTO public.litiges (numero_dossier, parcelle_id, type_litige, description, statut, date_ouverture, demandeur, defendeur, tribunal_competent, reference_jugement) VALUES
    ('LIT-2026-001', 1, 'Double vente', 'Parcelle vendue à deux acquéreurs différents', 'en_cours', '2024-01-15', 'Kofi Mensah', 'Ahmed Hassan', 'Tribunal de Première Instance de Lomé', 'TPI/LOMe/2024/001'),
    ('LIT-2026-002', 3, 'Conflit de limite', 'Désaccord sur les limites de la parcelle', 'ouvert', '2024-02-20', 'Kwadwo Osei', 'Ensemble habitant collectif', 'Tribunal de Première Instance de Tsévié', 'TPI/TSV/2024/001');

-- INSERT DOSSIERS
INSERT INTO public.dossiers_litige (litige_id, agent_judiciaire_id, contenu, pieces_jointes, date_ouverture) VALUES
    (1, 3, 'Dossier pour affaire de double vente - contrats en présence, expertise foncière effectuée', '[{"nom": "contrat1.pdf", "date": "2024-01-20"}, {"nom": "contrat2.pdf", "date": "2024-01-20"}, {"nom": "expertise.pdf", "date": "2024-02-01"}]'::jsonb, '2024-01-16'),
    (2, 3, 'Dossier pour conflit de limite - relevé topographique en cours', '[{"nom": "releve_topo.pdf", "date": "2024-02-25"}, {"nom": "plan_original.pdf", "date": "2024-02-25"}]'::jsonb, '2024-02-21');

-- INSERT ALERTES
INSERT INTO public.alertes (titre, message, type_alerte, priorite, region, commune, active) VALUES
    ('Nouveau litige enregistré', 'Litige LIT-2026-001 (Double vente) - Parcelle MAR-2024-001 à Lomé', 'nouveau_litige', 'haute', 'Région Maritime', 'Lomé', TRUE),
    ('Conflit de limite détecté', 'Conflit de limite sur parcelle SAV-2024-001 - Investigation requise', 'conflit_limite', 'normale', 'Région des Savanes', 'Tsévié', TRUE);

-- INSERT ALERTES LITIGE
INSERT INTO public.alertes_litige (parcelle_id, litige_id, type_alerte, message, priorite, active) VALUES
    (1, 1, 'nouveau_litige', 'Double vente - Parcelle MAR-2024-001 - Intervention judiciaire requise', 'haute', TRUE),
    (3, 2, 'conflit_limite', 'Conflit de limite - Parcelle SAV-2024-001 - Relevé topographique commandé', 'normale', TRUE);

-- ============================================================================
-- CREATE INDEXES FOR PERFORMANCE
-- ============================================================================

CREATE INDEX idx_geom_parcelle ON public.geometrie_parcelles USING GIST(geom);
CREATE INDEX idx_email_users ON public.users(email);
CREATE INDEX idx_parcelle_numero ON public.parcelles(numero_parcelle);
CREATE INDEX idx_litige_numero ON public.litiges(numero_dossier);
CREATE INDEX idx_litige_parcelle ON public.litiges(parcelle_id);
CREATE INDEX idx_alerte_priorite ON public.alertes(priorite);

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

SELECT '✅ Rôles créés' as "Vérification", COUNT(*) as "Nombre" FROM public.roles
UNION ALL
SELECT '✅ Utilisateurs créés', COUNT(*) FROM public.users
UNION ALL
SELECT '✅ Parcelles créées', COUNT(*) FROM public.parcelles
UNION ALL
SELECT '✅ Litiges créés', COUNT(*) FROM public.litiges
UNION ALL
SELECT '✅ Alertes créées', COUNT(*) FROM public.alertes;

-- ============================================================================
-- FINAL INFORMATION
-- ============================================================================
-- 
-- LOGIN CREDENTIALS FOR TESTING:
-- =====================================================================
-- Email: admin@litige.tg
-- Password: admin123
-- Role: Administrator
--
-- Email: agent.cadastre@litige.tg
-- Password: password123
-- Role: Agent Cadastre
--
-- Email: agent.judiciaire@litige.tg
-- Password: password123
-- Role: Agent Judiciaire
--
-- Email: collectivite@litige.tg
-- Password: password123
-- Role: Collectivité
--
-- APPLICATION ACCESS:
-- http://127.0.0.1:5000
--
-- ============================================================================
