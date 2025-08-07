#!/bin/bash

# ========================================
# SOLAR NASIH - Script de Déploiement Complet
# ========================================

set -e  # Arrêter en cas d'erreur

# Couleurs pour l'affichage
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages
print_message() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Bannière
print_banner() {
    echo "============================================================"
    echo "🚀 SOLAR NASIH - Déploiement Complet"
    echo "============================================================"
    echo "Ce script déploie tous les composants :"
    echo "• SMA (Solar Management Assistant)"
    echo "• RAG (Retrieval-Augmented Generation)"
    echo "• Frontend (React/TypeScript)"
    echo "============================================================"
}

# Vérification des prérequis
check_prerequisites() {
    print_message "Vérification des prérequis..."
    
    # Vérifier Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker n'est pas installé"
        exit 1
    fi
    
    # Vérifier Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose n'est pas installé"
        exit 1
    fi
    
    # Vérifier les répertoires
    if [ ! -d "SolarNasih_SMA" ]; then
        print_error "Répertoire SolarNasih_SMA non trouvé"
        exit 1
    fi
    
    if [ ! -d "SolarNasih_RAG" ]; then
        print_error "Répertoire SolarNasih_RAG non trouvé"
        exit 1
    fi
    
    if [ ! -d "SolarNasih_Template" ]; then
        print_error "Répertoire SolarNasih_Template non trouvé"
        exit 1
    fi
    
    print_success "Tous les prérequis sont satisfaits"
}

# Configuration de l'environnement
setup_environment() {
    print_message "Configuration de l'environnement..."
    
    # Créer le fichier .env s'il n'existe pas
    if [ ! -f ".env" ]; then
        if [ -f "SolarNasih_Deploiement_Complet/env.example" ]; then
            cp SolarNasih_Deploiement_Complet/env.example .env
            print_success "Fichier .env créé à partir du template"
            print_warning "N'oubliez pas de configurer vos clés API dans .env"
        else
            print_error "Fichier env.example non trouvé"
            exit 1
        fi
    else
        print_message "Fichier .env existe déjà"
    fi
}

# Déploiement Docker
deploy_docker() {
    print_message "Déploiement avec Docker Compose..."
    
    cd SolarNasih_Deploiement_Complet
    
    # Arrêter les services existants
    print_message "Arrêt des services existants..."
    docker-compose down 2>/dev/null || true
    
    # Construire et démarrer les services
    print_message "Construction et démarrage des services..."
    docker-compose up -d --build
    
    # Attendre que les services démarrent
    print_message "Attente du démarrage des services..."
    sleep 30
    
    # Vérifier l'état des services
    print_message "Vérification de l'état des services..."
    docker-compose ps
    
    cd ..
    
    print_success "Déploiement Docker terminé"
}

# Déploiement Render
deploy_render() {
    print_message "Préparation du déploiement Render..."
    
    # Vérifier que le script Python existe
    if [ -f "SolarNasih_Deploiement_Complet/deploy_render_complete.py" ]; then
        print_message "Exécution du script de déploiement Render..."
        python3 SolarNasih_Deploiement_Complet/deploy_render_complete.py
    else
        print_error "Script de déploiement Render non trouvé"
        exit 1
    fi
}

# Vérification des services
check_services() {
    print_message "Vérification des services..."
    
    # Vérifier SMA
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_success "SMA API est accessible"
    else
        print_warning "SMA API n'est pas accessible"
    fi
    
    # Vérifier RAG
    if curl -s http://localhost:8001/health > /dev/null 2>&1; then
        print_success "RAG API est accessible"
    else
        print_warning "RAG API n'est pas accessible"
    fi
    
    # Vérifier Frontend
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        print_success "Frontend est accessible"
    else
        print_warning "Frontend n'est pas accessible"
    fi
}

# Affichage des URLs
show_urls() {
    echo ""
    echo "============================================================"
    echo "🌐 URLs des services"
    echo "============================================================"
    echo "Frontend : http://localhost:3000"
    echo "SMA API  : http://localhost:8000"
    echo "RAG API  : http://localhost:8001"
    echo "Qdrant   : http://localhost:6333"
    echo "Redis    : redis://localhost:6379"
    echo ""
    echo "Documentation :"
    echo "SMA Docs : http://localhost:8000/docs"
    echo "RAG Docs : http://localhost:8001/docs"
    echo "============================================================"
}

# Menu principal
show_menu() {
    echo ""
    echo "============================================================"
    echo "🎯 CHOIX DE DÉPLOIEMENT"
    echo "============================================================"
    echo "1. Déploiement Docker local"
    echo "2. Déploiement Render (Cloud)"
    echo "3. Vérification des services"
    echo "4. Arrêt des services"
    echo "5. Logs des services"
    echo "6. Quitter"
    echo "============================================================"
}

# Gestion des logs
show_logs() {
    cd SolarNasih_Deploiement_Complet
    
    echo ""
    echo "============================================================"
    echo "📋 LOGS DES SERVICES"
    echo "============================================================"
    echo "1. Logs SMA"
    echo "2. Logs RAG"
    echo "3. Logs Frontend"
    echo "4. Logs Qdrant"
    echo "5. Logs Redis"
    echo "6. Tous les logs"
    echo "============================================================"
    
    read -p "Choisissez une option (1-6) : " log_choice
    
    case $log_choice in
        1) docker-compose logs -f solar-nasih-sma ;;
        2) docker-compose logs -f solar-nasih-rag ;;
        3) docker-compose logs -f solar-nasih-frontend ;;
        4) docker-compose logs -f solar-nasih-qdrant ;;
        5) docker-compose logs -f solar-nasih-redis ;;
        6) docker-compose logs -f ;;
        *) print_error "Option invalide" ;;
    esac
    
    cd ..
}

# Fonction principale
main() {
    print_banner
    check_prerequisites
    setup_environment
    
    while true; do
        show_menu
        read -p "Choisissez une option (1-6) : " choice
        
        case $choice in
            1)
                deploy_docker
                show_urls
                ;;
            2)
                deploy_render
                ;;
            3)
                check_services
                show_urls
                ;;
            4)
                print_message "Arrêt des services..."
                cd SolarNasih_Deploiement_Complet
                docker-compose down
                cd ..
                print_success "Services arrêtés"
                ;;
            5)
                show_logs
                ;;
            6)
                print_success "Au revoir !"
                exit 0
                ;;
            *)
                print_error "Option invalide"
                ;;
        esac
        
        echo ""
        read -p "Appuyez sur Entrée pour continuer..."
    done
}

# Exécution du script
main "$@"
