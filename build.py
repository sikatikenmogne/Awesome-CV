#!/usr/bin/env python3
"""
Script de compilation CV cross-platform
Samuel SIKATI KENMOGNE

Usage: python build.py [command]
"""

import os
import sys
import json
import subprocess
import shutil
from pathlib import Path
import platform

class CVBuilder:
    def __init__(self, config_path="config.json"):
        self.config_path = config_path
        self.config = self.load_config()
        self.is_windows = platform.system().lower() == "windows"
        
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
        prefix = {"INFO": "INFO", "SUCCESS": "SUCCESS", "ERROR": "ERROR", "WARNING": "WARNING"}
        print(f"[{prefix.get(level, level)}] {message}")
    
    def check_latex(self):
        """Verifie LaTeX"""
        compiler = self.config["compilation"]["latex_compiler"]
        if not shutil.which(compiler):
            self.log("ERROR", f"{compiler} non installe")
            if self.is_windows:
                self.log("INFO", "Installez MiKTeX: https://miktex.org/download")
            else:
                self.log("INFO", "Installez: sudo apt-get install texlive-xetex texlive-fonts-recommended")
            return False
        
        # Test version
        try:
            result = subprocess.run([compiler, "--version"], capture_output=True, text=True, timeout=10)
            version = result.stdout.split('\n')[0] if result.stdout else "version inconnue"
            self.log("SUCCESS", f"{compiler}: {version.strip()}")
            return True
        except (subprocess.SubprocessError, subprocess.TimeoutExpired):
            self.log("WARNING", f"{compiler} installe mais version indeterminee")
            return True
    
    def create_dirs(self):
        """Cree les repertoires de sortie"""
        dirs = set()
        
        # Repertoires principaux
        for file_config in self.config["compilation"]["files"].values():
            dirs.add(file_config["output_dir"])
        
        # Repertoires additionnels
        for file_config in self.config["compilation"].get("additional_files", []):
            if file_config.get("enabled", False):
                dirs.add(file_config["output_dir"])
        
        for directory in dirs:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def compile_file(self, file_config, name):
        """Compile un fichier"""
        source = file_config["source"]
        output_dir = file_config["output_dir"]
        output_name = file_config["output_name"]
        
        if not Path(source).exists():
            self.log("ERROR", f"Source manquante: {source}")
            return False
        
        self.log("INFO", f"Compilation {name}: {source}")
        
        # Preparation commande
        compiler = self.config["compilation"]["latex_compiler"]
        flags = self.config["compilation"]["latex_flags"]
        
        source_path = Path(source)
        source_dir = source_path.parent
        filename = source_path.name
        
        # Chemin de sortie absolu pour eviter les problemes Windows
        output_dir_abs = Path(output_dir).resolve()
        
        cmd = [compiler] + flags + [f"-output-directory={output_dir_abs}", filename]
        
        try:
            # Execution - NE PAS utiliser check=True pour MiKTeX
            result = subprocess.run(
                cmd, 
                cwd=source_dir, 
                capture_output=True, 
                text=True,
                timeout=120,
                encoding='utf-8',
                errors='ignore'
            )
            
            # Verification du code de retour et des messages
            stderr_lower = result.stderr.lower() if result.stderr else ""
            
            # Ignorer les avertissements de securite MiKTeX
            miktex_warnings = [
                "security risk: running with elevated privileges",
                "miktex-dvipdfmx: security risk",
                "security warning"
            ]
            
            is_miktex_warning_only = any(warning in stderr_lower for warning in miktex_warnings)
            
            # Verifier si c'est une vraie erreur (pas juste des avertissements MiKTeX)
            real_errors = [
                "fatal error", "emergency stop", "! error", "compilation failed",
                "file not found", "undefined control sequence"
            ]
            
            has_real_error = any(error in stderr_lower for error in real_errors) if result.stderr else False
            
            # Si le code de retour n'est pas 0 mais que c'est juste des avertissements MiKTeX, continuer
            if result.returncode != 0 and not is_miktex_warning_only:
                if has_real_error:
                    self.log("ERROR", f"Erreur LaTeX dans {name}")
                    if result.stderr:
                        print(f"STDERR: {result.stderr[:800]}...")
                    return False
                elif not is_miktex_warning_only:
                    self.log("ERROR", f"Echec compilation {name} (code: {result.returncode})")
                    if result.stderr:
                        print(f"STDERR: {result.stderr[:500]}...")
                    return False
            
            # Afficher les avertissements MiKTeX mais continuer
            if is_miktex_warning_only:
                self.log("WARNING", "Avertissements de securite MiKTeX detectes (ignores)")
            
            # Verification fichier genere
            temp_name = filename.replace('.tex', '.pdf')
            temp_pdf = output_dir_abs / temp_name
            final_pdf = output_dir_abs / output_name
            
            # Debug: lister les fichiers dans le repertoire de sortie
            if not temp_pdf.exists():
                self.log("INFO", f"Recherche de PDF dans: {output_dir_abs}")
                pdf_files = list(output_dir_abs.glob("*.pdf"))
                if pdf_files:
                    self.log("INFO", f"PDF trouves: {[f.name for f in pdf_files]}")
                    # Prendre le premier PDF trouve
                    temp_pdf = pdf_files[0]
                else:
                    self.log("ERROR", f"Aucun PDF genere dans {output_dir_abs}")
                    return False
            
            if temp_pdf.exists():
                if temp_pdf.name != output_name:
                    self.log("INFO", f"Renommage: {temp_pdf.name} -> {output_name}")
                    try:
                        shutil.copy2(temp_pdf, final_pdf)
                    except Exception as e:
                        self.log("WARNING", f"Echec renommage: {e}")
                        # Si le renommage echoue, au moins le PDF existe
                        if temp_pdf.name != output_name:
                            final_pdf = temp_pdf
                
                self.log("SUCCESS", f"PDF genere: {final_pdf.name}")
                return True
            else:
                self.log("ERROR", f"PDF non trouve apres compilation: {temp_name}")
                return False
                
        except subprocess.TimeoutExpired:
            self.log("ERROR", f"Timeout compilation {name}")
            return False
        except Exception as e:
            self.log("ERROR", f"Erreur inattendue lors de la compilation {name}: {e}")
            return False
    
    def build_single(self, file_key):
        """Compile un seul fichier"""
        if not self.config:
            return False
            
        files = self.config["compilation"]["files"]
        if file_key not in files:
            self.log("ERROR", f"Fichier inconnu: {file_key}")
            self.log("INFO", f"Disponibles: {', '.join(files.keys())}")
            return False
        
        self.create_dirs()
        return self.compile_file(files[file_key], file_key)
    
    def build_all(self):
        """Compile tous les fichiers actifs"""
        if not self.config:
            return False
            
        if not self.check_latex():
            return False
        
        self.create_dirs()
        
        success = True
        compiled = 0
        total = 0
        
        # Fichiers principaux
        for name, file_config in self.config["compilation"]["files"].items():
            total += 1
            if self.compile_file(file_config, name):
                compiled += 1
            else:
                success = False
        
        # Fichiers additionnels actifs
        for file_config in self.config["compilation"].get("additional_files", []):
            if file_config.get("enabled", False):
                total += 1
                if self.compile_file(file_config, file_config["name"]):
                    compiled += 1
                else:
                    success = False
        
        self.log("INFO", f"Compilation terminee: {compiled}/{total}")
        if success:
            self.log("SUCCESS", "Tous les fichiers compiles avec succes")
        else:
            self.log("ERROR", "Certains fichiers ont echoue")
        
        return success
    
    def clean_temp(self):
        """Nettoie les fichiers temporaires"""
        extensions = ["*.aux", "*.log", "*.out", "*.synctex.gz", "*.fdb_latexmk", "*.fls", "*.xdv"]
        
        cleaned = 0
        for ext in extensions:
            for temp_file in Path(".").rglob(ext):
                try:
                    temp_file.unlink()
                    cleaned += 1
                except OSError:
                    pass
        
        self.log("SUCCESS", f"Fichiers temporaires supprimes: {cleaned}")
    
    def clean_all(self):
        """Nettoyage complet"""
        self.clean_temp()
        
        # Supprimer repertoires de sortie
        dirs_to_clean = set()
        for file_config in self.config["compilation"]["files"].values():
            dirs_to_clean.add(file_config["output_dir"])
        
        for directory in dirs_to_clean:
            dir_path = Path(directory)
            if dir_path.exists():
                try:
                    shutil.rmtree(dir_path)
                    self.log("SUCCESS", f"Supprime: {directory}")
                except OSError as e:
                    self.log("WARNING", f"Impossible de supprimer {directory}: {e}")
    
    def debug_compilation(self, file_key):
        """Mode debug pour diagnostiquer les problemes de compilation"""
        if not self.config:
            return False
            
        files = self.config["compilation"]["files"]
        if file_key not in files:
            self.log("ERROR", f"Fichier inconnu: {file_key}")
            return False
        
        file_config = files[file_key]
        source = file_config["source"]
        output_dir = file_config["output_dir"]
        
        print(f"\n=== DEBUG COMPILATION {file_key} ===")
        
        # Verifications prealables
        print(f"Source: {source}")
        print(f"Source existe: {Path(source).exists()}")
        print(f"Output dir: {output_dir}")
        print(f"Output dir existe: {Path(output_dir).exists()}")
        
        if not Path(source).exists():
            print("ERREUR: Fichier source manquant!")
            return False
        
        # Preparation commande
        compiler = self.config["compilation"]["latex_compiler"]
        flags = self.config["compilation"]["latex_flags"]
        
        source_path = Path(source)
        source_dir = source_path.parent
        filename = source_path.name
        output_dir_abs = Path(output_dir).resolve()
        
        cmd = [compiler] + flags + [f"-output-directory={output_dir_abs}", filename]
        
        print(f"Commande: {' '.join(cmd)}")
        print(f"Repertoire de travail: {source_dir}")
        print(f"Repertoire de sortie: {output_dir_abs}")
        
        # Execution avec output en temps reel
        print(f"\n--- EXECUTION ---")
        try:
            # Creer le repertoire de sortie
            output_dir_abs.mkdir(parents=True, exist_ok=True)
            
            process = subprocess.Popen(
                cmd,
                cwd=source_dir,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            stdout, stderr = process.communicate(timeout=120)
            
            print("STDOUT:")
            print(stdout[-1000:] if len(stdout) > 1000 else stdout)  # Dernieres 1000 chars
            
            if stderr:
                print("\nSTDERR:")
                print(stderr[-1000:] if len(stderr) > 1000 else stderr)
            
            print(f"\nCode de retour: {process.returncode}")
            
            # Verification fichiers generes
            print(f"\n--- FICHIERS GENERES ---")
            if output_dir_abs.exists():
                pdf_files = list(output_dir_abs.glob("*.pdf"))
                all_files = list(output_dir_abs.glob("*"))
                
                print(f"Tous les fichiers: {[f.name for f in all_files]}")
                print(f"Fichiers PDF: {[f.name for f in pdf_files]}")
                
                if pdf_files:
                    for pdf in pdf_files:
                        size = pdf.stat().st_size
                        print(f"  {pdf.name}: {size} bytes")
                        
                    return True
                else:
                    print("Aucun PDF genere")
                    return False
            else:
                print(f"Repertoire de sortie n'existe pas: {output_dir_abs}")
                return False
                
        except subprocess.TimeoutExpired:
            print("TIMEOUT: Compilation trop longue")
            return False
        except Exception as e:
            print(f"ERREUR: {e}")
            return False
        """Liste les fichiers configurables"""
        if not self.config:
            return
            
        print("\n=== FICHIERS CONFIGURABLES ===")
        
        files = self.config["compilation"]["files"]
        print(f"\nFichiers principaux ({len(files)}):")
        for name, config in files.items():
            status = "OK" if Path(config["source"]).exists() else "MANQUANT"
            print(f"  {name}: {config['source']} [{status}]")
            print(f"    -> {config['output_name']}")
        
        additional = self.config["compilation"].get("additional_files", [])
        if additional:
            enabled = [f for f in additional if f.get("enabled", False)]
            print(f"\nFichiers additionnels actifs ({len(enabled)}):")
            for config in enabled:
                status = "OK" if Path(config["source"]).exists() else "MANQUANT"
                print(f"  {config['name']}: {config['source']} [{status}]")
                print(f"    -> {config['output_name']}")
            
            disabled = [f for f in additional if not f.get("enabled", False)]
            if disabled:
                print(f"\nFichiers additionnels desactives ({len(disabled)}):")
                for config in disabled:
                    print(f"  {config['name']}: {config['source']} [DESACTIVE]")

    def list_files(self):
        """Liste les fichiers configurables"""
        if not self.config:
            return
            
        print("\n=== FICHIERS CONFIGURABLES ===")
        
        files = self.config["compilation"]["files"]
        print(f"\nFichiers principaux ({len(files)}):")
        for name, config in files.items():
            status = "OK" if Path(config["source"]).exists() else "MANQUANT"
            print(f"  {name}: {config['source']} [{status}]")
            print(f"    -> {config['output_name']}")
        
        additional = self.config["compilation"].get("additional_files", [])
        if additional:
            enabled = [f for f in additional if f.get("enabled", False)]
            print(f"\nFichiers additionnels actifs ({len(enabled)}):")
            for config in enabled:
                status = "OK" if Path(config["source"]).exists() else "MANQUANT"
                print(f"  {config['name']}: {config['source']} [{status}]")
                print(f"    -> {config['output_name']}")
            
            disabled = [f for f in additional if not f.get("enabled", False)]
            if disabled:
                print(f"\nFichiers additionnels desactives ({len(disabled)}):")
                for config in disabled:
                    print(f"  {config['name']}: {config['source']} [DESACTIVE]")

def main():
    """Point d'entree principal"""
    command = sys.argv[1] if len(sys.argv) > 1 else "help"
    
    builder = CVBuilder()
    
    if command in ["help", "--help", "-h"]:
        print("""
Script de compilation CV cross-platform

USAGE:
  python build.py [COMMAND]

COMMANDS:
  all, build     Compile tous les fichiers actifs
  fr, french     Compile le CV francais
  en, english    Compile le CV anglais  
  clean          Supprime fichiers temporaires
  distclean      Nettoyage complet
  list           Liste fichiers configurables
  check          Verifie installation LaTeX
  debug [file]   Mode debug pour diagnostiquer les problemes
  help           Affiche cette aide

EXEMPLES:
  python build.py all
  python build.py fr
  python build.py debug fr     # Mode debug pour le CV francais
  python build.py clean
        """)
        return
    
    # Commande debug speciale
    if command == "debug":
        file_key = sys.argv[2] if len(sys.argv) > 2 else "cv_fr"
        success = builder.debug_compilation(file_key)
        sys.exit(0 if success else 1)
    
    commands = {
        "all": builder.build_all,
        "build": builder.build_all,
        "fr": lambda: builder.build_single("cv_fr"),
        "french": lambda: builder.build_single("cv_fr"),
        "en": lambda: builder.build_single("cv_en"),
        "english": lambda: builder.build_single("cv_en"),
        "clean": builder.clean_temp,
        "distclean": builder.clean_all,
        "list": builder.list_files,
        "check": builder.check_latex
    }
    
    if command in commands:
        if command in ["all", "build", "fr", "french", "en", "english"]:
            success = commands[command]()
            sys.exit(0 if success else 1)
        else:
            commands[command]()
    else:
        print(f"Commande inconnue: {command}")
        print("Utilisez: python build.py help")
        sys.exit(1)

if __name__ == "__main__":
    main()