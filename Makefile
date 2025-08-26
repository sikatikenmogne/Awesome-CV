# Makefile pour Awesome-CV Multi-langue avec Cover Letters
# Compatible Windows avec Git Bash / WSL / MSYS2

# Configuration
include custom/config.mk

# Détection de l'environnement Windows
ifeq ($(OS),Windows_NT)
    RM = del /Q
    RMR = rmdir /S /Q
    MKDIR = mkdir
    PATHSEP = \\
    SHELL = cmd
    # Utiliser Git Bash si disponible
    ifneq (,$(shell where bash 2>nul))
        SHELL = bash
        RM = rm -f
        RMR = rm -rf
        MKDIR = mkdir -p
        PATHSEP = /
    endif
else
    RM = rm -f
    RMR = rm -rf
    MKDIR = mkdir -p
    PATHSEP = /
endif

# Outils LaTeX
LATEX = xelatex
LATEXFLAGS = -synctex=1 -interaction=nonstopmode -file-line-error

# Dossiers
CUSTOM_DIR = custom
BUILD_DIR = $(CUSTOM_DIR)$(PATHSEP)build
OUTPUT_DIR = $(CUSTOM_DIR)$(PATHSEP)output

# Langues et documents
LANGUAGES = fr en
DOCS = cv resume
COVERLETTERS = ZENITY STARTUP TEMPLATE

# Noms de fichiers personnalisés
CV_FR_NAME = CV-$(AUTHOR_NAME)-$(TITLE_FR)-[FR].pdf
CV_EN_NAME = CV-$(AUTHOR_NAME)-$(TITLE_EN)-[EN].pdf
RESUME_FR_NAME = Resume-$(AUTHOR_NAME)-$(TITLE_FR_SHORT)-[FR].pdf
RESUME_EN_NAME = Resume-$(AUTHOR_NAME)-$(TITLE_EN_SHORT)-[EN].pdf

# Template pour cover letters
COVERLETTER_FR_TEMPLATE = CoverLetter-$(AUTHOR_NAME)-{COMPANY}-[FR].pdf
COVERLETTER_EN_TEMPLATE = CoverLetter-$(AUTHOR_NAME)-{COMPANY}-[EN].pdf

# Cibles principales
.PHONY: all clean help fr en cv resume coverletters build-dirs list-outputs

# Cible par défaut
all: build-dirs fr en
	@echo "Compilation terminée ! PDFs disponibles dans $(OUTPUT_DIR)"
	@echo ""
	@$(MAKE) list-outputs

# Aide sans icônes
help:
	@echo "Makefile Awesome-CV Multi-langue"
	@echo ""
	@echo "Cibles disponibles:"
	@echo "  all              - Compiler tout (FR + EN)"
	@echo "  fr               - Compiler versions françaises"
	@echo "  en               - Compiler versions anglaises" 
	@echo "  cv               - Compiler seulement les CV"
	@echo "  resume           - Compiler seulement les résumés"
	@echo "  coverletters     - Compiler toutes les cover letters"
	@echo "  coverletter-COMPANY - Compiler cover letter spécifique"
	@echo "  clean            - Nettoyer les fichiers temporaires"
	@echo "  clean-all        - Nettoyer tout"
	@echo "  list-outputs     - Lister les PDFs générés"
	@echo ""
	@echo "Cover letters disponibles: $(COVERLETTERS)"
	@echo ""
	@echo "Exemples:"
	@echo "  make fr                    # Version française complète"
	@echo "  make en                    # Version anglaise complète"
	@echo "  make coverletter-ZENITY    # Cover letter ZENITY (FR+EN)"
	@echo "  make coverletters          # Toutes les cover letters"

# Créer les dossiers nécessaires
build-dirs:
	@echo "Création des dossiers de build..."
	@$(MKDIR) "$(BUILD_DIR)" 2>nul || $(MKDIR) "$(BUILD_DIR)"
	@$(MKDIR) "$(OUTPUT_DIR)" 2>nul || $(MKDIR) "$(OUTPUT_DIR)"

