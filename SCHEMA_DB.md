# Schéma Base de Données - Système d'Alerte SIG

## Vue d'ensemble

```
┌─────────────────────────────────────────────────────────────┐
│                  BASE DE DONNÉES LITIGE_FONCIER            │
│                   PostgreSQL + PostGIS                      │
└─────────────────────────────────────────────────────────────┘

┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│    ROLES     │     │    USERS     │     │   PARCELLE   │
│──────────────│     │──────────────│     │──────────────│
│ id (PK)      │────▶│ id (PK)      │────▶│ id (PK)      │
│ nom          │     │ email        │     │ numero       │
│ description  │     │ nom          │     │ proprietaire │
│ permissions  │     │ mot_de_passe │     │ superficie   │
└──────────────┘     │ institution  │     │ statut       │
                     │ role_id (FK) │     │ etat_juridique
                     │ actif        │     │ region       │
                     │ date_creation│     └──────────────┘
                     │ date_modif   │              │
                     └──────────────┘              │
                                                   │
                         ┌──────────────────────────┘
                         │
                         ▼
                    ┌──────────────────────┐
                    │ GEOMETRIE_PARCELLE   │
                    │──────────────────────│
                    │ id (PK)              │
                    │ parcelle_id (FK)     │
                    │ geom (Polygon)       │◀── PostGIS
                    │ centroid (Point)     │
                    └──────────────────────┘


┌──────────────┐     ┌──────────────────┐     ┌──────────────────┐
│   LITIGE     │────▶│ DOSSIER_LITIGE   │     │ ALERTE_LITIGE    │
│──────────────│     │──────────────────│     │──────────────────│
│ id (PK)      │     │ id (PK)          │     │ id (PK)          │
│ numero_dos.. │     │ litige_id (FK)   │     │ parcelle_id (FK) │
│ parcelle_id  │────▶│ agent_judic_id   │────▶│ litige_id (FK)   │
│ type_litige  │     │ contenu          │     │ type_alerte      │
│ description  │     │ pieces_jointes   │     │ message          │
│ statut       │     │ date_ouverture   │     │ priorite         │
│ demandeur    │     │ date_fermeture   │     │ active           │
│ defendeur    │     └──────────────────┘     │ date_creation    │
│ tribunal_... │                              │ date_resolution  │
└──────────────┘                              └──────────────────┘


┌──────────────┐
│   ALERTES    │
│──────────────│
│ id (PK)      │
│ titre        │
│ message      │
│ type_alerte  │
│ priorite     │
│ region       │
│ commune      │
│ active       │
│ date_creation│
│ date_resol.. │
└──────────────┘
```

---

## Détail des Tables

### 1. ROLES
```sql
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(50) UNIQUE NOT NULL,
    description VARCHAR(255),
    permissions JSON DEFAULT '{}',
    
    -- Valeurs possibles pour 'nom':
    -- - 'admin'
    -- - 'agent_cadastre'
    -- - 'agent_judiciaire'
    -- - 'collectivite'
);

-- Exemples de données:
INSERT INTO roles VALUES
  (1, 'admin', 'Administrateur système', '{"all": true}'),
  (2, 'agent_cadastre', 'Agent du cadastre', '{"consulter_carte": true, "enregistrer_operation": true}'),
  (3, 'agent_judiciaire', 'Agent judiciaire / Tribunal', '{"enregistrer_dossier": true}'),
  (4, 'collectivite', 'Collectivité territoriale', '{"consulter_carte_fonciere": true}');
```

### 2. USERS
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    mot_de_passe VARCHAR(255) NOT NULL,  -- Hasché avec werkzeug
    telephone VARCHAR(20),
    institution VARCHAR(200),             -- Cadastre, Tribunal, Mairie, etc.
    role_id INTEGER NOT NULL,
    actif BOOLEAN DEFAULT true,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (role_id) REFERENCES roles(id)
);

