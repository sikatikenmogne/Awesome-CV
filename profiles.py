#!/usr/bin/env python3
"""
Script de gestion des profils de compilation
Utilise la configuration avancée pour compiler des sets spécifiques de documents

Usage: python profiles.py [profile_name] [options]
"""

import os
import sys
import json
import click
from pathlib import Path

class ProfileManager:
    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        self.config = self.load_config()
        
    def load_config(self):
        """Charge la configuration"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"ERROR: Fichier de configuration non trouve: {self.config_path}")
            return None
        except json.JSONDecodeError as e:
            print(f"ERROR: Erreur JSON: {e}")
            return None
    
    def list_profiles(self):
        """Liste les profils disponibles"""
        if not self.config:
            return
            
        print("=== PROFILS DE COMPILATION DISPONIBLES ===")
        
        # Profils de compilation
        build_profiles = self.config.get("build_profiles", {})
        if build_profiles:
            print("\nPROFILS DE BUILD:")
            for profile_name, profile_config in build_profiles.items():
                name = profile_config.get("name", profile_name)
                files = profile_config.get("files", [])
                print(f"  {profile_name}: {name}")
                print(f"    Fichiers: {', '.join(files)}")
                
                # Flags LaTeX spécifiques
                latex_flags = profile_config.get("latex_flags")
                if latex_flags:
                    print(f"    Flags LaTeX: {' '.join(latex_flags)}")
                print()
        
        # Sets de documents  
        document_sets = self.config.get("compilation", {}).get("document_sets", {})
        if document_sets:
            print("SETS DE DOCUMENTS:")
            for set_name, set_config in document_sets.items():
                name = set_config.get("name", set_name)
                files = set_config.get("files", [])
                description = set_config.get("description", "")
                
                print(f"  {set_name}: {name}")
                print(f"    Fichiers: {', '.join(files)}")
                if description:
                    print(f"    Description: {description}")
                print()
    
    def get_profile_files(self, profile_name):
        """Récupère la liste des fichiers pour un profil"""
        if not self.config:
            return []
            
        # Vérifier dans build_profiles
        build_profiles = self.config.get("build_profiles", {})
        if profile_name in build_profiles:
            return build_profiles[profile_name].get("files", [])
        
        # Vérifier dans document_sets
        document_sets = self.config.get("compilation", {}).get("document_sets", {})
        if profile_name in document_sets:
            return document_sets[profile_name].get("files", [])
        
        return []
    
    def get_profile_latex_flags(self, profile_name):
        """Récupère les flags LaTeX pour un profil"""
        if not self.config:
            return []
            
        build_profiles = self.config.get("build_profiles", {})
        if profile_name in build_profiles:
            return build_profiles[profile_name].get("latex_flags", [])
        
        # Retourner les flags par défaut si pas de flags spécifiques
        return self.config.get("compilation", {}).get("latex_flags", [])
    
    def compile_profile(self, profile_name):
        """Compile un profil spécifique"""
        if not self.config:
            print("ERROR: Configuration invalide")
            return False
            
        files_to_compile = self.get_profile_files(profile_name)
        if not files_to_compile:
            print(f"ERROR: Profil non trouve ou vide: {profile_name}")
            return False
        
        print(f"=== COMPILATION DU PROFIL: {profile_name} ===")
        print(f"Fichiers à compiler: {', '.join(files_to_compile)}")
        
        # Importer le builder
        try:
            from build import CVBuilder
            builder = CVBuilder(self.config_path)
        except ImportError:
            print("ERROR: Module build.py non disponible")
            return False
        
        # Modifier temporairement les flags LaTeX si nécessaire
        profile_flags = self.get_profile_latex_flags(profile_name)
        original_flags = builder.config["compilation"]["latex_flags"]
        
        if profile_flags != original_flags:
            print(f"Utilisation des flags spécifiques: {' '.join(profile_flags)}")
            builder.config["compilation"]["latex_flags"] = profile_flags
        
        success = True
        compiled_count = 0
        
        # Compiler chaque fichier
        for file_key in files_to_compile:
            print(f"\n--- Compilation: {file_key} ---")
            if builder.compile_single_file(file_key):
                compiled_count += 1
                print(f"SUCCESS: {file_key} compilé")
            else:
                print(f"ERROR: Echec compilation {file_key}")
                success = False
        
        # Restaurer les flags originaux
        if profile_flags != original_flags:
            builder.config["compilation"]["latex_flags"] = original_flags
        
        print(f"\n=== RÉSULTAT ===")
        print(f"Fichiers compilés: {compiled_count}/{len(files_to_compile)}")
        
        if success:
            print("SUCCESS: Profil compilé avec succès!")
        else:
            print("ERROR: Certains fichiers ont échoué")
            
        return success
    
    def create_custom_profile(self, name, files, description=""):
        """Crée un profil personnalisé temporaire"""
        print(f"=== CRÉATION PROFIL PERSONNALISÉ: {name} ===")
        print(f"Fichiers: {', '.join(files)}")
        
        # Vérifier que les fichiers existent dans la config
        all_files = list(self.config.get("compilation", {}).get("files", {}).keys())
        additional_files = [f["name"] for f in self.config.get("compilation", {}).get("additional_files", []) 
                          if f.get("enabled", False)]
        all_files.extend(additional_files)
        
        invalid_files = [f for f in files if f not in all_files]
        if invalid_files:
            print(f"ERROR: Fichiers non trouvés dans la configuration: {', '.join(invalid_files)}")
            print(f"Fichiers disponibles: {', '.join(all_files)}")
            return False
        
        # Créer un profil temporaire
        temp_profile = {
            "name": name,
            "files": files,
            "description": description
        }
        
        # L'ajouter temporairement à la config
        if "build_profiles" not in self.config:
            self.config["build_profiles"] = {}
        
        self.config["build_profiles"][name] = temp_profile
        
        # Compiler
        success = self.compile_profile(name)
        
        # Nettoyer le profil temporaire
        del self.config["build_profiles"][name]
        
        return success
    
    def show_profile_help(self):
        """Affiche l'aide sur les profils"""
        print("""
=== AIDE - GESTION DES PROFILS ===

USAGE:
  python profiles.py [COMMANDE] [OPTIONS]

COMMANDES:
  list                    Liste tous les profils disponibles
  compile [profile]       Compile un profil spécifique
  create [name] [files]   Crée et compile un profil personnalisé
  help                    Affiche cette aide

EXEMPLES:
  python profiles.py list
  python profiles.py compile quick
  python profiles.py compile job_application
  python profiles.py create my_profile cv_fr,cover_letter_fr

PROFILS PRÉDÉFINIS COURANTS:
  quick           - Compilation rapide (CV seulement)
  complete        - Compilation complète (CV + lettres)
  job_application - Package de candidature
  portfolio       - Avec portfolio de projets

PERSONNALISATION:
  Les profils sont définis dans config.json sous:
  - "build_profiles" pour les profils de compilation
  - "document_sets" pour les sets de documents logiques

  Exemple de profil personnalisé dans config.json:
  "build_profiles": {
    "mon_profil": {
      "name": "Mon profil personnalisé",
      "files": ["cv_fr", "cover_letter_fr"],
      "latex_flags": ["-interaction=batchmode"]
    }
  }
        """)