# Compilation par langue
fr: build-dirs cv-fr resume-fr coverletters-fr
en: build-dirs cv-en resume-en coverletters-en

# Compilation par type de document
cv: cv-fr cv-en
resume: resume-fr resume-en
coverletters: coverletters-fr coverletters-en

# Cover letters par langue
coverletters-fr: $(addprefix coverletter-fr-,$(COVERLETTERS))
coverletters-en: $(addprefix coverletter-en-,$(COVERLETTERS))

# Cover letter spécifique (toutes langues)
coverletter-ZENITY: coverletter-fr-ZENITY coverletter-en-ZENITY
coverletter-STARTUP: coverletter-fr-STARTUP coverletter-en-STARTUP
coverletter-TEMPLATE: coverletter-fr-TEMPLATE coverletter-en-TEMPLATE

# Règles de compilation CV
cv-fr: build-dirs
	@echo "Compilation CV français..."
	@cd $(CUSTOM_DIR) && $(LATEX) $(LATEXFLAGS) -output-directory=../$(BUILD_DIR) fr/cv-fr.tex
	@cd $(CUSTOM_DIR) && $(LATEX) $(LATEXFLAGS) -output-directory=../$(BUILD_DIR) fr/cv-fr.tex
	@copy "$(BUILD_DIR)$(PATHSEP)cv-fr.pdf" "$(OUTPUT_DIR)$(PATHSEP)$(CV_FR_NAME)" >nul 2>&1 || cp "$(BUILD_DIR)/cv-fr.pdf" "$(OUTPUT_DIR)/$(CV_FR_NAME)"
	@echo "CV français généré: $(CV_FR_NAME)"

cv-en: build-dirs
	@echo "Compilation CV anglais..."
	@cd $(CUSTOM_DIR) && $(LATEX) $(LATEXFLAGS) -output-directory=../$(BUILD_DIR) en/cv-en.tex
	@cd $(CUSTOM_DIR) && $(LATEX) $(LATEXFLAGS) -output-directory=../$(BUILD_DIR) en/cv-en.tex
	@copy "$(BUILD_DIR)$(PATHSEP)cv-en.pdf" "$(OUTPUT_DIR)$(PATHSEP)$(CV_EN_NAME)" >nul 2>&1 || cp "$(BUILD_DIR)/cv-en.pdf" "$(OUTPUT_DIR)/$(CV_EN_NAME)"
	@echo "CV anglais généré: $(CV_EN_NAME)"

# Règles de compilation Resume
resume-fr: build-dirs
	@echo "Compilation résumé français..."
	@cd $(CUSTOM_DIR) && $(LATEX) $(LATEXFLAGS) -output-directory=../$(BUILD_DIR) fr/resume-fr.tex
	@cd $(CUSTOM_DIR) && $(LATEX) $(LATEXFLAGS) -output-directory=../$(BUILD_DIR) fr/resume-fr.tex
	@copy "$(BUILD_DIR)$(PATHSEP)resume-fr.pdf" "$(OUTPUT_DIR)$(PATHSEP)$(RESUME_FR_NAME)" >nul 2>&1 || cp "$(BUILD_DIR)/resume-fr.pdf" "$(OUTPUT_DIR)/$(RESUME_FR_NAME)"
	@echo "Résumé français généré: $(RESUME_FR_NAME)"

resume-en: build-dirs
	@echo "Compilation résumé anglais..."
	@cd $(CUSTOM_DIR) && $(LATEX) $(LATEXFLAGS) -output-directory=../$(BUILD_DIR) en/resume-en.tex
	@cd $(CUSTOM_DIR) && $(LATEX) $(LATEXFLAGS) -output-directory=../$(BUILD_DIR) en/resume-en.tex
	@copy "$(BUILD_DIR)$(PATHSEP)resume-en.pdf" "$(OUTPUT_DIR)$(PATHSEP)$(RESUME_EN_NAME)" >nul 2>&1 || cp "$(BUILD_DIR)/resume-en.pdf" "$(OUTPUT_DIR)/$(RESUME_EN_NAME)"
	@echo "Résumé anglais généré: $(RESUME_EN_NAME)"

