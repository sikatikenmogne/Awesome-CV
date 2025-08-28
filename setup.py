#!/usr/bin/env python3
"""
Script d'installation CV cross-platform
Samuel SIKATI KENMOGNE

Usage: python setup.py [command]
"""

import os
import sys
import json
import subprocess
import shutil
import platform
from pathlib import Path

class CVSetup:
    def __init__(self):
        self.is_windows = platform.system().lower() == "windows"
        self.is_macos = platform.system().lower() == "darwin"
        self.is_linux = platform.system().lower() == "linux"
        
    def log(self, level, message):
        """Log cross-platform"""
        print(f"[{level}] {message}")
    
    def detect_system(self):
        """Detecte le systeme"""
        system_info = {
            "OS": platform.system(),
            "Architecture": platform.machine(),  
            "Python": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        }
        
        self.log("INFO", "Detection du systeme:")
        for key, value in system_info.items():
            print(f"  {key}: {value}")
        
        return True
    
    def check_dependencies(self):
        """Verifie les dependances"""
        self.log("INFO", "Verification des dependances...")
        
        status = {"git": False, "latex": False, "python": True}
        
        # Git
        if shutil.which("git"):
            try:
                result = subprocess.run(["git", "--version"], capture_output=True, text=True, timeout=10)
                version = result.stdout.strip().split()[-1] if result.stdout else "inconnue"
                self.log("SUCCESS", f"Git v{version}")
                status["git"] = True
            except:
                self.log("WARNING", "Git installe mais version indeterminee")
                status["git"] = True
        else:
            self.log("ERROR", "Git non installe")
            self.show_git_install_instructions()
        
        # LaTeX
        if shutil.which("xelatex"):
            try:
                result = subprocess.run(["xelatex", "--version"], capture_output=True, text=True, timeout=10)
                version_line = result.stdout.split('\n')[0] if result.stdout else "Version inconnue"
                self.log("SUCCESS", f"XeLaTeX: {version_line.strip()}")
                status["latex"] = True
            except:
                self.log("WARNING", "XeLaTeX installe mais version indeterminee")
                status["latex"] = True
        else:
            self.log("ERROR", "XeLaTeX non installe")
            self.show_latex_install_instructions()
        
        # Repository Git
        try:
            subprocess.run(["git", "rev-parse", "--git-dir"], check=True, capture_output=True)
            self.log("SUCCESS", "Repository Git detecte")
        except subprocess.CalledProcessError:
            self.log("WARNING", "Pas dans un repository Git")
        
        return status
    
    def show_git_install_instructions(self):
        """Instructions installation Git"""
        if self.is_windows:
            print("  Installez Git: https://git-scm.com/download/win")
        elif self.is_macos:
            print("  Installez Git: brew install git")
            print("  Ou: https://git-scm.com/download/mac")
        else:
            print("  Installez Git: sudo apt-get install git")
    
    def show_latex_install_instructions(self):
        """Instructions installation LaTeX"""
        if self.is_windows:
            print("  Installez MiKTeX: https://miktex.org/download")
            print("  Ou TeX Live: https://tug.org/texlive/windows.html")
        elif self.is_macos:
            print("  Installez MacTeX: https://tug.org/mactex/")
            print("  Ou: brew install --cask mactex")
        else:
            print("  Installez TeX Live:")
            print("  sudo apt-get install texlive-xetex texlive-fonts-recommended texlive-latex-extra")
    
    def create_directories(self):
        """Cree la structure de repertoires"""
        self.log("INFO", "Creation des repertoires...")
        
        directories = [
            "custom/fr",
            "custom/en", 
            "custom/output/fr",
            "custom/output/en",
            ".github/workflows"
        ]
        
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
            self.log("SUCCESS", f"Repertoire: {directory}")
    
    def create_gitignore(self):
        """Cree .gitignore"""
        gitignore_content = """# LaTeX temporary files
*.aux
*.log
*.out
*.synctex.gz
*.fdb_latexmk
*.fls
*.xdv

# Python cache
__pycache__/
*.pyc

# OS specific
.DS_Store
Thumbs.db

# Keep output structure but ignore PDFs
custom/output/*/
!custom/output/*/.gitkeep
"""
        
        gitignore_path = Path(".gitignore")
        if not gitignore_path.exists():
            gitignore_path.write_text(gitignore_content, encoding='utf-8')
            self.log("SUCCESS", "Fichier .gitignore cree")
        else:
            self.log("INFO", "Fichier .gitignore existe deja")
    
    def create_sample_config(self):
        """Cree un exemple de configuration"""
        config_path = Path("config.json")
        if config_path.exists():
            self.log("INFO", "Configuration existe deja")
            return
            
        sample_config = {
            "project": {
                "name": "CV-VOTRE-NOM",
                "author": "VOTRE NOM",
                "version_format": "v%Y.%m.%d"
            },
            "compilation": {
                "latex_compiler": "xelatex",
                "latex_flags": ["-synctex=1", "-interaction=nonstopmode", "-file-line-error"],
                "files": {
                    "cv_fr": {
                        "source": "custom/fr/resume-fr.tex",
                        "output_dir": "custom/output/fr",
                        "output_name": "CV-VOTRE-NOM-Ingenieur-Logiciel-FR.pdf"
                    },
                    "cv_en": {
                        "source": "custom/en/resume-en.tex",
                        "output_dir": "custom/output/en", 
                        "output_name": "CV-VOTRE-NOM-Software-Engineer-EN.pdf"
                    }
                }
            }
        }
        
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(sample_config, f, indent=2, ensure_ascii=False)
        
        self.log("SUCCESS", "Configuration d'exemple creee")
        self.log("INFO", "Modifiez config.json avec vos informations")
    
    def test_system(self):
        """Test basique du systeme"""
        self.log("INFO", "Test du systeme...")
        
        # Test Python
        self.log("SUCCESS", f"Python {sys.version}")
        
        # Test imports
        try:
            import json
            self.log("SUCCESS", "Module json OK")
        except ImportError:
            self.log("ERROR", "Module json manquant")
            return False
        
        # Test fichiers essentiels
        essential_files = ["build.py", "release.py"]
        for file_name in essential_files:
            if Path(file_name).exists():
                self.log("SUCCESS", f"Script essentiel: {file_name}")
            else:
                self.log("WARNING", f"Script manquant: {file_name}")
        
        return True
    
    def show_next_steps(self):
        """Affiche les prochaines etapes"""
        print("\n" + "="*50)
        print("INSTALLATION TERMINEE")
        print("="*50)
        
        print("\nPROCHAINES ETAPES:")
        print("1. Modifiez config.json avec vos informations")
        print("2. Creez vos fichiers CV:")
        print("   - custom/fr/resume-fr.tex (CV francais)")
        print("   - custom/en/resume-en.tex (CV anglais)")
        print("3. Testez la compilation:")
        print("   python build.py all")
        print("4. Creez votre premiere release:")
        print("   python release.py")
        
        print("\nCOMMANDES PRINCIPALES:")
        print("  python build.py all     - Compiler tous les CV")
        print("  python build.py fr      - CV francais seulement") 
        print("  python build.py en      - CV anglais seulement")
        print("  python release.py       - Creer une release")
        print("  python setup.py check   - Verifier l'installation")
        
        print(f"\nVotre environnement CV est pret!")

