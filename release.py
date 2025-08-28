#!/usr/bin/env python3
"""
Script de release CV cross-platform
Samuel SIKATI KENMOGNE

Usage: python release.py [version] [options]
"""

import os
import sys
import json
import subprocess
import shutil
from datetime import datetime
from pathlib import Path

class CVReleaser:
    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        self.config = self.load_config()
        
    def load_config(self):
        """Charge la configuration"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"ERROR: Configuration invalide: {e}")
            return None
    
    def log(self, level, message):
        """Log cross-platform"""
        print(f"[{level}] {message}")
    
    def check_prerequisites(self):
        """Verifie les prerequis"""
        self.log("INFO", "Verification des prerequis...")
        
        # Git
        if not shutil.which("git"):
            self.log("ERROR", "Git non installe")
            return False
        
        # Repository Git
        try:
            subprocess.run(["git", "rev-parse", "--git-dir"], 
                          check=True, capture_output=True)
        except subprocess.CalledProcessError:
            self.log("ERROR", "Pas dans un repository Git")
            return False
        
        # Changements non commites
        try:
            result = subprocess.run(["git", "status", "--porcelain"], 
                                  capture_output=True, text=True)
            if result.stdout.strip():
                self.log("WARNING", "Changements non commites detectes:")
                print(result.stdout)
                response = input("Continuer? [y/N]: ").lower()
                if response != 'y':
                    return False
        except subprocess.CalledProcessError:
            self.log("WARNING", "Impossible de verifier le statut Git")
        
        self.log("SUCCESS", "Prerequis OK")
        return True
    
    def build_cvs(self):
        """Compile les CV"""
        self.log("INFO", "Compilation des CV...")
        
        try:
            from build import CVBuilder
            builder = CVBuilder(self.config_path)
            
            if builder.build_all():
                self.log("SUCCESS", "CV compiles avec succes")
                return True
            else:
                self.log("ERROR", "Echec compilation des CV")
                return False
                
        except ImportError:
            self.log("ERROR", "Module build.py non disponible")
            return False
        except Exception as e:
            self.log("ERROR", f"Erreur compilation: {e}")
            return False
    
    def generate_version(self):
        """Genere une version automatique"""
        if self.config:
            format_str = self.config.get("project", {}).get("version_format", "v%Y.%m.%d")
            return datetime.now().strftime(format_str)
        return datetime.now().strftime("v%Y.%m.%d")
    
    def tag_exists(self, version):
        """Verifie si un tag existe"""
        try:
            result = subprocess.run(["git", "tag", "-l"], capture_output=True, text=True)
            return version in result.stdout.splitlines()
        except subprocess.CalledProcessError:
            return False
    
    def create_release(self, version, dry_run=False, force=False):
        """Cree une release"""
        self.log("INFO", f"Creation release {version}")
        
        # Verifier tag existant
        if self.tag_exists(version):
            if force:
                self.log("WARNING", f"Suppression tag existant: {version}")
                try:
                    subprocess.run(["git", "tag", "-d", version], check=True, capture_output=True)
                    subprocess.run(["git", "push", "origin", f":refs/tags/{version}"], 
                                 capture_output=True)  # Ignore errors for remote
                except subprocess.CalledProcessError:
                    pass
            else:
                self.log("ERROR", f"Tag {version} existe deja. Utilisez --force")
                return False
        
        if dry_run:
            self.log("INFO", "SIMULATION - Actions qui seraient effectuees:")
            self.log("INFO", f"  1. Creation tag: {version}")
            self.log("INFO", "  2. Push vers origin")
            self.log("INFO", "  3. GitHub Actions declencherait la release")
            return True
        
        # Message du tag
        author = self.config.get("project", {}).get("author", "Unknown") if self.config else "Unknown"
        date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        message = f"""Release {version}

Nouvelle version du CV de {author}

Documents inclus:
- CV francais (Ingenieur Logiciel)  
- CV anglais (Software Engineer)

Genere le {date_str}"""
        
        try:
            # Creer tag
            self.log("INFO", f"Creation du tag {version}...")
            subprocess.run(["git", "tag", "-a", version, "-m", message], check=True)
            
            # Push tag
            self.log("INFO", "Push du tag vers origin...")
            subprocess.run(["git", "push", "origin", version], check=True)
            
            self.log("SUCCESS", f"Tag {version} cree et pousse!")
            self.log("INFO", "GitHub Actions va maintenant creer la release automatiquement")
            
            return True
            
        except subprocess.CalledProcessError as e:
            self.log("ERROR", f"Echec creation tag: {e}")
            return False

def main():
    """Point d'entree principal"""
    # Parse arguments simples
    args = sys.argv[1:]
    
    version = None
    dry_run = False
    force = False
    build_only = False
    
    # Parse arguments
    i = 0
    while i < len(args):
        arg = args[i]
        if arg in ["--dry-run", "-d"]:
            dry_run = True
        elif arg in ["--force", "-f"]:
            force = True
        elif arg in ["--build-only", "-b"]:
            build_only = True
        elif arg in ["--help", "-h", "help"]:
            print("""
Script de release CV cross-platform

USAGE:
  python release.py [VERSION] [OPTIONS]

ARGUMENTS:
  VERSION        Version a creer (ex: v1.2.3). Si omise, genere automatiquement

OPTIONS:
  --dry-run, -d     Simulation sans creation de tag
  --force, -f       Force la creation meme si le tag existe  
  --build-only, -b  Compile uniquement sans creer de release
  --help, -h        Affiche cette aide

EXEMPLES:
  python release.py                    # Version automatique
  python release.py v1.2.3            # Version specifique
  python release.py v1.2.3 --dry-run  # Simulation
  python release.py --build-only      # Compilation seulement

WORKFLOW:
  1. Verification des prerequis (Git, repository)
  2. Compilation des CV (francais + anglais)
  3. Creation du tag Git
  4. Push du tag (declenche GitHub Actions)
  5. GitHub Actions cree la release avec les PDF
            """)
            return
        elif not arg.startswith('-'):
            version = arg
        i += 1
    
    # Initialiser releaser
    releaser = CVReleaser()
    
    # Generer version si necessaire
    if not version:
        version = releaser.generate_version()
        releaser.log("INFO", f"Version auto-generee: {version}")
    
    releaser.log("INFO", f"Debut release {version}")
    
    # Verifier prerequis
    if not releaser.check_prerequisites():
        sys.exit(1)
    
    # Compiler CV
    if not releaser.build_cvs():
        sys.exit(1)
    
    # Si build-only, s'arreter
    if build_only:
        releaser.log("SUCCESS", "Compilation terminee (mode build-only)")
        return
    
    # Creer release
    if releaser.create_release(version, dry_run, force):
        releaser.log("SUCCESS", f"Release {version} terminee!")
    else:
        releaser.log("ERROR", "Echec creation release")
        sys.exit(1)

if __name__ == "__main__":
    main()
