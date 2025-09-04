# CV Automation - Cross-Platform

Système d'automatisation simple et efficace pour la compilation et publication de CV.

## Installation Rapide (3 étapes)

### 1. Prérequis

**Tous systèmes :**
- Python 3.7+
- Git 
- XeLaTeX (MiKTeX/TeX Live/MacTeX)

**Installation par système :**

```bash
# Windows
# Téléchargez depuis les sites officiels :
# - Python: https://python.org/downloads (cochez "Add to PATH")
# - Git: https://git-scm.com/download/win
# - MiKTeX: https://miktex.org/download

# Linux (Ubuntu/Debian)
sudo apt-get install python3 git texlive-xetex texlive-fonts-recommended

# macOS
brew install python git
brew install --cask mactex
```

### 2. Installation du Projet

```bash
# Cloner et installer
git clone https://github.com/votre-username/Awesome-CV.git
cd Awesome-CV
python setup.py install
```

### 3. Premier Test

```bash
# Vérifier l'installation
python cv.py check

# Compiler vos CV (quand vous aurez créé vos .tex)
python cv.py build all
```

## Utilisation

### Script Principal (Recommandé)

```bash
python cv.py [commande] [arguments]
```

**Commandes principales :**
```bash
python cv.py build all          # Compiler tous les CV
python cv.py build fr           # CV français seulement
python cv.py build en           # CV anglais seulement
python cv.py release            # Créer une release GitHub
python cv.py release v1.2.3     # Release avec version spécifique
python cv.py setup check        # Vérifier l'installation
python cv.py help               # Aide complète
```

### Scripts Individuels

```bash
python build.py all             # Compilation
python release.py v1.2.3        # Release
python setup.py check           # Vérification
```

## Structure

```
Awesome-CV/
├── config.json                 # Configuration principale
├── cv.py                       # Script principal
├── build.py                    # Compilation
├── release.py                  # Release 
├── setup.py                    # Installation
├── custom/
│   ├── fr/
│   │   └── resume-fr.tex       # Votre CV français
│   ├── en/
│   │   └── resume-en.tex       # Votre CV anglais
│   └── output/                 # PDF générés
└── .github/workflows/
    └── build-release-cv.yml    # Workflow GitHub Actions
```

## Configuration

### Fichiers de Base

1. **Créez vos CV :**
   - `custom/fr/resume-fr.tex` (CV français)
   - `custom/en/resume-en.tex` (CV anglais)

2. **Modifiez `config.json` avec vos informations :**
```json
{
  "project": {
    "author": "VOTRE NOM"
  },
  "compilation": {
    "files": {
      "cv_fr": {
        "output_name": "CV-VOTRE-NOM-Ingenieur-Logiciel-FR.pdf"
      },
      "cv_en": {
        "output_name": "CV-VOTRE-NOM-Software-Engineer-EN.pdf"
      }
    }
  }
}
```

### Ajouter des Fichiers Supplémentaires

Pour ajouter une lettre de motivation :

```json
{
  "compilation": {
    "additional_files": [
      {
        "name": "cover_letter_fr",
        "source": "custom/fr/coverletter/coverletter.tex",
        "output_dir": "custom/output/fr",
        "output_name": "Lettre-Motivation-VOTRE-NOM-FR.pdf",
        "enabled": true
      }
    ]
  }
}
```

## Workflow GitHub Actions

Le système crée automatiquement des releases avec vos PDF quand vous créez un tag :

```bash
# Créer une release automatiquement
python cv.py release

# Ou manuellement
git tag v1.2.3
git push origin v1.2.3
# GitHub Actions compile et publie automatiquement
```

## Raccourcis

```bash
# Compilation rapide
python cv.py all             # = python cv.py build all
python cv.py fr              # = python cv.py build fr  
python cv.py en              # = python cv.py build en
python cv.py clean           # = python cv.py build clean

# Vérification
python cv.py check           # = python cv.py setup check
python cv.py status          # Statut rapide du projet
```

## Dépannage

### Erreurs Courantes

**Python non reconnu (Windows) :**
- Réinstallez Python en cochant "Add Python to PATH"

**XeLaTeX non trouvé :**
```bash
python cv.py check           # Voir les instructions d'installation
```

**Erreur de compilation :**
```bash
python cv.py build clean    # Nettoyer et recommencer
python cv.py build fr       # Compiler un seul fichier pour tester
```

**Configuration invalide :**
```bash
python setup.py install     # Régénère config.json d'exemple
```

## Caractéristiques

- **Cross-platform** : Windows, Linux, macOS
- **Simple** : Une seule commande pour tout
- **Flexible** : Ajout facile de nouveaux documents
- **Automatique** : GitHub Actions intégré
- **Sans dépendances** : Utilise seulement Python standard
- **Robuste** : Gestion d'erreurs et validation