# Règles de compilation Cover Letters françaises
coverletter-fr-ZENITY: build-dirs
	@echo "Compilation cover letter ZENITY français..."
	@cd $(CUSTOM_DIR) && $(LATEX) $(LATEXFLAGS) -output-directory=../$(BUILD_DIR) fr/coverletter/coverletter-ZENITY.tex
	@cd $(CUSTOM_DIR) && $(LATEX) $(LATEXFLAGS) -output-directory=../$(BUILD_DIR) fr/coverletter/coverletter-ZENITY.tex
	@copy "$(BUILD_DIR)$(PATHSEP)coverletter-ZENITY.pdf" "$(OUTPUT_DIR)$(PATHSEP)CoverLetter-$(AUTHOR_NAME)-ZENITY-[FR].pdf" >nul 2>&1 || cp "$(BUILD_DIR)/coverletter-ZENITY.pdf" "$(OUTPUT_DIR)/CoverLetter-$(AUTHOR_NAME)-ZENITY-[FR].pdf"
	@echo "Cover letter ZENITY français générée"

coverletter-fr-STARTUP: build-dirs
	@echo "Compilation cover letter STARTUP français..."
	@cd $(CUSTOM_DIR) && $(LATEX) $(LATEXFLAGS) -output-directory=../$(BUILD_DIR) fr/coverletter/coverletter-STARTUP.tex
	@cd $(CUSTOM_DIR) && $(LATEX) $(LATEXFLAGS) -output-directory=../$(BUILD_DIR) fr/coverletter/coverletter-STARTUP.tex
	@copy "$(BUILD_DIR)$(PATHSEP)coverletter-STARTUP.pdf" "$(OUTPUT_DIR)$(PATHSEP)CoverLetter-$(AUTHOR_NAME)-STARTUP-[FR].pdf" >nul 2>&1 || cp "$(BUILD_DIR)/coverletter-STARTUP.pdf" "$(OUTPUT_DIR)/CoverLetter-$(AUTHOR_NAME)-STARTUP-[FR].pdf"
	@echo "Cover letter STARTUP français générée"

coverletter-fr-TEMPLATE: build-dirs
	@echo "Compilation cover letter TEMPLATE français..."
	@cd $(CUSTOM_DIR) && $(LATEX) $(LATEXFLAGS) -output-directory=../$(BUILD_DIR) fr/coverletter/coverletter-TEMPLATE.tex
	@cd $(CUSTOM_DIR) && $(LATEX) $(LATEXFLAGS) -output-directory=../$(BUILD_DIR) fr/coverletter/coverletter-TEMPLATE.tex
	@copy "$(BUILD_DIR)$(PATHSEP)coverletter-TEMPLATE.pdf" "$(OUTPUT_DIR)$(PATHSEP)CoverLetter-$(AUTHOR_NAME)-TEMPLATE-[FR].pdf" >nul 2>&1 || cp "$(BUILD_DIR)/coverletter-TEMPLATE.pdf" "$(OUTPUT_DIR)/CoverLetter-$(AUTHOR_NAME)-TEMPLATE-[FR].pdf"
	@echo "Cover letter TEMPLATE français générée"

