#!/bin/bash

# RAG Multimodal System Deployment Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NAMESPACE="rag-multimodal"
DOCKER_REGISTRY="your-registry.com"
IMAGE_TAG="${1:-latest}"

echo -e "${BLUE}🚀 RAG Multimodal System Deployment${NC}"
echo -e "${BLUE}=====================================${NC}"

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    echo -e "${BLUE}🔍 Checking prerequisites...${NC}"
    
    # Check if kubectl is installed
    if ! command -v kubectl &> /dev/null; then
        print_error "kubectl is not installed"
        exit 1
    fi
    
    # Check if docker is installed
    if ! command -v docker &> /dev/null; then
        print_error "docker is not installed"
        exit 1
    fi
    
    # Check if helm is installed (optional)
    if command -v helm &> /dev/null; then
        print_status "helm is available"
    else
        print_warning "helm is not installed (optional)"
    fi
    
    print_status "Prerequisites check completed"
}

# Build Docker images
build_images() {
    echo -e "${BLUE}🏗️  Building Docker images...${NC}"
    
    # Build API image
    echo "Building API image..."
    docker build -f deployment/docker/Dockerfile -t $DOCKER_REGISTRY/rag-multimodal:$IMAGE_TAG .
    
    # Build Frontend image
    echo "Building Frontend image..."
    docker build -f deployment/docker/Dockerfile.frontend -t $DOCKER_REGISTRY/rag-multimodal-frontend:$IMAGE_TAG .
    
    print_status "Docker images built successfully"
}

# Push images to registry
push_images() {
    echo -e "${BLUE}📤 Pushing images to registry...${NC}"
    
    docker push $DOCKER_REGISTRY/rag-multimodal:$IMAGE_TAG
    docker push $DOCKER_REGISTRY/rag-multimodal-frontend:$IMAGE_TAG
    
    print_status "Images pushed to registry"
}

# Create namespace
create_namespace() {
    echo -e "${BLUE}📁 Creating namespace...${NC}"
    
    kubectl apply -f deployment/kubernetes/namespace.yaml
    
    print_status "Namespace created"
}

# Deploy to Kubernetes
deploy_kubernetes() {
    echo -e "${BLUE}☸️  Deploying to Kubernetes...${NC}"
    
    # Apply configurations in order
    kubectl apply -f deployment/kubernetes/configmap.yaml
    kubectl apply -f deployment/kubernetes/secrets.yaml
    kubectl apply -f deployment/kubernetes/persistent-volumes.yaml
    
    # Wait for PVCs to be bound
    echo "Waiting for persistent volumes..."
    kubectl wait --for=condition=Bound pvc --all -n $NAMESPACE --timeout=300s
    
    # Deploy services
    kubectl apply -f deployment/kubernetes/service.yaml
    
    # Deploy applications
    kubectl apply -f deployment/kubernetes/deployment.yaml
    
    # Deploy ingress
    kubectl apply -f deployment/kubernetes/ingress.yaml
    
    # Deploy HPA
    kubectl apply -f deployment/kubernetes/hpa.yaml
    
    print_status "Kubernetes deployment completed"
}

# Wait for deployments
wait_for_deployments() {
    echo -e "${BLUE}⏳ Waiting for deployments to be ready...${NC}"
    
    kubectl wait --for=condition=available --timeout=600s deployment --all -n $NAMESPACE
    
    print_status "All deployments are ready"
}

# Verify deployment
verify_deployment() {
    echo -e "${BLUE}🔍 Verifying deployment...${NC}"
    
    # Check pod status
    echo "Pod status:"
    kubectl get pods -n $NAMESPACE
    
    # Check service status
    echo -e "\nService status:"
    kubectl get services -n $NAMESPACE
    
    # Check ingress status
    echo -e "\nIngress status:"
    kubectl get ingress -n $NAMESPACE
    
    # Test health endpoints
    echo -e "\nTesting health endpoints..."
    API_SERVICE=$(kubectl get svc rag-multimodal-api-service -n $NAMESPACE -o jsonpath='{.spec.clusterIP}')
    if kubectl run test-pod --image=curlimages/curl:latest --rm -i --restart=Never -- curl -f http://$API_SERVICE:8000/health/; then
        print_status "API health check passed"
    else
        print_warning "API health check failed"
    fi
}

# Rollback deployment
rollback_deployment() {
    echo -e "${BLUE}🔄 Rolling back deployment...${NC}"
    
    kubectl rollout undo deployment/rag-multimodal-api -n $NAMESPACE
    kubectl rollout undo deployment/rag-multimodal-frontend -n $NAMESPACE
    
    print_status "Rollback completed"
}

# Clean up deployment
cleanup_deployment() {
    echo -e "${BLUE}🧹 Cleaning up deployment...${NC}"
    
    kubectl delete namespace $NAMESPACE --ignore-not-found=true
    
    print_status "Cleanup completed"
}

# Update deployment
update_deployment() {
    echo -e "${BLUE}🔄 Updating deployment...${NC}"
    
    # Update image tags in deployments
    kubectl set image deployment/rag-multimodal-api api=$DOCKER_REGISTRY/rag-multimodal:$IMAGE_TAG -n $NAMESPACE
    kubectl set image deployment/rag-multimodal-frontend frontend=$DOCKER_REGISTRY/rag-multimodal-frontend:$IMAGE_TAG -n $NAMESPACE
    
    # Wait for rollout
    kubectl rollout status deployment/rag-multimodal-api -n $NAMESPACE
    kubectl rollout status deployment/rag-multimodal-frontend -n $NAMESPACE
    
    print_status "Deployment updated"
}

# Main deployment function
deploy() {
    check_prerequisites
    build_images
    push_images
    create_namespace
    deploy_kubernetes
    wait_for_deployments
    verify_deployment
    
    echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
    echo -e "${BLUE}Access your application at:${NC}"
    echo "Frontend: http://$(kubectl get ingress rag-multimodal-ingress -n $NAMESPACE -o jsonpath='{.spec.rules[0].host}')"
    echo "API: http://$(kubectl get ingress rag-multimodal-ingress -n $NAMESPACE -o jsonpath='{.spec.rules[1].host}')"
}

# Help function
show_help() {
    echo "RAG Multimodal System Deployment Script"
    echo ""
    echo "Usage: $0 [COMMAND] [IMAGE_TAG]"
    echo ""
    echo "Commands:"
    echo "  deploy      Deploy the complete system (default)"
    echo "  build       Build Docker images only"
    echo "  push        Push images to registry"
    echo "  update      Update existing deployment"
    echo "  rollback    Rollback to previous version"
    echo "  verify      Verify current deployment"
    echo "  cleanup     Remove all resources"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 deploy latest"
    echo "  $0 update v1.2.0"
    echo "  $0 rollback"
}

# Parse command line arguments
case "${1:-deploy}" in
    "deploy")
        deploy
        ;;
    "build")
        check_prerequisites
        build_images
        ;;
    "push")
        push_images
        ;;
    "update")
        check_prerequisites
        build_images
        push_images
        update_deployment
        verify_deployment
        ;;
    "rollback")
        rollback_deployment
        ;;
    "verify")
        verify_deployment
        ;;
    "cleanup")
        cleanup_deployment
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