def main():
    """Point d'entree principal"""
    command = sys.argv[1] if len(sys.argv) > 1 else "install"
    
    setup = CVSetup()
    
    if command == "install":
        print("=== INSTALLATION CV AUTOMATION ===")
        
        setup.detect_system()
        deps = setup.check_dependencies()
        setup.create_directories()
        setup.create_gitignore()
        setup.create_sample_config()
        setup.test_system()
        setup.show_next_steps()
        
        if not all(deps.values()):
            print("\nWARNING: Certaines dependances sont manquantes")
            sys.exit(1)
            
    elif command == "check":
        print("=== VERIFICATION SYSTEME ===")
        
        setup.detect_system()
        deps = setup.check_dependencies()
        
        if all(deps.values()):
            setup.log("SUCCESS", "Toutes les dependances sont installees")
        else:
            setup.log("ERROR", "Dependances manquantes detectees")
            sys.exit(1)
            
    elif command in ["help", "--help", "-h"]:
        print("""
Script d'installation CV cross-platform

USAGE:
  python setup.py [COMMAND]

COMMANDS:
  install    Installation complete (defaut)
  check      Verification des dependances
  help       Affiche cette aide

EXEMPLES:
  python setup.py install
  python setup.py check
        """)
        
    else:
        print(f"Commande inconnue: {command}")
        print("Commandes: install, check, help")
        sys.exit(1)

if __name__ == "__main__":
    main()