@click.command()
@click.argument('command', default='help')
@click.argument('profile_or_files', default='', required=False)
@click.option('--config', '-c', default='config.json', help='Fichier de configuration')
@click.option('--description', '-d', default='', help='Description du profil personnalisé')
@click.option('--verbose', '-v', is_flag=True, help='Mode verbose')
def main(command, profile_or_files, config, description, verbose):
    """
    Gestionnaire de profils de compilation pour CV
    
    Permet de compiler des ensembles prédéfinis de documents selon
    différents profils (rapide, complet, candidature, etc.)
    """
    
    manager = ProfileManager(config)
    
    if command == 'list':
        manager.list_profiles()
        
    elif command == 'compile':
        if not profile_or_files:
            print("ERROR: Nom de profil requis")
            print("Usage: python profiles.py compile [profile_name]")
            print("Utilisez 'python profiles.py list' pour voir les profils disponibles")
            sys.exit(1)
        
        success = manager.compile_profile(profile_or_files)
        sys.exit(0 if success else 1)
        
    elif command == 'create':
        if not profile_or_files:
            print("ERROR: Nom et fichiers requis")
            print("Usage: python profiles.py create [name] [file1,file2,...]")
            sys.exit(1)
        
        # Parser les arguments pour profil personnalisé
        args = profile_or_files.split(',') if ',' in profile_or_files else [profile_or_files]
        profile_name = args[0]
        files = args[1:] if len(args) > 1 else []
        
        if not files:
            print("ERROR: Liste de fichiers requise")
            print("Exemple: python profiles.py create mon_profil cv_fr,cover_letter_fr")
            sys.exit(1)
        
        success = manager.create_custom_profile(profile_name, files, description)
        sys.exit(0 if success else 1)
        
    elif command == 'help':
        manager.show_profile_help()
        
    else:
        print(f"Commande inconnue: {command}")
        print("Commandes disponibles: list, compile, create, help")
        sys.exit(1)

if __name__ == "__main__":
    main()
