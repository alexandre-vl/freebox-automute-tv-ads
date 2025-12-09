# 🎯 Guide de la Nouvelle Structure

## 📊 Vue d'Ensemble

La codebase a été complètement réorganisée en une structure professionnelle et maintenable.

```
freetv/
├── 📁 src/                     # Code source principal
│   ├── freetv/                # ⭐ Package principal
│   ├── config.py              # Configuration
│   └── __init__.py            # Package initialization
│
├── 📁 scripts/                 # Scripts utilitaires
│   ├── quickstart.sh          # Installation rapide
│   ├── setup_wizard.py        # Assistant de configuration
│   ├── channel_mapper.py      # Mapper les chaînes
│   ├── debug_demute.py        # Analyser démutages
│   ├── solution_demute.py     # Tester solutions
│   └── ...
│
├── 📁 tests/                   # Tests unitaires
│   ├── test_basic.py          # Tests basiques
│   └── test_demute_fix.py     # Tests correction démutage
│
├── 📁 docs/                    # Documentation
│   └── legacy/                # Ancienne documentation
│       ├── main.py            # Ancien programme
│       └── *.md               # Anciens docs
│
├── 📄 README.md                # Documentation principale
├── 📄 CHANGELOG.md             # Historique des versions
├── 📄 Makefile                 # Commandes utiles
├── 📄 run.sh                   # Script de lancement simple
├── 📄 pyproject.toml           # Configuration Python
├── 📄 requirements.txt         # Dépendances
└── 📄 .gitignore              # Fichiers ignorés

```

---

## 🎯 Principaux Changements

### 1️⃣ **Code Source dans `src/`**

| Avant | Après | Raison |
|-------|-------|--------|
| `main_fancy.py` (racine) | `src/freetv` | Nom plus clair et descriptif |
| `main.py` (racine) | `docs/legacy/main.py` | Version obsolète archivée |
| `config.py` (racine) | `src/config.py` | Regroupement logique |

**Bénéfices:**
- ✅ Structure claire et professionnelle
- ✅ Séparation code source / scripts / tests
- ✅ Import plus propres (`from src import ...`)

### 2️⃣ **Scripts dans `scripts/`**

Tous les utilitaires ont été déplacés :
- Setup et configuration
- Mapping des chaînes
- Scripts de debug
- Outils de test

**Bénéfices:**
- ✅ Distinction claire entre code applicatif et utilitaires
- ✅ Facile de trouver les scripts
- ✅ Meilleure organisation

### 3️⃣ **Tests dans `tests/`**

Tests unitaires regroupés et organisés.

**Bénéfices:**
- ✅ Structure standard Python
- ✅ Facile d'ajouter de nouveaux tests
- ✅ Séparation code / tests

### 4️⃣ **Documentation dans `docs/`**

- **`docs/legacy/`** : Ancienne documentation conservée pour référence
- **Racine** : `README.md` et `CHANGELOG.md` modernisés

**Bénéfices:**
- ✅ Documentation claire et accessible
- ✅ Historique préservé
- ✅ README professionnel

---

## 🚀 Comment Utiliser la Nouvelle Structure

### Démarrage Rapide

```bash
# Option 1: Script universel
./run.sh

# Option 2: Make
make run

# Option 3: Direct
uv run python -m src.freetv
```

### Configuration

```bash
# Éditer la configuration
vim src/config.py

# Ou utiliser l'assistant
make setup
```

### Mapping de chaînes

```bash
# Utiliser le mapper
make map-channels

# Ou directement
python scripts/channel_mapper.py
```

### Tests

```bash
# Tous les tests
make test

# Test spécifique
python tests/test_demute_fix.py
```

### Debug

```bash
# Analyser les démutages
make debug-demute

# Ou directement
python scripts/debug_demute.py
```

---

## 📝 Fichiers Importants

### `src/freetv` ⭐

**LE** programme principal. C'est lui qui :
- Se connecte à la Freebox
- Détecte les publicités
- Mute/démute automatiquement
- Affiche l'interface TUI

**Anciennes versions:**
- `main_fancy.py` → **SUPPRIMÉ** (refactorisé en package `src/freetv`)
- `main.py` → **ARCHIVÉ** dans `docs/legacy/main.py`

### `src/config.py`

Configuration centralisée :
- Connexion Freebox
- Mapping des chaînes
- Paramètres de cache
- Intervalles

### `Makefile`

Commandes utiles :
```bash
make help           # Liste toutes les commandes
make run            # Lance le programme
make test           # Exécute les tests
make clean          # Nettoie les fichiers temporaires
make map-channels   # Mapper les chaînes
```

