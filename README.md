# 🎬 Freebox Auto-Mute

**Programme intelligent d'auto-mute des publicités pour Freebox Player**

Détecte automatiquement les publicités via l'API OQEE et mute/démute votre Freebox Player en temps réel.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-stable-brightgreen.svg)

---

## ✨ Fonctionnalités

- 🔇 **Mute automatique** pendant les publicités
- 📺 **Interface graphique** avec affichage en temps réel (Rich TUI)
- 🎯 **Détection intelligente** via l'API OQEE
- ⚡ **Anti-flash audio** : fusion des pubs consécutives (< 10s)
- 📊 **EPG intégré** : affichage du programme en cours
- 🔄 **Cache intelligent** : limiteles appels API
- 🎨 **Thème moderne** : interface soignée avec icônes et couleurs

---

## 🚀 Installation Rapide

### Prérequis

- Python 3.8+
- Une Freebox (Delta, Pop, Ultra, etc.)
- Accès au réseau local de la Freebox

### Installation avec `uv` (recommandé)

```bash
# 1. Cloner le projet
git clone <repo-url>
cd freetv

# 2. Installer les dépendances
uv sync

# 3. Configuration initiale
./scripts/quickstart.sh
```

### Installation avec `pip`

```bash
# 1. Créer un environnement virtuel
python3 -m venv .venv
source .venv/bin/activate

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Lancer le programme
python -m src.freetv
```

---

## ⚙️ Configuration

### Fichier `src/config.py`

```python
# Connexion Freebox
FREEBOX_HOST = "mafreebox.freebox.fr"
FREEBOX_PORT = "443"

# Intervalle entre chaque vérification (en secondes)
CHECK_INTERVAL = 2

# Durée du cache des ad breaks OQEE (en secondes)
AD_BREAKS_CACHE_TTL = 3

# Mapping chaînes Freebox ↔ OQEE
CHANNEL_MAPPING = {
    "uuid-webtv-612": "536",  # TF1
    "uuid-webtv-201": "270",  # France 2
    "uuid-webtv-613": "537",  # M6
    # ... voir config.py pour la liste complète
}
```

### Permissions Freebox

**Important** : L'application doit avoir la permission "Contrôle du Freebox Player"

1. Ouvrez `http://mafreebox.freebox.fr`
2. Allez dans **Paramètres → Gestion des accès → Applications**
3. Trouvez **Freepybox** et cochez **✅ Contrôle du Freebox Player**

---

## 🎯 Utilisation

### Lancement Standard

```bash
# Avec uv
uv run python -m src.freetv

# Avec Python
python -m src.freetv
```

### Makefile(raccourcis)

```bash
make run        # Lancer le programme
make setup      # Assistant de configuration
make test       # Lancer les tests
make clean      # Nettoyer les fichiers temporaires
```

---

## 📁 Structure du Projet

```
freetv/
├── src/
│   ├── freetv/               # Package principal ⭐
│   │   ├── __main__.py       # Point d'entrée
│   │   └── ...
│   └── config.py              # Configuration
├── scripts/
│   ├── channel_mapper.py      # Mapper les chaînes
├── tests/
│   ├── test_basic.py          # Tests basiques
│   └── test_demute_fix.py     # Tests correction démutage
├── .github/
│   └── workflows/             # CI/CD
├── Makefile                   # Commandes utiles
├── pyproject.toml             # Configuration Python
├── requirements.txt           # Dépendances pip
└── README.md                  # Ce fichier
```

---

## 🔧 Scripts Utilitaires

### Mapper des nouvelles chaînes

```bash
python scripts/channel_mapper.py
```

Affiche les chaînes disponibles et aide à créer le mapping Freebox ↔ OQEE.

---

## 🐛 Dépannage

### Le programme ne se connecte pas

1. Vérifiez que votre Freebox est accessible : `ping mafreebox.freebox.fr`
2. Vérifiez les permissions dans l'interface Freebox
3. Regardez les logs pour plus de détails

### Les publicités ne sont pas détectées

1. Vérifiez que votre chaîne est dans `CHANNEL_MAPPING`
2. Utilisez `scripts/channel_mapper.py` pour trouver l'ID OQEE
3. Certaines chaînes n'ont pas d'API anti-pub disponible

### Flash audio entre deux pubs

✅ **Résolu** depuis la v2.0 avec :
- Fusion automatique des ad_breaks proches (< 10s)
- Buffer de démutage (10s avant la prochaine pub)

---

## 🧪 Tests

```bash
# Tous les tests
make test

# Tests spécifiques
python tests/test_demute_fix.py
python tests/test_basic.py
```

---

## 📊 Performance

- **Consommation mémoire** : ~50 MB
- **CPU** : < 1% en moyenne
- **Latence de détection** : 1-2 secondes
- **Appels API** : Cache intelligent (refresh toutes les 3s max)

---

## 🗺️ Roadmap

- [ ] Support multi-Freebox
- [ ] Interface web (dashboard)
- [ ] Statistiques de pubs détectées
- [ ] Export des données en JSON/CSV
- [ ] Support d'autres box (LiveBox, etc.)
- [ ] Mode "apprentissage" pour améliorer la détection

---

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :

1. Fork le projet
2. Créer une branche (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add AmazingFeature'`)
4. Push (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

---

## 📜 Licence

MIT License - voir le fichier LICENSE pour plus de détails.

---

## 🙏 Remerciements

- [freepybox](https://github.com/foreign-sub/freepybox) - Client Python pour l'API Freebox
- [rich](https://github.com/Textualize/rich) - Magnifique TUI
- API OQEE - Données EPG et ad_breaks

---

## 📧 Contact

Pour toute question ou suggestion, ouvrez une issue sur GitHub.

---

**Fait avec ❤️ et ☕ pour ne plus jamais entendre de pubs**
