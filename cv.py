#!/usr/bin/env python3
"""
CV Manager - Script unique cross-platform
Samuel SIKATI KENMOGNE

Point d'entree unique pour toutes les operations CV
Usage: python cv.py [command] [args]
"""

import os
import sys
import subprocess
from pathlib import Path

def show_banner():
    """Affiche la banniere"""
    print("""
=== CV AUTOMATION MANAGER ===
Samuel SIKATI KENMOGNE
Cross-platform CV compilation and release system
    """)

def show_help():
    """Affiche l'aide principale"""
    show_banner()
    print("""
USAGE:
  python cv.py [COMMAND] [ARGUMENTS]

COMMANDES PRINCIPALES:
  build [target]     Compilation des CV
  release [version]  Creation de release
  setup [action]     Installation et configuration
  help               Affiche cette aide

COMMANDES DE COMPILATION:
  build all          Compiler tous les CV
  build fr           Compiler le CV francais
  build en           Compiler le CV anglais
  build clean        Nettoyer fichiers temporaires
  build list         Lister les fichiers

COMMANDES DE RELEASE:
  release            Release avec version automatique
  release v1.2.3     Release avec version specifique
  release --dry-run  Simulation de release
  release --build-only   Compilation sans release

COMMANDES DE SETUP:
  setup install      Installation complete
  setup check        Verification systeme

COMMANDES DE DEBUG:
  debug [file]       Mode debug compilation (defaut: cv_fr)
  debug-fr          Debug compilation CV francais
  debug-en          Debug compilation CV anglais

EXEMPLES:
  python cv.py build all
  python cv.py release v1.2.3
  python cv.py setup check
  python cv.py debug fr      # Debug du CV francais

Pour plus d'aide sur une commande:
  python cv.py [command] --help
    """)

def execute_script(script_name, args):
    """Execute un script Python avec les arguments"""
    script_path = Path(script_name)
    
    if not script_path.exists():
        print(f"ERROR: Script manquant: {script_name}")
        print("Executez 'python cv.py setup install' pour l'installation")
        return False
    
    try:
        cmd = [sys.executable, str(script_path)] + args
        result = subprocess.run(cmd, check=True)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Echec execution {script_name} (code: {e.returncode})")
        return False
    except KeyboardInterrupt:
        print("\nInterrompu par l'utilisateur")
        return False

def handle_build(args):
    """Gere les commandes de compilation"""
    if not args or args[0] == "--help":
        print("""
COMMANDES DE COMPILATION:

  all, build       Compile tous les fichiers actifs
  fr, french       Compile uniquement le CV francais
  en, english      Compile uniquement le CV anglais  
  clean            Supprime les fichiers temporaires
  distclean        Nettoyage complet
  list             Liste les fichiers configurables
  check            Verifie l'installation LaTeX
  debug [file]     Mode debug pour diagnostiquer les problemes

EXEMPLES:
  python cv.py build all
  python cv.py build fr
  python cv.py build debug fr    # Debug compilation CV francais
  python cv.py build clean
        """)
        return True
    
    return execute_script("build.py", args)

def handle_release(args):
    """Gere les commandes de release"""
    if args and args[0] == "--help":
        print("""
COMMANDES DE RELEASE:

ARGUMENTS:
  [version]        Version a creer (ex: v1.2.3)
                  Si omise, genere automatiquement

OPTIONS:
  --dry-run       Simulation sans creation de tag
  --force         Force la creation meme si le tag existe
  --build-only    Compile uniquement sans release

EXEMPLES:
  python cv.py release                    # Version automatique
  python cv.py release v1.2.3            # Version specifique
  python cv.py release v1.2.3 --dry-run  # Simulation
  python cv.py release --build-only      # Compilation seulement
        """)
        return True
    
    return execute_script("release.py", args)

def handle_setup(args):
    """Gere les commandes d'installation"""
    if not args:
        args = ["install"]
    
    if args[0] == "--help":
        print("""
COMMANDES DE SETUP:

  install      Installation complete automatique
  check        Verification de l'environnement

EXEMPLES:
  python cv.py setup install
  python cv.py setup check
        """)
        return True
    
    return execute_script("setup.py", args)

def quick_status():
    """Affiche un statut rapide du projet"""
    print("=== STATUT RAPIDE ===")
    
    # Configuration
    if Path("config.json").exists():
        print("[OK] Configuration trouvee")
    else:
        print("[MANQUANT] config.json")
    
    # Scripts essentiels
    essential_scripts = ["build.py", "release.py", "setup.py"]
    for script in essential_scripts:
        if Path(script).exists():
            print(f"[OK] {script}")
        else:
            print(f"[MANQUANT] {script}")
    
    # Sources CV
    cv_sources = ["custom/fr/resume-fr.tex", "custom/en/resume-en.tex"]
    for source in cv_sources:
        if Path(source).exists():
            print(f"[OK] {source}")
        else:
            print(f"[MANQUANT] {source}")
    
    # PDF generes
    pdf_outputs = [
        "custom/output/fr/CV-Samuel-SIKATI-KENMOGNE-Ingenieur-Logiciel-FR.pdf",
        "custom/output/en/CV-Samuel-SIKATI-KENMOGNE-Software-Engineer-EN.pdf"
    ]
    
    pdf_count = 0
    for pdf in pdf_outputs:
        if Path(pdf).exists():
            pdf_count += 1
    
    print(f"[INFO] PDF generes: {pdf_count}/2")

def main():
    """Point d'entree principal"""
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    args = sys.argv[2:]
    
    # Commandes principales
    if command in ["build", "compile"]:
        success = handle_build(args)
        sys.exit(0 if success else 1)
        
    elif command in ["release", "tag"]:
        success = handle_release(args)
        sys.exit(0 if success else 1)
        
    elif command in ["setup", "install"]:
        success = handle_setup(args)
        sys.exit(0 if success else 1)
        
    elif command in ["help", "--help", "-h"]:
        show_help()
        
    elif command in ["status", "info"]:
        quick_status()
        
    elif command == "version":
        show_banner()
        print("Version: 1.0.0")
        print("Cross-platform CV automation system")
        
    # Raccourcis directs
    elif command == "all":
        success = execute_script("build.py", ["all"])
        sys.exit(0 if success else 1)
        
    elif command in ["fr", "french"]:
        success = execute_script("build.py", ["fr"])
        sys.exit(0 if success else 1)
        
    elif command in ["en", "english"]:
        success = execute_script("build.py", ["en"])
        sys.exit(0 if success else 1)
        
    elif command == "clean":
        success = execute_script("build.py", ["clean"])
        sys.exit(0 if success else 1)
        
    elif command == "check":
        success = execute_script("setup.py", ["check"])
        sys.exit(0 if success else 1)
        
    # Commandes de debug
    elif command == "debug":
        file_key = args[0] if args else "cv_fr"
        success = execute_script("build.py", ["debug", file_key])
        sys.exit(0 if success else 1)
        
    elif command == "debug-fr":
        success = execute_script("build.py", ["debug", "cv_fr"])
        sys.exit(0 if success else 1)
        
    elif command == "debug-en":
        success = execute_script("build.py", ["debug", "cv_en"])
        sys.exit(0 if success else 1)
        
    else:
        print(f"Commande inconnue: {command}")
        print("Utilisez: python cv.py help")
        sys.exit(1)

if __name__ == "__main__":
    main()