# 🚀 GUIDE DE DÉMARRAGE - Système d'Alerte SIG

## État Actuel du Projet

✅ **Complété:**
- Architecture Flask créée
- Modèles de données configurés
- Routes API implémentées
- Environnement Python configuré
- PostgreSQL + PostGIS installés
- Base de données créée
- Utilisateur admin créé

## 📋 Checklist de Démarrage

### Étape 1: Terminal 1 - Démarrer PostgreSQL
```bash
sudo service postgresql start
```

### Étape 2: Terminal 1 - Vérifier PostgreSQL
```bash
sudo -u postgres psql litige_foncier -c "SELECT 1;"
# Devrait afficher: 1
```

### Étape 3: Terminal 2 - Charger les données de test
```bash
cd /home/lawson/Documents/PROJETGEOMATIQUE
source venv/bin/activate
python load_test_data.py
```

**Sortie attendue:**
```
📦 Chargement des données de test...
👥 Créer utilisateurs...
   ✅ 3 utilisateurs créés
🏘️  Créer parcelles...
   ✅ 4 parcelles créées
⚖️  Créer litiges...
   ✅ 2 litiges créés
🚨 Créer alertes...
   ✅ 2 alertes créées

✅ Données de test chargées avec succès !
```

### Étape 4: Terminal 3 - Lancer le serveur Flask
```bash
cd /home/lawson/Documents/PROJETGEOMATIQUE
source venv/bin/activate
python run.py
```

**Sortie attendue:**
```
 * Serving Flask app 'run'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

## 🧪 Tester l'API

### Option A: Avec cURL

**1. S'authentifier:**
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@litige.tg","mot_de_passe":"admin123"}'
```

**Réponse:**
```json
{
  "message": "Connexion réussie",
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "id": 1,
    "nom": "Administrateur Système",
    "email": "admin@litige.tg",
    "role": "admin"
  }
}
```

**2. Copier le token et tester une route**
```bash
export TOKEN="eyJ0eXAiOiJKV1QiLCJhbGc..."

curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:5000/api/admin/utilisateurs
```

### Option B: Avec Postman

1. Importer `Postman_Collection.json`
2. Aller à "Variables" et ajouter le token reçu
3. Exécuter les endpoints

## 🔐 Identifiants de Test

### Admin
- Email: `admin@litige.tg`
- Mot de passe: `admin123`

### Agent Cadastre
- Email: `agent.cadastre@litige.tg`
- Mot de passe: `password123`

### Agent Judiciaire
- Email: `agent.judiciaire@litige.tg`
- Mot de passe: `password123`

### Collectivité
- Email: `collectivite@litige.tg`
- Mot de passe: `password123`

## 📊 Données de Test Créées

### Utilisateurs (4)
- 1 Admin
- 1 Agent Cadastre
- 1 Agent Judiciaire
- 1 Collectivité

### Parcelles (4)
- MAR-2024-001: Normal
- MAR-2024-002: Litigieuse (double vente)
- MAR-2024-003: Litigieuse (conflit limite)
- MAR-2024-004: Normal

### Litiges (2)
- LIT-2026-001: Double vente
- LIT-2026-002: Conflit limite

### Alertes (2)
- Alerte haute: Double vente
- Alerte normale: Conflit limite

## 🧪 Endpoints à Tester

### Authentification
- POST `/api/auth/login` - Se connecter ✅
- GET `/api/auth/profile` - Profil utilisateur ✅
- POST `/api/auth/register` - Créer compte
- POST `/api/auth/logout` - Déconnexion

### Agent Cadastre
- GET `/api/cadastre/carte` - Consulter carte ✅
- GET `/api/cadastre/parcelle/<id>` - Détails parcelle ✅
- GET `/api/cadastre/rechercher` - Rechercher ✅
- POST `/api/cadastre/operation` - Enregistrer opération
- GET `/api/cadastre/etat-juridique/<id>` - État juridique

### Agent Judiciaire
- POST `/api/litige/dossier` - Enregistrer litige
- PUT `/api/litige/dossier/<id>` - Mettre à jour litige
- GET `/api/litige/alertes` - Consulter alertes ✅
- GET `/api/litige/dossier/<id>/parcelles` - Parcelles contentieuses

### Collectivité
- GET `/api/collectivite/carte-fonciere` - Carte foncière ✅
- GET `/api/collectivite/parcelles-a-risque` - Parcelles à risque ✅
- GET `/api/collectivite/alertes-actives` - Alertes actives ✅
- GET `/api/collectivite/statistiques` - Statistiques

### Admin
- GET `/api/admin/utilisateurs` - Lister utilisateurs ✅
- GET `/api/admin/base-donnees/status` - Status DB ✅
- GET `/api/admin/parametres-alertes` - Paramètres alertes
- GET `/api/admin/roles` - Lister rôles

## 🐛 Troubleshooting

### "PostgreSQL Connection Refused"
```bash
sudo service postgresql start
sudo -u postgres psql litige_foncier -c "SELECT 1;"
```

### "Port 5000 already in use"
```bash
lsof -i :5000
kill -9 <PID>
```

### "ModuleNotFoundError"
```bash
cd /home/lawson/Documents/PROJETGEOMATIQUE
source venv/bin/activate
pip install -r requirements.txt
```

### "psycopg2 error"
```bash
pip install --upgrade psycopg2-binary
```

## 📚 Documentation

- [README.md](README.md) - Guide complet
- [ARCHITECTURE.md](ARCHITECTURE.md) - Architecture technique
- [SCHEMA_DB.md](SCHEMA_DB.md) - Schéma base de données
- [Postman_Collection.json](Postman_Collection.json) - Tests API

## ✨ Résumé

Vous avez maintenant:
✅ Backend Flask complet
✅ 27 endpoints API
✅ Base de données PostgreSQL+PostGIS
✅ Données de test
✅ Authentification JWT
✅ Système d'alertes

**Prêt à tester !** 🚀
