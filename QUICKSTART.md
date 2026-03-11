# 🚀 Guide de Démarrage Rapide

## Système d'Alerte SIG pour la Gestion des Litiges Fonciers

**Projet Master Géomatique - Université de Lomé**
**Région Maritime, Togo**

---

## 📋 Prérequis

- **Python 3.8+**
- **PostgreSQL 12+** avec extension PostGIS
- **Git** (optionnel)
- **Postman** pour tester l'API (optionnel)

---

## 1️⃣ Installation de l'Environnement

### Sur Ubuntu/Debian:

```bash
# Installer Python et dépendances système
sudo apt-get update
sudo apt-get install python3-pip python3-venv postgresql postgresql-contrib postgis

# Activer PostGIS
sudo service postgresql start
sudo -u postgres psql -c "CREATE EXTENSION postgis;" postgres
```

### Sur macOS (avec Homebrew):

```bash
# Installer PostgreSQL + PostGIS
brew install postgresql postgis
brew services start postgresql

# Activer PostGIS
createdb postgres
psql postgres -c "CREATE EXTENSION postgis;"
```

---

## 2️⃣ Configuration du Projet

```bash
# 1. Accéder au répertoire du projet
cd /home/lawson/Documents/PROJETGEOMATIQUE

# 2. Créer un environnement virtuel
python3 -m venv venv

# 3. Activer l'environnement
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# 4. Installer les dépendances
pip install -r requirements.txt

# 5. Créer le fichier .env
cp .env.example .env

# 6. Éditer .env avec vos paramètres
# DATABASE_URL=postgresql://user:password@localhost:5432/litige_foncier
# SECRET_KEY=votre_clé_secrète
```

---

## 3️⃣ Initialisation de la Base de Données

### Créer la base de données PostgreSQL:

```bash
# Créer la base de données
createdb litige_foncier

# Ajouter l'extension PostGIS
psql litige_foncier -c "CREATE EXTENSION postgis;"

# Vérifier
psql litige_foncier -c "SELECT version();"
```

### Initialiser les tables Flask:

```bash
# Depuis le répertoire du projet avec l'environnement activé
flask init-db
```

### Créer un utilisateur administrateur:

```bash
flask create-admin

# Répondre aux questions:
# Email: admin@litige.tg
# Nom: Administrateur Système
# Mot de passe: (entrer un mot de passe sécurisé)
```

### (Optionnel) Charger les données de test:

```bash
python seed_db.py

# Sortie:
# ✅ Base de données initialisée avec succès !
# 📊 Données créées:
#    - 4 utilisateurs
#    - 4 parcelles
#    - 2 litiges
#    - 2 alertes litige + 2 alertes génériques
```

---

## 4️⃣ Lancer l'Application

```bash
# Mode développement (avec rechargement automatique)
python run.py

# Ou avec flask
flask run

# Ou en production (Gunicorn)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

**L'application est maintenant disponible sur:** `http://localhost:5000`

---

## 5️⃣ Tester l'API

### Avec cURL:

```bash
# 1. Authentification
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@litige.tg",
    "mot_de_passe": "admin123"
  }'

# Copier le token reçu

# 2. Consulter carte cadastrale
curl -H "Authorization: Bearer TOKEN_COPIÉ" \
  http://localhost:5000/api/cadastre/carte

# 3. Lister utilisateurs (admin uniquement)
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:5000/api/admin/utilisateurs
```

### Avec Postman:

1. **Importer la collection:**
   - Ouvrir Postman
   - Click "Import" → Choisir `Postman_Collection.json`
   
2. **Définir le token:**
   - Exécuter "Auth → Login"
   - Copier le token reçu
   - Aller à "Variables" et coller dans `token`
   
3. **Tester les endpoints:**
   - Essayer "Agent Cadastre → Consulter Carte"
   - Essayer "Agent Judiciaire → Enregistrer Dossier Litige"
   - Essayer "Admin → Lister Utilisateurs"

---

## 📚 Structure du Projet

