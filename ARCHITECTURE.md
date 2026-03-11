# Architecture du Système d'Alerte SIG pour la Gestion des Litiges Fonciers

## Vue d'ensemble

Système web permettant de centraliser, visualiser et partager les informations relatives aux parcelles en litige au Togo. Connecté à une base de données géospatiale PostGIS.

## Structure du Projet

```
app/
├── __init__.py          # Initialisation Flask
├── models/
│   ├── user.py          # Modèles User, Role
│   ├── parcelle.py      # Modèles Parcelle, GeometrieParcelle
│   ├── litige.py        # Modèles Litige, DossierLitige, AlerteLitige
│   └── alerte.py        # Modèle Alerte générique
├── routes/
│   ├── auth.py          # Authentification/autorisation
│   ├── cadastre.py      # Routes Agent Cadastre
│   ├── litige.py        # Routes Agent Judiciaire
│   ├── collectivite.py  # Routes Collectivités
│   └── admin.py         # Routes Administrateur
├── templates/           # Fichiers HTML (Jinja2)
└── static/
    ├── js/             # JavaScript (Leaflet, GeoJSON)
    └── css/            # Feuilles de style
```

## Modèle de Données

### Utilisateurs
- **User**: id, email, mot_de_passe, nom, institution, role_id, actif
- **Role**: id, nom, description, permissions (JSON)

### Cadastre & Géométrie
- **Parcelle**: id, numero_parcelle, proprietaire, superficie, commune, region, statut, etat_juridique
- **GeometrieParcelle**: parcelle_id, geom (PostGIS Polygon), centroid (Point)

### Litiges & Alertes
- **Litige**: id, numero_dossier, parcelle_id, type_litige, description, statut, demandeur, defendeur
- **DossierLitige**: id, litige_id, agent_judiciaire_id, contenu, pieces_jointes
- **AlerteLitige**: id, parcelle_id, litige_id, type_alerte, message, priorite, active
- **Alerte**: id, titre, message, type_alerte, priorite, region, commune, active

## API Endpoints

### Authentication (`/api/auth`)
- `POST /login` - Connexion utilisateur
- `POST /register` - Créer un compte
- `GET /profile` - Profil utilisateur (JWT)
- `POST /logout` - Déconnexion

### Agent du Cadastre (`/api/cadastre`)
- `POST /authenticate` - Vérifier authentification
- `GET /carte` - Consulter carte cadastrale (GeoJSON)
- `GET /parcelle/<id>` - Détails parcelle
- `GET /rechercher?numero=&proprietaire=&commune=` - Rechercher
- `POST /operation` - Enregistrer opération (avec blocage auto)
- `GET /etat-juridique/<id>` - État juridique parcelle

### Agent Judiciaire (`/api/litige`)
- `POST /dossier` - Enregistrer dossier litige
- `PUT /dossier/<id>` - Mettre à jour statut litige
- `GET /dossier/<id>/parcelles` - Parcelles en contentieux
- `GET /alertes` - Consulter alertes actives
- `PUT /alerte/<id>` - Résoudre alerte

### Collectivité (`/api/collectivite`)
- `GET /carte-fonciere?region=&commune=` - Carte foncière
- `GET /parcelles-a-risque` - Parcelles litigieuses
- `GET /alertes-actives` - Alertes actives
- `GET /statistiques?region=` - Statistiques foncières

### Administrateur (`/api/admin`)
- `GET /utilisateurs` - Lister utilisateurs
- `PUT /utilisateur/<id>` - Modifier utilisateur
- `DELETE /utilisateur/<id>` - Supprimer utilisateur
- `GET /roles` - Lister rôles
- `GET /parametres-alertes` - Paramètres alertes
- `PUT /parametres-alertes` - Configurer alertes
- `GET /base-donnees/status` - Statut DB
- `POST /backup` - Créer sauvegarde

## Rôles et Permissions

### 1. Agent du Cadastre
- S'authentifier
- Consulter carte cadastrale
- Rechercher parcelle
- Consulter état juridique parcelle
- Enregistrer opération cadastrale
- Recevoir alerte de litige
- Blocage automatique opération (si alerte active)

### 2. Agent Judiciaire / Tribunal
- S'authentifier
- Enregistrer dossier de litige
- Mettre à jour statut litige
- Associer litige à parcelle
- Consulter parcelles en contentieux

### 3. Collectivité Territoriale
- Consulter carte foncière
- Consulter parcelles à risque
- Consulter alertes actives
- Voir statistiques

### 4. Administrateur Système
- Gérer utilisateurs
- Gérer rôles et permissions
- Paramétrer règles d'alerte
- Gérer base de données SIG

## Technologies Stack

**Backend**: Flask, SQLAlchemy, Flask-JWT
**Database**: PostgreSQL + PostGIS (extension géospatiale)
**Maps**: Leaflet.js, GeoServer (optionnel)
**Frontend**: HTML5, CSS3, JavaScript

## Installation & Configuration

### 1. Créer l'environnement
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### 2. Configurer PostgreSQL+PostGIS
```bash
# Créer database
createdb litige_foncier

# Activer PostGIS
psql litige_foncier -c "CREATE EXTENSION postgis;"

# Mettre à jour .env
DATABASE_URL=postgresql://user:password@localhost:5432/litige_foncier
```

### 3. Initialiser la BD
```bash
flask init-db
flask create-admin
```

### 4. Lancer l'application
```bash
python run.py
# Ou: flask run
```

L'app sera disponible sur `http://localhost:5000`

## Flux Métier Clé

### Enregistrement d'un Litige
1. Agent judiciaire crée dossier litige → Litige créé
2. Parcelle passe à statut "litigieuse"
3. Alerte créée automatiquement (priorité haute)
4. Agent cadastre reçoit alerte
5. Opérations cadastrales bloquées sur parcelle

### Résolution de Litige
1. Agent judiciaire met à jour statut "résolu"
2. Alerte désactivée
3. Si aucun autre litige actif → Parcelle restaurée "normal"
4. Agent cadastre peut relancer opérations

## Sécurité

- ✅ JWT pour authentification sans session
- ✅ Rôles-Permissions granulaires
- ✅ Chiffrage mot de passe (werkzeug)
- ✅ CORS configuré
- ✅ Validation données côté serveur

## Évolutions Futures

1. **Frontend**
   - Dashboard interactif Leaflet/GeoServer
   - Export rapports (PDF, GeoJSON)
   - Notifications temps réel (WebSocket)
   - Mobile responsive

2. **Backend**
   - Audit logging
   - Cache Redis
   - Worker Celery pour tâches async
   - API GraphQL alternative

3. **SIG**
   - Intégration WMS/WFS GeoServer
   - Analyse spatiale PostGIS avancée
   - Heatmaps des zones à risque
   - Historique modifications parcelles

4. **Fonctionnalités**
   - OCR documents scanalisés
   - Chatbot assistance utilisateurs
   - Intégration SMS/Email alertes
   - API mobile iOS/Android
