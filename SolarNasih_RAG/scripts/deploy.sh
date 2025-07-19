#!/bin/bash

# Script de déploiement pour RAG Multimodal System
set -e

echo "🚀 Déploiement du RAG Multimodal System..."

# Variables
PROJECT_NAME="rag-multimodal-system"
DOCKER_IMAGE="rag-multimodal:latest"
REGISTRY_URL="your-registry.azurecr.io"

# Couleurs pour les messages
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Fonction pour afficher les messages
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Vérifier les prérequis
check_prerequisites() {
    log_info "Vérification des prérequis..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker n'est pas installé"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose n'est pas installé"
        exit 1
    fi
    
    log_info "Prérequis vérifiés ✓"
}

# Construire l'image Docker
build_image() {
    log_info "Construction de l'image Docker..."
    docker build -t $DOCKER_IMAGE .
    log_info "Image construite ✓"
}

# Pousser l'image vers le registry (optionnel)
push_image() {
    if [ "$PUSH_IMAGE" = "true" ]; then
        log_info "Poussage de l'image vers le registry..."
        docker tag $DOCKER_IMAGE $REGISTRY_URL/$DOCKER_IMAGE
        docker push $REGISTRY_URL/$DOCKER_IMAGE
        log_info "Image poussée ✓"
    fi
}

# Déployer avec Docker Compose
deploy_local() {
    log_info "Déploiement local avec Docker Compose..."
    docker-compose up -d
    log_info "Déploiement local terminé ✓"
}

# Déployer sur AWS ECS
deploy_aws() {
    log_info "Déploiement sur AWS ECS..."
    
    # Vérifier AWS CLI
    if ! command -v aws &> /dev/null; then
        log_error "AWS CLI n'est pas installé"
        exit 1
    fi
    
    # Créer le cluster ECS
    aws ecs create-cluster --cluster-name rag-multimodal-cluster
    
    # Créer le service
    aws ecs create-service \
        --cluster rag-multimodal-cluster \
        --service-name rag-multimodal-service \
        --task-definition rag-multimodal-system \
        --desired-count 1
    
    log_info "Déploiement AWS terminé ✓"
}

# Déployer sur Azure
deploy_azure() {
    log_info "Déploiement sur Azure..."
    
    # Vérifier Azure CLI
    if ! command -v az &> /dev/null; then
        log_error "Azure CLI n'est pas installé"
        exit 1
    fi
    
    # Créer le groupe de ressources
    az group create --name rag-multimodal-rg --location eastus
    
    # Créer le container instance
    az container create \
        --resource-group rag-multimodal-rg \
        --name rag-multimodal-system \
        --image $REGISTRY_URL/$DOCKER_IMAGE \
        --ports 8000 8501 \
        --dns-name-label rag-multimodal \
        --environment-variables QDRANT_URL=http://qdrant:6333 REDIS_URL=redis://redis:6379
    
    log_info "Déploiement Azure terminé ✓"
}

# Fonction principale
main() {
    local target=${1:-local}
    
    case $target in
        "local")
            check_prerequisites
            build_image
            deploy_local
            ;;
        "aws")
            check_prerequisites
            build_image
            push_image
            deploy_aws
            ;;
        "azure")
            check_prerequisites
            build_image
            push_image
            deploy_azure
            ;;
        *)
            log_error "Cible de déploiement invalide: $target"
            echo "Usage: $0 [local|aws|azure]"
            exit 1
            ;;
    esac
    
    log_info "Déploiement terminé avec succès! 🎉"
}

# Exécuter le script
main "$@" 