-- Index pour optimiser recherches:
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role_id ON users(role_id);
```

### 3. PARCELLES
```sql
CREATE TABLE parcelles (
    id SERIAL PRIMARY KEY,
    numero_parcelle VARCHAR(50) UNIQUE NOT NULL,
    proprietaire VARCHAR(200),
    superficie FLOAT,                     -- en m²
    lieu_dit VARCHAR(200),
    arrondissement VARCHAR(100),
    commune VARCHAR(100),
    region VARCHAR(100) DEFAULT 'Maritime',
    numero_titre VARCHAR(50),
    date_titre DATE,
    statut VARCHAR(50) DEFAULT 'normal',  -- normal, litigieuse, bloquee
    etat_juridique VARCHAR(200),          -- foncier, domanial, collectif
    observations TEXT,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Index pour recherches:
    CREATE INDEX idx_parcelles_numero ON parcelles(numero_parcelle);
    CREATE INDEX idx_parcelles_statut ON parcelles(statut);
    CREATE INDEX idx_parcelles_region ON parcelles(region);
    CREATE INDEX idx_parcelles_commune ON parcelles(commune);
);
```

### 4. GEOMETRIE_PARCELLE (PostGIS)
```sql
CREATE TABLE geometrie_parcelle (
    id SERIAL PRIMARY KEY,
    parcelle_id INTEGER NOT NULL UNIQUE,
    geom GEOMETRY(Polygon, 4326),        -- WGS84
    centroid GEOMETRY(Point, 4326),      -- Centre de gravité
    
    FOREIGN KEY (parcelle_id) REFERENCES parcelles(id) ON DELETE CASCADE
);

-- Créer index spatial:
CREATE INDEX idx_geom_parcelle ON geometrie_parcelle USING GIST(geom);
CREATE INDEX idx_centroid ON geometrie_parcelle USING GIST(centroid);
```

### 5. LITIGES
```sql
CREATE TABLE litiges (
    id SERIAL PRIMARY KEY,
    numero_dossier VARCHAR(50) UNIQUE NOT NULL,
    parcelle_id INTEGER NOT NULL,
    type_litige VARCHAR(100),            -- double_vente, conflit_limite, titre_multiple
    description TEXT NOT NULL,
    statut VARCHAR(50) DEFAULT 'ouvert', -- ouvert, en_cours, resolu, suspendu, rejet
    date_enregistrement TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_resolution TIMESTAMP,
    demandeur VARCHAR(200),
    defendeur VARCHAR(200),
    tribunal_competent VARCHAR(200),
    reference_jugement VARCHAR(100),
    
    FOREIGN KEY (parcelle_id) REFERENCES parcelles(id) ON DELETE CASCADE,
    
    CREATE INDEX idx_litiges_numero ON litiges(numero_dossier);
    CREATE INDEX idx_litiges_parcelle ON litiges(parcelle_id);
    CREATE INDEX idx_litiges_statut ON litiges(statut);
);
```

### 6. DOSSIER_LITIGE
```sql
CREATE TABLE dossier_litige (
    id SERIAL PRIMARY KEY,
    litige_id INTEGER NOT NULL UNIQUE,
    agent_judiciaire_id INTEGER,
    contenu TEXT,
    pieces_jointes JSON DEFAULT '[]',    -- Chemins fichiers
    date_ouverture TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_fermeture TIMESTAMP,
    
    FOREIGN KEY (litige_id) REFERENCES litiges(id) ON DELETE CASCADE,
    FOREIGN KEY (agent_judiciaire_id) REFERENCES users(id)
);
```

### 7. ALERTES_LITIGE
```sql
CREATE TABLE alertes_litige (
    id SERIAL PRIMARY KEY,
    parcelle_id INTEGER NOT NULL,
    litige_id INTEGER NOT NULL,
    type_alerte VARCHAR(100),            -- blocage_operation, nouvelle_action, etc.
    message TEXT,
    priorite VARCHAR(20) DEFAULT 'normal', -- haute, normale, basse
    active BOOLEAN DEFAULT true,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_resolution TIMESTAMP,
    
    FOREIGN KEY (parcelle_id) REFERENCES parcelles(id) ON DELETE CASCADE,
    FOREIGN KEY (litige_id) REFERENCES litiges(id) ON DELETE CASCADE,
    
    CREATE INDEX idx_alertes_parcelle ON alertes_litige(parcelle_id);
    CREATE INDEX idx_alertes_active ON alertes_litige(active);
    CREATE INDEX idx_alertes_priorite ON alertes_litige(priorite);
);
```

### 8. ALERTES (Génériques)
```sql
CREATE TABLE alertes (
    id SERIAL PRIMARY KEY,
    titre VARCHAR(200) NOT NULL,
    message TEXT,
    type_alerte VARCHAR(100),            -- risque_foncier, conflit_limite, etc.
    priorite VARCHAR(20) DEFAULT 'normal', -- haute, normale, basse
    region VARCHAR(100),
    commune VARCHAR(100),
    active BOOLEAN DEFAULT true,
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_resolution TIMESTAMP,
    
    CREATE INDEX idx_alertes_region ON alertes(region);
    CREATE INDEX idx_alertes_commune ON alertes(commune);
    CREATE INDEX idx_alertes_active ON alertes(active);
);
```

---

## Relations et Contraintes

### Relations Many-to-One:

```
USER.role_id → ROLE.id
PARCELLE.id ← DOSSIER_LITIGE.parcelle_id (dans LITIGE)
LITIGE.parcelle_id → PARCELLE.id
LITIGE.id ← DOSSIER_LITIGE.litige_id
LITIGE.id ← ALERTES_LITIGE.litige_id
PARCELLE.id ← ALERTES_LITIGE.parcelle_id
USER.id ← DOSSIER_LITIGE.agent_judiciaire_id
GEOMETRIE_PARCELLE.parcelle_id → PARCELLE.id (1-to-1)
```

### Cascade Delete:

- PARCELLE supprimée → LITIGE supprimés → DOSSIER_LITIGE supprimés
- LITIGE supprimé → ALERTES_LITIGE supprimées
- PARCELLE supprimée → GEOMETRIE_PARCELLE supprimée

---

## Exemples de Requêtes Courantes

### Parcelles avec litiges actifs:
```sql
SELECT DISTINCT p.*, l.numero_dossier, l.statut
FROM parcelles p
JOIN litiges l ON p.id = l.parcelle_id
WHERE l.statut IN ('ouvert', 'en_cours')
ORDER BY p.region, p.commune;
```

### Alertes actives haute priorité:
```sql
SELECT a.*, p.numero_parcelle, p.proprietaire
FROM alertes_litige a
JOIN parcelles p ON a.parcelle_id = p.id
WHERE a.active = true AND a.priorite = 'haute'
ORDER BY a.date_creation DESC;
```

### Statistiques par région:
```sql
SELECT 
  p.region,
  COUNT(*) as parcelles_total,
  COUNT(CASE WHEN p.statut = 'litigieuse' THEN 1 END) as litiges,
  ROUND(100.0 * COUNT(CASE WHEN p.statut = 'litigieuse' THEN 1 END) / COUNT(*), 2) as pourcentage,
  SUM(p.superficie) / 10000.0 as superficie_hectares
