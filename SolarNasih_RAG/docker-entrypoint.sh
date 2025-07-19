#!/bin/bash

# Script de démarrage pour Docker
echo "🚀 Démarrage du RAG Multimodal System..."

# Attendre que les services externes soient prêts
echo "⏳ Attente des services externes..."
sleep 10

# Démarrer l'API en arrière-plan
echo "🔧 Démarrage de l'API FastAPI..."
python run_api.py &
API_PID=$!

# Attendre que l'API soit prête
sleep 15

# Démarrer le frontend
echo "🌐 Démarrage du frontend Streamlit..."
python run_frontend.py &
FRONTEND_PID=$!

# Attendre que les processus se terminent
wait $API_PID $FRONTEND_PID 