#!/bin/bash
#
# Script de démarrage simplifié pour Freebox Auto-Mute
# Usage: ./run.sh
#

set -e

# Couleurs
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔═══════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║      🎬 Freebox Auto-Mute - Démarrage            ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════╝${NC}"
echo ""

# Vérifier si uv est installé
if command -v uv &> /dev/null; then
    echo -e "${GREEN}✅ uv détecté${NC}"
    echo -e "${BLUE}🚀 Lancement avec uv...${NC}"
    echo ""
    uv run python -m src.freetv
else
    # Fallback sur Python standard
    echo -e "${YELLOW}⚠️  uv non trouvé, utilisation de python3${NC}"
    
    # Vérifier si venv existe
    if [ -d ".venv" ]; then
        echo -e "${GREEN}✅ venv détecté${NC}"
        source .venv/bin/activate
    else
        echo -e "${YELLOW}⚠️  Pas de venv trouvé${NC}"
        echo -e "${BLUE}💡 Conseil: Installez uv ou créez un venv${NC}"
        echo ""
    fi
    
    echo -e "${BLUE}🚀 Lancement avec python3...${NC}"
    echo ""
    python3 -m src.freetv
fi
