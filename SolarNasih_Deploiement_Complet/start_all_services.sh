#!/bin/bash
# 🚀 SOLAR NASIH - Démarrage Unifié (Bash)
# Script pour démarrer tous les services avec une seule commande

set -e

echo "============================================================"
echo "🚀 SOLAR NASIH - Démarrage de Tous les Services"
echo "============================================================"

# Vérification des prérequis
echo "🔍 Vérification des prérequis..."

if [ ! -d "SolarNasih_SMA" ] || [ ! -d "SolarNasih_RAG" ] || [ ! -d "SolarNasih_Template" ]; then
    echo "❌ Erreur: Composants manquants"
    echo "   Assurez-vous d'être dans le répertoire racine du projet"
    exit 1
fi

echo "✅ Tous les composants trouvés"

# Installation des dépendances Python
echo "📦 Installation des dépendances unifiées..."
if python -m pip install -r SolarNasih_Deploiement_Complet/requirements_unified.txt; then
    echo "✅ Dépendances Python installées"
else
    echo "❌ Erreur lors de l'installation des dépendances Python"
    exit 1
fi

# Installation des dépendances Node.js
echo "📦 Installation des dépendances Node.js..."
cd SolarNasih_Template
if [ ! -d "node_modules" ]; then
    if npm install; then
        echo "✅ Dépendances Node.js installées"
    else
        echo "❌ Erreur lors de l'installation des dépendances Node.js"
        exit 1
    fi
else
    echo "✅ Dépendances Node.js déjà installées"
fi
cd ..

# Démarrage des services
echo "🚀 Démarrage de tous les services..."

# Démarrer Redis avec Docker (si disponible)
if command -v docker &> /dev/null; then
    if docker run --name solar-nasih-redis -p 6379:6379 -d redis:alpine 2>/dev/null; then
        echo "✅ Redis démarré avec Docker"
    else
        echo "⚠️ Redis déjà en cours d'exécution ou erreur Docker"
    fi
else
    echo "⚠️ Redis non disponible (Docker requis)"
fi

# Démarrer Qdrant avec Docker (si disponible)
if command -v docker &> /dev/null; then
    if docker run --name solar-nasih-qdrant -p 6333:6333 -p 6334:6334 -d qdrant/qdrant:latest 2>/dev/null; then
        echo "✅ Qdrant démarré avec Docker"
    else
        echo "⚠️ Qdrant déjà en cours d'exécution ou erreur Docker"
    fi
else
    echo "⚠️ Qdrant non disponible (Docker requis)"
fi

# Fonction pour arrêter tous les services
cleanup() {
    echo ""
    echo "🛑 Arrêt de tous les services..."
    
    # Arrêter les processus Python
    pkill -f "uvicorn main:app" || true
    pkill -f "uvicorn api_simple:app" || true
    
    # Arrêter le processus npm
    pkill -f "npm run dev" || true
    
    # Arrêter les conteneurs Docker
    docker stop solar-nasih-redis 2>/dev/null || true
    docker rm solar-nasih-redis 2>/dev/null || true
    docker stop solar-nasih-qdrant 2>/dev/null || true
    docker rm solar-nasih-qdrant 2>/dev/null || true
    
    echo "✅ Tous les services arrêtés"
    exit 0
}

# Configurer le gestionnaire de signal
trap cleanup SIGINT SIGTERM

# Démarrer SMA en arrière-plan
echo "🚀 Démarrage du service SMA..."
cd SolarNasih_SMA
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
SMA_PID=$!
cd ..

# Démarrer RAG en arrière-plan
echo "🤖 Démarrage du service RAG..."
cd SolarNasih_RAG
python -m uvicorn api_simple:app --host 0.0.0.0 --port 8001 --reload &
RAG_PID=$!
cd ..

# Démarrer Frontend en arrière-plan
echo "🌐 Démarrage du service Frontend..."
cd SolarNasih_Template
npm run dev &
FRONTEND_PID=$!
cd ..

# Attendre un peu pour que les services démarrent
sleep 5

echo ""
echo "============================================================"
echo "🎉 TOUS LES SERVICES SONT DÉMARRÉS !"
echo "============================================================"
echo ""
echo "📊 Services disponibles:"
echo "   • SMA API: http://localhost:8000"
echo "   • RAG API: http://localhost:8001"
echo "   • Frontend: http://localhost:5173"
echo "   • Redis: localhost:6379"
echo "   • Qdrant: localhost:6333"
echo ""
echo "📚 Documentation:"
echo "   • SMA API Docs: http://localhost:8000/docs"
echo "   • RAG API Docs: http://localhost:8001/docs"
echo ""
echo "🛑 Appuyez sur Ctrl+C pour arrêter tous les services"
echo "============================================================"

# Maintenir le script en vie
wait