### `run.sh`

Script de démarrage universel qui :
- Détecte `uv` ou Python
- Active l'environnement virtuel si besoin
- Lance le programme

---

## 🎓 Best Practices

### Ajout d'une Nouvelle Fonctionnalité

1. **Code dans `src/`**
   ```bash
   vim src/new_feature.py
   ```

2. **Tests dans `tests/`**
   ```bash
   vim tests/test_new_feature.py
   ```

3. **Documentation dans `README.md`**
   ```bash
   vim README.md
   ```

4. **Changelog**
   ```bash
   vim CHANGELOG.md
   ```

### Ajout d'un Nouveau Script

1. **Script dans `scripts/`**
   ```bash
   vim scripts/my_tool.py
   chmod +x scripts/my_tool.py
   ```

2. **Documentation dans le script**
   ```python
   """
   Description de l'outil.
   
   Usage:
       python scripts/my_tool.py [options]
   """
   ```

3. **Ajouter une commande Make (optionnel)**
   ```makefile
   my-tool: ## Description de la commande
       @uv run python scripts/my_tool.py
   ```

---

## 🔄 Migration depuis l'Ancienne Structure

### Si vous aviez des modifications dans `main_fancy.py`

1. **Vérifier le nouveau fichier**
   ```bash
   vim src/freetv/core/engine.py
   ```

2. **Appliquer vos modifications**
   - Les fonctionnalités de base sont identiques
   - Ajout du buffer de démutage (10s)
   - Fusion automatique des ad_breaks

3. **Tester**
   ```bash
   make compile
   make run
   ```

### Si vous aviez une configuration customisée

1. **Éditer `src/config.py`**
   ```bash
   vim src/config.py
   ```

2. **Adapter vos mappings de chaînes**
   ```python
   CHANNEL_MAPPING = {
       "uuid-webtv-XXX": "YYY",
       # ...
   }
   ```

---

## ❓ FAQ

### Où est passé `main.py` ?

**Archivé** dans `docs/legacy/main.py`. Il n'est plus utilisé car :
- Interface moins riche
- Pas d'EPG
- Pas de correction du démutage
- Code moins maintenable

### Où est `main_fancy.py` ?

**Refactorisé** en package `src/freetv` :
- Nom plus descriptif
- Localisation dans `src/`
- Toutes les fonctionnalités préservées

### Pourquoi tant de fichiers dans `scripts/` ?

Ce sont des **outils utilitaires**, pas du code applicatif :
- Configuration
- Debug
- Mapping
- Tests

On peut les ignorer pour l'utilisation quotidienne.

### Comment lancer le programme maintenant ?

**3 options simples:**
```bash
./run.sh           # Le plus simple
make run          # Avec Make
uv run python -m src.freetv  # Direct
```

### Les anciens scripts marchent encore ?

Oui, ceux dans `scripts/` :
- `scripts/quickstart.sh` ✅
- `scripts/setup.sh` ✅
- etc.

Mais les références à `main_fancy.py` ont été mises à jour.

---

## 🎉 Avantages de la Nouvelle Structure

### Pour les Développeurs

- ✅ **Code organisé** : Facile de trouver ce qu'on cherche
- ✅ **Tests séparés** : Plus facile à maintenir
- ✅ **Scripts utilitaires** : Clairement identifiés
- ✅ **Documentation** : Tout est documenté

### Pour les Utilisateurs

- ✅ **Plus simple** : `./run.sh` et c'est tout
- ✅ **Makefile** : Commandes claires (`make run`, `make test`)
- ✅ **README clair** : Onboarding plus rapide
- ✅ **Moins de fichiers** à la racine : Moins de confusion

### Pour le Projet

- ✅ **Maintenabilité** : Structure standard Python
- ✅ **Évolutivité** : Facile d'ajouter des fonctionnalités
- ✅ **Professionnalisme** : Structure reconnue
- ✅ **Collaboration** : Facilite les contributions

---

## 🚀 Prochaines Étapes

1. **Tester la nouvelle structure**
   ```bash
   make compile
   make test
   make run
   ```

2. **Mettre à jour vos habitudes**
   - Utiliser `./run.sh` ou `make run`
   - Éditer `src/config.py` pour la config
   - Utiliser `make` pour les commandes courantes

3. **Explorer les nouvelles fonctionnalités**
   - Buffer de démutage
   - Fusion des ad_breaks
   - Interface TUI améliorée

---

**🎊 Félicitations ! Vous avez maintenant une codebase professionnelle et organisée.**