```
PROJETGEOMATIQUE/
├── app/
│   ├── models/
│   │   ├── user.py              # Utilisateurs & Rôles
│   │   ├── parcelle.py          # Parcelles & Géométrie SIG
│   │   ├── litige.py            # Litiges & Alertes
│   │   └── alerte.py            # Alertes génériques
│   ├── routes/
│   │   ├── auth.py              # API Authentification
│   │   ├── cadastre.py          # API Agent Cadastre
│   │   ├── litige.py            # API Agent Judiciaire
│   │   ├── collectivite.py      # API Collectivité
│   │   └── admin.py             # API Administration
│   ├── templates/
│   │   └── index.html           # Dashboard interactif
│   └── static/
│       ├── css/style.css        # Styles
│       └── js/                  # Scripts JavaScript
├── run.py                       # Point d'entrée
├── config.py                    # Configuration
├── requirements.txt             # Dépendances
├── seed_db.py                   # Données test
├── README.md                    # Documentation complète
├── ARCHITECTURE.md              # Architecture technique
└── Postman_Collection.json      # Tests API
```

---

## 🔐 Identifiants de Test (si données chargées)

```
Admin:
  Email: admin@litige.tg
  Password: admin123

Agent Cadastre:
  Email: agent.cadastre@litige.tg
  Password: password123

Agent Judiciaire:
  Email: agent.judiciaire@litige.tg
  Password: password123

Collectivité:
  Email: collectivite@litige.tg
  Password: password123
```

---

## 🔧 Commandes Utiles

```bash
# Activer l'environnement virtuel
source venv/bin/activate

# Exécuter les migrations database
flask db upgrade

# Créer une console Python avec contexte Flask
flask shell

# Lancer les tests
pytest

# Afficher les logs
tail -f logs/app.log

# Arrêter le serveur
Ctrl + C
```

---

## 🗂️ Workflow Métier Clé

### Enregistrement d'un Litige:

```
1. Agent Judiciaire crée dossier litige
2. Parcelle → statut "litigieuse"
3. Alerte créée (priorité haute)
4. Agent Cadastre voit l'alerte
5. Opérations cadastrales bloquées
```

### Résolution de Litige:

```
1. Agent Judiciaire → "Marquer comme résolu"
2. Alerte → désactivée
3. Pas d'autres litiges actifs? → Parcelle "normale"
4. Agent Cadastre peut relancer opérations
```

---

## 🐛 Troubleshooting

### Erreur: "DATABASE_URL not set"
```bash
# Solution:
cp .env.example .env
# Éditer .env avec vos paramètres
```

### Erreur: "Address already in use :5000"
```bash
# Utiliser un autre port:
python run.py --port 8000
# ou tuer le processus existant:
lsof -ti:5000 | xargs kill -9
```

### Erreur: PostGIS extension not found
```bash
# Ubuntu:
sudo apt-get install postgresql-contrib
# macOS:
brew install postgis
```

### PostgreSQL ne démarre pas
```bash
# Ubuntu:
sudo service postgresql restart
# macOS:
brew services restart postgresql
```

---

## 📖 Documentation Complète

- **[README.md](README.md)** - Guide complet du projet
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Architecture technique détaillée
- **API REST:** Voir endpoints dans [ARCHITECTURE.md](ARCHITECTURE.md#api-endpoints)

---

## 🎯 Prochaines Étapes

- [ ] Configurer frontend HTML/CSS/Leaflet
- [ ] Intégrer GeoServer pour WMS/WFS
- [ ] Ajouter websockets pour notifications temps réel
- [ ] Déployer sur serveur production
- [ ] Configurer CI/CD (GitHub Actions)
- [ ] Ajouter logging et monitoring

---

## 📞 Support

Pour les questions ou problèmes:
1. Consulter [ARCHITECTURE.md](ARCHITECTURE.md)
2. Vérifier les logs: `logs/app.log`
3. Tester avec Postman Collection

---

## 📄 Licence

Projet académique - Master Géomatique Université de Lomé

**Créé:** Février 2026
**Région:** Maritime, Togo