# Règles de compilation Cover Letters anglaises
coverletter-en-ZENITY: build-dirs
	@echo "Compilation cover letter ZENITY anglais..."
	@cd $(CUSTOM_DIR) && $(LATEX) $(LATEXFLAGS) -output-directory=../$(BUILD_DIR) en/coverletter/coverletter-ZENITY.tex
	@cd $(CUSTOM_DIR) && $(LATEX) $(LATEXFLAGS) -output-directory=../$(BUILD_DIR) en/coverletter/coverletter-ZENITY.tex
	@copy "$(BUILD_DIR)$(PATHSEP)coverletter-ZENITY.pdf" "$(OUTPUT_DIR)$(PATHSEP)CoverLetter-$(AUTHOR_NAME)-ZENITY-[EN].pdf" >nul 2>&1 || cp "$(BUILD_DIR)/coverletter-ZENITY.pdf" "$(OUTPUT_DIR)/CoverLetter-$(AUTHOR_NAME)-ZENITY-[EN].pdf"
	@echo "Cover letter ZENITY anglaise générée"

coverletter-en-STARTUP: build-dirs
	@echo "Compilation cover letter STARTUP anglais..."
	@cd $(CUSTOM_DIR) && $(LATEX) $(LATEXFLAGS) -output-directory=../$(BUILD_DIR) en/coverletter/coverletter-STARTUP.tex
	@cd $(CUSTOM_DIR) && $(LATEX) $(LATEXFLAGS) -output-directory=../$(BUILD_DIR) en/coverletter/coverletter-STARTUP.tex
	@copy "$(BUILD_DIR)$(PATHSEP)coverletter-STARTUP.pdf" "$(OUTPUT_DIR)$(PATHSEP)CoverLetter-$(AUTHOR_NAME)-STARTUP-[EN].pdf" >nul 2>&1 || cp "$(BUILD_DIR)/coverletter-STARTUP.pdf" "$(OUTPUT_DIR)/CoverLetter-$(AUTHOR_NAME)-STARTUP-[EN].pdf"
	@echo "Cover letter STARTUP anglaise générée"

coverletter-en-TEMPLATE: build-dirs
	@echo "Compilation cover letter TEMPLATE anglais..."
	@cd $(CUSTOM_DIR) && $(LATEX) $(LATEXFLAGS) -output-directory=../$(BUILD_DIR) en/coverletter/coverletter-TEMPLATE.tex
	@cd $(CUSTOM_DIR) && $(LATEX) $(LATEXFLAGS) -output-directory=../$(BUILD_DIR) en/coverletter/coverletter-TEMPLATE.tex
	@copy "$(BUILD_DIR)$(PATHSEP)coverletter-TEMPLATE.pdf" "$(OUTPUT_DIR)$(PATHSEP)CoverLetter-$(AUTHOR_NAME)-TEMPLATE-[EN].pdf" >nul 2>&1 || cp "$(BUILD_DIR)/coverletter-TEMPLATE.pdf" "$(OUTPUT_DIR)/CoverLetter-$(AUTHOR_NAME)-TEMPLATE-[EN].pdf"
	@echo "Cover letter TEMPLATE anglaise générée"

# Lister les PDFs générés
list-outputs:
	@echo "PDFs générés dans $(OUTPUT_DIR):"
	@dir "$(OUTPUT_DIR)\*.pdf" /B 2>nul || ls "$(OUTPUT_DIR)"/*.pdf 2>/dev/null || echo "Aucun PDF trouvé"

# Nettoyage
clean:
	@echo "Nettoyage des fichiers temporaires..."
	@$(RMR) "$(BUILD_DIR)" 2>nul || $(RMR) "$(BUILD_DIR)" || echo "Dossier build déjà propre"
	@echo "Nettoyage terminé"

clean-all: clean
	@echo "Nettoyage complet..."
	@$(RMR) "$(OUTPUT_DIR)" 2>nul || $(RMR) "$(OUTPUT_DIR)" || echo "Dossier output déjà propre"
	@echo "Nettoyage complet terminé"

# Surveillance automatique simplifiée pour Windows
watch:
	@echo "Surveillance des fichiers (Entrée pour recompiler, Ctrl+C pour quitter)..."
	@while true; do \
		echo "Appuyez sur Entrée pour recompiler..."; \
		read line; \
		$(MAKE) all; \
	done