FROM parcelles p
GROUP BY p.region
ORDER BY pourcentage DESC;
```

### Blocages de parcelles (litiges non résolus):
```sql
SELECT p.*, l.numero_dossier, l.type_litige, l.date_enregistrement
FROM parcelles p
JOIN litiges l ON p.id = l.parcelle_id
WHERE p.statut = 'litigieuse' AND l.statut != 'resolu'
ORDER BY l.date_enregistrement DESC;
```

### Dossiers de litige par tribunal:
```sql
SELECT 
  l.tribunal_competent,
  COUNT(*) as dossiers,
  COUNT(CASE WHEN l.statut = 'resolu' THEN 1 END) as resolus,
  COUNT(CASE WHEN l.statut IN ('ouvert', 'en_cours') THEN 1 END) as en_cours
FROM litiges l
GROUP BY l.tribunal_competent
ORDER BY en_cours DESC;
```

---

## Performance & Optimisation

### Index créés:
- Tous les Foreign Keys
- `parcelles.numero_parcelle` (recherche rapide)
- `parcelles.statut` (filtrage rapide)
- `users.email` (authentification)
- Géométries PostGIS (GIST)

### Requêtes optimisées:
- Utiliser JOIN au lieu de requêtes multiples
- Filtrer par statut/région pour limiter résultats
- Préférer les index spatiaux pour géométrie

---

## Sauvegarde & Restauration

```bash
# Sauvegarde:
pg_dump -U user litige_foncier > backup.sql

# Avec données géospatiales:
pg_dump -U user --format=custom litige_foncier > backup.dump

# Restauration:
psql -U user litige_foncier < backup.sql

# Ou:
pg_restore -U user -d litige_foncier backup.dump
```

---

## Sécurité

✅ **Mesures implémentées:**
- Hash sécurisé des mots de passe (werkzeug)
- Contraintes FK pour intégrité référentielle
- Index pour performance
- Triggers potentiels pour audit (à ajouter)

⚠️ **À implémenter:**
- Audit logging de toutes les modifications
- Chiffrage des données sensibles
- Masquage des données (PII) en logs
- Sauvegarde automatique quotidienne

---

## Diagramme MCD (Merise)

```
ROLE (1) ------- (N) USER
                    |
                    | (1)
                    |
                (N) |
            PARCELLE |
                |   |
                |   |
            (N) |   | (1)
                |   └── GEOMETRIE_PARCELLE (1)
                |
            LITIGE
                |
            (N) | (1)
                ├── DOSSIER_LITIGE
                │
                └── ALERTES_LITIGE
                    |
                PARCELLE

ALERTES (entité indépendante pour alertes génériques)
```

---

**Créé:** Février 2026
**Version:** 1.0
**Système:** PostgreSQL 12+ avec PostGIS
