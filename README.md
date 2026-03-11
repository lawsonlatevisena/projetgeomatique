# Système d'Alerte SIG pour la Gestion des Litiges Fonciers

📍 **Projet Master Géomatique - Université de Lomé**

## Contexte

Les litiges fonciers constituent un problème majeur dans la région maritime du Togo. Ce système d'alerte web SIG centralise, visualise et partage les informations relatives aux parcelles en litige, permettant :

✅ Blocage automatique des opérations cadastrales sur parcelles litigieuses
✅ Coordination entre cadastre, tribunaux et collectivités
✅ Réduction des conflits liés à double vente ou titres multiples
✅ Traçabilité complète des dossiers

## Quick Start

### 1. Installation

```bash
# Cloner le projet
cd /home/lawson/Documents/PROJETGEOMATIQUE

# Créer environnement virtuel
python3 -m venv venv
source venv/bin/activate

# Installer dépendances
pip install -r requirements.txt
```

### 2. Configuration Base de Données

```bash
# Installer PostgreSQL + PostGIS (Ubuntu/Debian)
sudo apt-get install postgresql postgresql-contrib postgis

# Créer base de données
sudo -u postgres createdb litige_foncier
sudo -u postgres psql litige_foncier -c "CREATE EXTENSION postgis;"

# Configurer .env
cp .env.example .env
# Éditer: DATABASE_URL=postgresql://user:password@localhost:5432/litige_foncier
```

### 3. Initialiser l'Application

```bash
# Activer venv si nécessaire
source venv/bin/activate

# Initialiser BD et créer rôles
flask init-db

# Créer administrateur
flask create-admin
# Email: admin@litige.tg
# Nom: Administrateur
# Mot de passe: (à définir)
```

### 4. Lancer le Serveur

```bash
python run.py
```

L'application sera accessible sur: **http://localhost:5000**

## Organisation du Projet

```
.
├── app/                      # Code application Flask
│   ├── models/              # Modèles de données (User, Parcelle, Litige)
│   ├── routes/              # Routes API par acteur
│   ├── templates/           # Fichiers HTML
│   └── static/              # JS, CSS, assets
├── run.py                   # Point d'entrée
├── config.py                # Configuration
├── requirements.txt         # Dépendances Python
├── .env.example             # Variables d'environnement
└── ARCHITECTURE.md          # Documentation technique détaillée
```

## Cas d'Utilisation par Acteur

### 🗺️ Agent du Cadastre
- S'authentifier au système
- Consulter la carte cadastrale interactive
- Rechercher une parcelle (numéro, propriétaire, commune)
- Consulter l'état juridique d'une parcelle
- Enregistrer une opération cadastrale
- Recevoir alertes de litige
- **Blocage automatique** si parcelle litigieuse

**Endpoints clés:**
```
GET  /api/cadastre/carte
GET  /api/cadastre/parcelle/<id>
GET  /api/cadastre/rechercher?numero=...
POST /api/cadastre/operation
GET  /api/cadastre/etat-juridique/<id>
```

### ⚖️ Agent Judiciaire / Tribunal
- S'authentifier
- **Enregistrer dossier de litige** (crée alerte auto)
- Mettre à jour statut du litige (ouvert → résolu)
- Associer litige à parcelle
- Consulter parcelles en contentieux
- Gérer alertes liées au litige

**Endpoints clés:**
```
POST /api/litige/dossier
PUT  /api/litige/dossier/<id>
GET  /api/litige/dossier/<id>/parcelles
GET  /api/litige/alertes
PUT  /api/litige/alerte/<id>
```

### 🏛️ Collectivité Territoriale
- Consulter carte foncière (région/commune)
- Consulter parcelles à risque
- Consulter alertes actives
- Visualiser statistiques foncières

**Endpoints clés:**
```
GET /api/collectivite/carte-fonciere?region=Maritime
GET /api/collectivite/parcelles-a-risque
GET /api/collectivite/alertes-actives
GET /api/collectivite/statistiques?region=Maritime
```

### 👨‍💼 Administrateur Système
- Gérer utilisateurs et rôles
- Paramétrer règles d'alerte
- Accéder statistiques/monitoring BD
- Gérer sauvegardes

