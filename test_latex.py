#!/usr/bin/env python3
"""
Script de test LaTeX pour diagnostiquer MiKTeX
Samuel SIKATI KENMOGNE

Usage: python test_latex.py
"""

import os
import sys
import subprocess
import tempfile
from pathlib import Path
import platform

def test_latex_basic():
    """Test de base de LaTeX"""
    print("=== TEST LATEX BASIQUE ===")
    
    # Créer un document minimal
    test_content = r"""
\documentclass{article}
\usepackage[utf8]{inputenc}
\begin{document}
Test de compilation LaTeX minimal.

Caractères spéciaux: éàçù

Date: \today
\end{document}
"""
    
    # Créer un fichier temporaire
    with tempfile.NamedTemporaryFile(mode='w', suffix='.tex', delete=False, encoding='utf-8') as f:
        f.write(test_content)
        test_file = f.name
    
    test_path = Path(test_file)
    test_dir = test_path.parent
    test_name = test_path.stem
    
    print(f"Fichier test: {test_file}")
    
    try:
        # Test avec xelatex
        cmd = ["xelatex", "-interaction=nonstopmode", "-output-directory", str(test_dir), test_path.name]
        print(f"Commande: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            cwd=test_dir,
            capture_output=True,
            text=True,
            timeout=60,
            encoding='utf-8',
            errors='ignore'
        )
        
        print(f"Code de retour: {result.returncode}")
        
        if result.stdout:
            print("STDOUT (dernières lignes):")
            print('\n'.join(result.stdout.split('\n')[-10:]))
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        # Vérifier le PDF
        pdf_file = test_dir / f"{test_name}.pdf"
        if pdf_file.exists():
            size = pdf_file.stat().st_size
            print(f"✅ PDF généré: {pdf_file} ({size} bytes)")
            success = True
        else:
            print("❌ PDF non généré")
            success = False
        
        return success
        
    except subprocess.TimeoutExpired:
        print("❌ TIMEOUT: LaTeX trop lent")
        return False
    except Exception as e:
        print(f"❌ ERREUR: {e}")
        return False
    finally:
        # Nettoyer les fichiers temporaires
        try:
            test_path.unlink()
            for ext in ['.pdf', '.aux', '.log', '.out']:
                temp_file = test_dir / f"{test_name}{ext}"
                if temp_file.exists():
                    temp_file.unlink()
        except:
            pass

def test_xelatex_fonts():
    """Test des polices XeLaTeX"""
    print("\n=== TEST POLICES XELATEX ===")
    
    test_content = r"""
\documentclass{article}
\usepackage{fontspec}
\setmainfont{Arial}
\begin{document}
Test de polices XeLaTeX avec fontspec.

Texte avec Arial.

Caractères Unicode: ♠ ♣ ♥ ♦ α β γ
\end{document}
"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.tex', delete=False, encoding='utf-8') as f:
        f.write(test_content)
        test_file = f.name
    
    test_path = Path(test_file)
    test_dir = test_path.parent
    test_name = test_path.stem
    
    try:
        cmd = ["xelatex", "-interaction=nonstopmode", "-output-directory", str(test_dir), test_path.name]
        
        result = subprocess.run(
            cmd,
            cwd=test_dir,
            capture_output=True,
            text=True,
            timeout=60,
            encoding='utf-8',
            errors='ignore'
        )
        
        pdf_file = test_dir / f"{test_name}.pdf"
        if pdf_file.exists():
            print("✅ Polices XeLaTeX OK")
            success = True
        else:
            print("❌ Problème avec les polices")
            if result.stderr:
                print(f"Erreur: {result.stderr[:300]}")
            success = False
        
        return success
        
    except Exception as e:
        print(f"❌ ERREUR polices: {e}")
        return False
    finally:
        try:
            test_path.unlink()
            for ext in ['.pdf', '.aux', '.log', '.out']:
                temp_file = test_dir / f"{test_name}{ext}"
                if temp_file.exists():
                    temp_file.unlink()
        except:
            pass

def check_miktex_setup():
    """Vérifier la configuration MiKTeX"""
    print("\n=== VERIFICATION MIKTEX ===")
    
    # Vérifier xelatex
    try:
        result = subprocess.run(["xelatex", "--version"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            print(f"✅ XeLaTeX: {version}")
        else:
            print("❌ XeLaTeX non fonctionnel")
            return False
    except Exception as e:
        print(f"❌ XeLaTeX non trouvé: {e}")
        return False
    
    # Vérifier packages essentiels
    essential_packages = ["fontspec", "xunicode", "xltxtra"]
    
    for package in essential_packages:
        try:
            # Test rapide de package
            test_content = f"\\documentclass{{article}}\\usepackage{{{package}}}\\begin{{document}}\\end{{document}}"
            
            with tempfile.NamedTemporaryFile(mode='w', suffix='.tex', delete=False, encoding='utf-8') as f:
                f.write(test_content)
                test_file = f.name
            
            result = subprocess.run(
                ["xelatex", "-interaction=batchmode", test_file],
                capture_output=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print(f"✅ Package {package}: OK")
            else:
                print(f"❌ Package {package}: MANQUANT ou ERREUR")
            
            # Nettoyer
            Path(test_file).unlink()
            
        except Exception as e:
            print(f"❌ Test package {package}: {e}")
    
    return True

def main():
    """Test principal"""
    print("DIAGNOSTIC LATEX - Windows/MiKTeX")
    print("=" * 40)
    
    # Infos système
    print(f"OS: {platform.system()} {platform.release()}")
    print(f"Python: {sys.version}")
    print(f"Répertoire de travail: {Path.cwd()}")
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: LaTeX de base
    if test_latex_basic():
        tests_passed += 1
    
    # Test 2: Polices XeLaTeX
    if test_xelatex_fonts():
        tests_passed += 1
    
    # Test 3: Configuration MiKTeX
    if check_miktex_setup():
        tests_passed += 1
    
    print(f"\n=== RESULTAT FINAL ===")
    print(f"Tests réussis: {tests_passed}/{total_tests}")
    
    if tests_passed == total_tests:
        print("✅ LaTeX fonctionne correctement!")
        print("Votre problème vient probablement des fichiers CV eux-mêmes.")
        print("Essayez: python cv.py debug fr")
    elif tests_passed > 0:
        print("⚠️ LaTeX fonctionne partiellement")
        print("Recommandations:")
        print("1. Réinstaller MiKTeX en mode utilisateur")
        print("2. Mettre à jour tous les packages")
        print("3. Redémarrer Windows")
    else:
        print("❌ LaTeX ne fonctionne pas")
        print("Recommandations:")
        print("1. Désinstaller MiKTeX complètement")
        print("2. Redémarrer Windows") 
        print("3. Réinstaller MiKTeX: https://miktex.org/download")
        print("4. Choisir 'Install for current user'")
    
    print("\nPour plus d'aide:")
    print("- Consultez TROUBLESHOOTING-WINDOWS.md")
    print("- Utilisez: python cv.py debug fr")

if __name__ == "__main__":
    main()
