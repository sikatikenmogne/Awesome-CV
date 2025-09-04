# Dépannage Windows - MiKTeX

Guide de résolution des problèmes courants sur Windows avec MiKTeX.

## Problème : "security risk: running with elevated privileges"

### Symptômes
```
[ERROR] Echec compilation cv_fr
STDERR: xelatex: security risk: running with elevated privileges
miktex-dvipdfmx: security risk: running with elevated privileges
```

### ✅ Solutions

#### Solution 1 : Utiliser le Mode Debug (Recommandé)
```cmd
python cv.py debug fr
```
Cette commande vous donnera des détails complets sur ce qui se passe.

#### Solution 2 : Réinstaller MiKTeX en Mode Utilisateur
1. **Désinstaller MiKTeX complètement**
2. **Redémarrer Windows**
3. **Réinstaller MiKTeX** : https://miktex.org/download
   - ⚠️ **IMPORTANT** : Choisir "Install for current user" (pas "for all users")
   - Cocher "Add to PATH"

#### Solution 3 : Réparer MiKTeX
```cmd
# Ouvrir MiKTeX Console (en tant qu'utilisateur normal)
# Aller dans "Tasks" > "Refresh file name database"
# Puis "Tasks" > "Update format files"
```

#### Solution 4 : Utiliser un Répertoire de Sortie Différent
Modifiez `config.json` :
```json
{
  "compilation": {
    "files": {
      "cv_fr": {
        "output_dir": "output/fr"
      }
    }
  }
}
```

## Problème : PDF Non Généré

### Diagnostic
```cmd
python cv.py debug fr
```

### Solutions Courantes

#### Vérifier les Fichiers Sources
```cmd
python build.py list
```
Assurez-vous que vos fichiers `.tex` existent.

#### Vérifier les Permissions
1. Clic droit sur le dossier du projet
2. Propriétés > Sécurité
3. Vérifier que vous avez "Contrôle total"

#### Répertoire Temporaire Windows
Parfois Windows bloque l'écriture. Essayez :
```cmd
set TEMP=C:\tmp
set TMP=C:\tmp
mkdir C:\tmp
python cv.py build fr
```

## Problème : "xelatex not found"

### Solution
1. **Vérifier l'installation MiKTeX**
   ```cmd
   xelatex --version
   ```

2. **Si pas trouvé, ajouter au PATH**
   - Panneau de configuration > Système > Variables d'environnement
   - PATH > Ajouter : `C:\Users\VOTRE_NOM\AppData\Local\Programs\MiKTeX\miktex\bin\x64`

3. **Redémarrer l'invite de commande**

## Problème : Packages LaTeX Manquants

### Solution Automatique MiKTeX
MiKTeX installe automatiquement les packages manquants, mais parfois ça échoue.

#### Installer Manuellement
1. Ouvrir **MiKTeX Console**
2. Onglet **Packages**
3. Rechercher et installer :
   - `fontspec`
   - `xunicode`
   - `xltxtra`
   - `polyglossia`

## Problème : Compilation Très Lente

### Solutions
1. **Désactiver l'antivirus temporairement** pour le dossier du projet
2. **Utiliser un SSD** si possible
3. **Fermer les autres applications**

## Problème : Caractères Spéciaux/Accents

### Solution
Vérifier l'encodage de vos fichiers `.tex` :
1. Ouvrir avec VS Code ou Notepad++
2. Sauvegarder en **UTF-8** (pas UTF-8 BOM)

## Commandes de Diagnostic

### Diagnostic Complet
```cmd
python cv.py debug fr          # Debug CV français
python cv.py debug en          # Debug CV anglais  
python setup.py check          # Vérifier le système
python build.py list           # Lister les fichiers
```

### Informations Système
```cmd
python --version               # Version Python
xelatex --version             # Version LaTeX
git --version                 # Version Git
```

### Test Minimal
Créez un fichier test minimal `test.tex` :
```latex
\documentclass{article}
\begin{document}
Test de compilation.
\end{document}
```

Puis testez :
```cmd
xelatex -output-directory=. test.tex
```

## Variables d'Environnement Utiles

```cmd
# Forcer MiKTeX à ne pas demander les packages
set MIKTEX_AUTOINSTALL=1

# Répertoire temporaire personnalisé
set TEMP=C:\temp_latex
set TMP=C:\temp_latex
```

## Logs Détaillés

### Activer les Logs MiKTeX
```cmd
# Dans MiKTeX Console > Settings > General
# Cocher "Always show the log file after a run"
```

### Logs du Script Python
```cmd
python cv.py debug fr > debug.log 2>&1
```

## Si Rien Ne Marche

### Solution de Dernier Recours
1. **Désinstaller MiKTeX complètement**
2. **Nettoyer le registre** avec CCleaner ou équivalent
3. **Redémarrer Windows**
4. **Installer TeX Live** au lieu de MiKTeX :
   - https://tug.org/texlive/windows.html
   - Plus stable mais plus volumineux

### Alternative : WSL
Si vous avez Windows 10/11, utilisez WSL :
```cmd
wsl --install -d Ubuntu
wsl
sudo apt-get install texlive-xetex texlive-fonts-recommended
```

## Support

### Informations à Fournir
Si vous demandez de l'aide, incluez :
```cmd
python cv.py debug fr > debug_info.txt 2>&1
python setup.py check > system_info.txt 2>&1
```

Et partagez le contenu de ces fichiers.

---

*Guide Windows - Samuel SIKATI KENMOGNE 2024*