**Endpoints clés:**
```
GET    /api/admin/utilisateurs
PUT    /api/admin/utilisateur/<id>
GET    /api/admin/parametres-alertes
PUT    /api/admin/parametres-alertes
GET    /api/admin/base-donnees/status
POST   /api/admin/backup
```

## Exemples d'Utilisation

### 1. S'authentifier

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"agent@cadastre.tg", "mot_de_passe":"password"}'
```

**Réponse:**
```json
{
  "message": "Connexion réussie",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "nom": "Agent Cadastre",
    "email": "agent@cadastre.tg",
    "role": "agent_cadastre"
  }
}
```

### 2. Consulter Carte Cadastrale

```bash
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:5000/api/cadastre/carte
```

**Réponse:** GeoJSON FeatureCollection avec toutes les parcelles

### 3. Enregistrer Litige

```bash
curl -X POST http://localhost:5000/api/litige/dossier \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "numero_dossier": "LIT-2026-001",
    "parcelle_id": 42,
    "type_litige": "double_vente",
    "description": "Deux titres émis pour même parcelle",
    "demandeur": "Jean Dupont",
    "defendeur": "Marie Martin",
    "tribunal_competent": "Tribunal de 1ère Instance de Lomé"
  }'
```

**Effet automatique:**
- ✅ Litige créé
- ✅ Parcelle → statut "litigieuse"
- ✅ Alerte créée (priorité haute)
- ✅ Agent cadastre reçoit notification
- ✅ Opérations cadastrales bloquées

## Modèle de Données Clé

### Parcelle
```
- id (PK)
- numero_parcelle (unique)
- proprietaire
- superficie (m²)
- lieu_dit, arrondissement, commune, region
- numero_titre, date_titre
- statut: "normal" | "litigieuse" | "bloquee"
- etat_juridique: "foncier" | "domanial" | "collectif"
- geometrie PostGIS (polygon + centroid)
```

### Litige
```
- id (PK)
- numero_dossier (unique)
- parcelle_id (FK)
- type_litige: "double_vente" | "conflit_limite" | "titre_multiple"
- description, statut
- demandeur, defendeur, tribunal_competent
```

### AlerteLitige
```
- id (PK)
- parcelle_id, litige_id
- type_alerte, message
- priorite: "basse" | "normale" | "haute"
- active: boolean
- date_creation, date_resolution
```

## Tests de l'API

### Avec Postman
1. Importer les endpoints dans Postman
2. Créer collection avec authentification Bearer Token
3. Tester chaque endpoint par rôle

### Avec curl
```bash
# Enregistrer token
TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@litige.tg","mot_de_passe":"password"}' \
  | jq -r '.access_token')

# Utiliser token
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/admin/utilisateurs
```

## Déploiement Production

### Utiliser Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

### Avec Docker
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "run:app"]
```

## Développement Frontend

Le frontend HTML/CSS/JS sera créé dans `app/templates/` et `app/static/`

### Dépendances Frontend à ajouter:
- **Leaflet.js** - Cartes interactives
- **Bootstrap 5** - Responsive design
- **Chart.js** - Graphiques statistiques
- **Axios** - Requêtes AJAX

```html
<script src="https://cdn.jsdelivr.net/npm/leaflet@1.9.4/dist/leaflet.js"></script>
<script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
```

## Troubleshooting

### Erreur: "DATABASE_URL not found"
```bash
cp .env.example .env
# Éditer .env avec vos paramètres
```

### Erreur: PostGIS extension not available
```bash
# Ubuntu/Debian
sudo apt-get install postgresql-contrib
```

### Erreur: "Address already in use :5000"
```bash
# Changer le port
python run.py --port 5001
```

## Roadmap

- [x] Architecture Flask et modèles
- [x] Authentification JWT
- [x] Routes API par acteur
- [ ] Frontend HTML/CSS/Leaflet
- [ ] Intégration GeoServer
- [ ] Système d'alertes temps réel (WebSocket)
- [ ] Export rapports PDF
- [ ] Mobile app (React Native)
- [ ] Dashboard analytics
- [ ] OCR documents

## License

Projet académique - Master Géomatique Université de Lomé

## Support

📧 Email: [À définir]
📞 Téléphone: [À définir]

---

**Créé:** février 2026
**Région:** Maritime, Togo
**Université:** Université de Lomé
