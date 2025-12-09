.PHONY: help run setup test clean install dev lint format check-deps

# Couleurs pour l'affichage
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

help: ## Affiche cette aide
	@echo "$(BLUE)╔═══════════════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║     🎬 Freebox Auto-Mute - Commandes Make        ║$(NC)"
	@echo "$(BLUE)╚═══════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(NC) %s\n", $$1, $$2}'
	@echo ""

run: ## Lance le programme principal
	@echo "$(BLUE)🚀 Lancement de Freebox Auto-Mute...$(NC)"
	@uv run python -m src.freetv

setup: ## Lance l'assistant de configuration
	@echo "$(BLUE)⚙️  Assistant de configuration...$(NC)"
	@uv run python scripts/setup_wizard.py

install: ## Installe les dépendances
	@echo "$(BLUE)📦 Installation des dépendances...$(NC)"
	@uv sync
	@echo "$(GREEN)✅ Installation terminée$(NC)"

dev: ## Installe les dépendances de développement
	@echo "$(BLUE)🔧 Installation des dépendances de développement...$(NC)"
	@uv sync --all-extras
	@echo "$(GREEN)✅ Installation terminée$(NC)"

test: ## Lance tous les tests
	@echo "$(BLUE)🧪 Lancement des tests...$(NC)"
	@uv run python tests/test_demute_fix.py
	@uv run python tests/test_basic.py
	@echo "$(GREEN)✅ Tous les tests sont passés$(NC)"

test-demute: ## Test de la correction de démutage
	@echo "$(BLUE)🧪 Test de la correction de démutage...$(NC)"
	@uv run python tests/test_demute_fix.py

debug-demute: ## Analyse les problèmes de démutage
	@echo "$(BLUE)🔍 Analyse des problèmes de démutage...$(NC)"
	@uv run python scripts/debug_demute.py

map-channels: ## Mapper les chaînes Freebox ↔ OQEE
	@echo "$(BLUE)📺 Mapping des chaînes...$(NC)"
	@uv run python scripts/channel_mapper.py

clean: ## Nettoie les fichiers temporaires
	@echo "$(BLUE)🧹 Nettoyage...$(NC)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type f -name "*.log" -delete 2>/dev/null || true
	@find . -type f -name "*_timestamp.json" -delete 2>/dev/null || true
	@find . -type f -name "player_status.json" -delete 2>/dev/null || true
	@echo "$(GREEN)✅ Nettoyage terminé$(NC)"

lint: ## Vérifie le code avec pylint
	@echo "$(BLUE)🔍 Analyse du code...$(NC)"
	@uv run pylint src/ scripts/ tests/ 2>/dev/null || echo "$(YELLOW)⚠️  pylint non installé$(NC)"

format: ## Formate le code avec black
	@echo "$(BLUE)✨ Formatage du code...$(NC)"
	@uv run black src/ scripts/ tests/ 2>/dev/null || echo "$(YELLOW)⚠️  black non installé$(NC)"

check-deps: ## Vérifie les dépendances
	@echo "$(BLUE)📦 Vérification des dépendances...$(NC)"
	@uv tree

compile: ## Compile le code Python
	@echo "$(BLUE)🔨 Compilation du code...$(NC)"
	@python3 -m py_compile src/freebox_auto_mute.py
	@python3 -m py_compile src/config.py
	@echo "$(GREEN)✅ Compilation réussie$(NC)"

info: ## Affiche les informations du projet
	@echo "$(BLUE)╔═══════════════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║           📊 Informations du Projet              ║$(NC)"
	@echo "$(BLUE)╚═══════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "  $(GREEN)Nom :$(NC) Freebox Auto-Mute"
	@echo "  $(GREEN)Version :$(NC) 2.0.0"
	@echo "  $(GREEN)Python :$(NC) $$(python3 --version)"
	@echo "  $(GREEN)Localisation :$(NC) $$(pwd)"
	@echo ""
	@echo "  $(YELLOW)Fichiers sources :$(NC)"
	@find src -name "*.py" -exec echo "    - {}" \;
	@echo ""
	@echo "  $(YELLOW)Scripts :$(NC)"
	@find scripts -name "*.py" -o -name "*.sh" | head -5 | xargs -I {} echo "    - {}"
	@echo ""

structure: ## Affiche la structure du projet
	@echo "$(BLUE)📁 Structure du projet :$(NC)"
	@tree -L 2 -I '__pycache__|.venv|*.pyc|uv.lock' --dirsfirst

quickstart: ## Installation rapide (tout en un)
	@echo "$(BLUE)╔═══════════════════════════════════════════════════╗$(NC)"
	@echo "$(BLUE)║        🚀 Installation Rapide Freebox Auto-Mute   ║$(NC)"
	@echo "$(BLUE)╚═══════════════════════════════════════════════════╝$(NC)"
	@echo ""
	@echo "$(YELLOW)1/3 Installation des dépendances...$(NC)"
	@$(MAKE) install
	@echo ""
	@echo "$(YELLOW)2/3 Compilation du code...$(NC)"
	@$(MAKE) compile
	@echo ""
	@echo "$(YELLOW)3/3 Configuration...$(NC)"
	@$(MAKE) setup
	@echo ""
	@echo "$(GREEN)✅ Installation terminée !$(NC)"
	@echo ""
	@echo "$(BLUE)Pour lancer le programme :$(NC)"
	@echo "  make run"

.DEFAULT_GOAL := help

run-pkg: ## Lance le package refactorisé
	@echo "$(BLUE)🚀 Lancement de Freebox Auto-Mute (Module)...$(NC)"
	@uv run python -m src.freetv
