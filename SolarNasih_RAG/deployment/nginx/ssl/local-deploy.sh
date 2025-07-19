# Local development deployment script using Docker Compose

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="deployment/docker/docker-compose.prod.yml"
ENV_FILE=".env"

echo -e "${BLUE}🏠 RAG Multimodal System - Local Deployment${NC}"
echo -e "${BLUE}============================================${NC}"

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
    
    # Check if docker is installed
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi
    
    # Check if docker-compose is installed
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed"
        exit 1
    fi
    
    # Check if .env file exists
    if [ ! -f "$ENV_FILE" ]; then
        print_warning ".env file not found, copying from .env.example"
        cp .env.example .env
        print_warning "Please edit .env file with your API keys before continuing"
        read -p "Press Enter when ready..."
    fi
    
    print_status "Prerequisites check completed"
}

# Build images
build_images() {
    echo -e "${BLUE}🏗️  Building Docker images...${NC}"
    
    docker-compose -f $COMPOSE_FILE build --no-cache
    
    print_status "Images built successfully"
}

# Start services
start_services() {
    echo -e "${BLUE}🚀 Starting services...${NC}"
    
    # Start infrastructure services first
    docker-compose -f $COMPOSE_FILE up -d qdrant redis postgres
    
    # Wait for infrastructure to be ready
    echo "Waiting for infrastructure services..."
    sleep 30
    
    # Start application services
    docker-compose -f $COMPOSE_FILE up -d api frontend nginx
    
    # Start monitoring (optional)
    docker-compose -f $COMPOSE_FILE up -d prometheus grafana
    
    print_status "All services started"
}

# Stop services
stop_services() {
    echo -e "${BLUE}🛑 Stopping services...${NC}"
    
    docker-compose -f $COMPOSE_FILE down
    
    print_status "Services stopped"
}

# Show status
show_status() {
    echo -e "${BLUE}📊 Service Status${NC}"
    
    docker-compose -f $COMPOSE_FILE ps
}

# Show logs
show_logs() {
    local service=${1:-}
    
    if [ -z "$service" ]; then
        docker-compose -f $COMPOSE_FILE logs --tail=50 -f
    else
        docker-compose -f $COMPOSE_FILE logs --tail=50 -f $service
    fi
}

# Clean up
cleanup() {
    echo -e "${BLUE}🧹 Cleaning up...${NC}"
    
    # Stop and remove containers
    docker-compose -f $COMPOSE_FILE down -v
    
    # Remove images (optional)
    read -p "Remove Docker images? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        docker-compose -f $COMPOSE_FILE down --rmi all
    fi
    
    print_status "Cleanup completed"
}

# Health check
health_check() {
    echo -e "${BLUE}🏥 Performing health checks...${NC}"
    
    # Check API health
    if curl -f http://localhost:8000/health/ >/dev/null 2>&1; then
        print_status "API is healthy"
    else
        print_error "API health check failed"
    fi
    
    # Check Frontend
    if curl -f http://localhost:8501/_stcore/health >/dev/null 2>&1; then
        print_status "Frontend is healthy"
    else
        print_error "Frontend health check failed"
    fi
    
    # Check Qdrant
    if curl -f http://localhost:6333/health >/dev/null 2>&1; then
        print_status "Qdrant is healthy"
    else
        print_error "Qdrant health check failed"
    fi
    
    # Check Redis
    if docker-compose -f $COMPOSE_FILE exec redis redis-cli ping >/dev/null 2>&1; then
        print_status "Redis is healthy"
    else
        print_error "Redis health check failed"
    fi
}

# Initialize system
initialize() {
    echo -e "${BLUE}🔧 Initializing system...${NC}"
    
    # Wait for services to be ready
    echo "Waiting for services to be ready..."
    sleep 60
    
    # Run database migrations
    docker-compose -f $COMPOSE_FILE exec api python scripts/migrate_db.py
    
    # Download models if needed
    docker-compose -f $COMPOSE_FILE exec api python scripts/install_models.py
    
    print_status "System initialized"
}

# Monitor resources
monitor() {
    echo -e "${BLUE}📊 Resource Monitoring${NC}"
    
    # Show container resource usage
    docker stats --no-stream $(docker-compose -f $COMPOSE_FILE ps -q)
}

# Backup data
backup() {
    echo -e "${BLUE}💾 Backing up data...${NC}"
    
    BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p $BACKUP_DIR
    
    # Backup Qdrant data
    docker run --rm -v rag_qdrant_data:/source -v $(pwd)/$BACKUP_DIR:/backup alpine tar czf /backup/qdrant_data.tar.gz -C /source .
    
    # Backup PostgreSQL data
    docker-compose -f $COMPOSE_FILE exec postgres pg_dump -U raguser rag_multimodal > $BACKUP_DIR/postgres_backup.sql
    
    print_status "Backup completed: $BACKUP_DIR"
}

# Restore data
restore() {
    local backup_dir=$1
    
    if [ -z "$backup_dir" ]; then
        print_error "Please specify backup directory"
        exit 1
    fi
    
    echo -e "${BLUE}♻️  Restoring data from $backup_dir...${NC}"
    
    # Stop services
    docker-compose -f $COMPOSE_FILE down
    
    # Restore Qdrant data
    if [ -f "$backup_dir/qdrant_data.tar.gz" ]; then
        docker run --rm -v rag_qdrant_data:/target -v $(pwd)/$backup_dir:/backup alpine tar xzf /backup/qdrant_data.tar.gz -C /target
    fi
    
    # Start services
    start_services
    
    # Restore PostgreSQL data
    if [ -f "$backup_dir/postgres_backup.sql" ]; then
        sleep 30  # Wait for postgres to be ready
        docker-compose -f $COMPOSE_FILE exec -T postgres psql -U raguser rag_multimodal < $backup_dir/postgres_backup.sql
    fi
    
    print_status "Restore completed"
}

# Help function
show_help() {
    echo "RAG Multimodal System - Local Deployment Script"
    echo ""
    echo "Usage: $0 [COMMAND] [OPTIONS]"
    echo ""
    echo "Commands:"
    echo "  start       Build and start all services"
    echo "  stop        Stop all services"
    echo "  restart     Restart all services"
    echo "  status      Show service status"
    echo "  logs        Show logs (optionally for specific service)"
    echo "  health      Perform health checks"
    echo "  init        Initialize system (run after first start)"
    echo "  monitor     Show resource usage"
    echo "  backup      Backup system data"
    echo "  restore     Restore system data"
    echo "  cleanup     Stop services and clean up"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start"
    echo "  $0 logs api"
    echo "  $0 restore backups/20231201_120000"
}

# Parse command line arguments
case "${1:-start}" in
    "start")
        check_prerequisites
        build_images
        start_services
        echo -e "${GREEN}🎉 System started successfully!${NC}"
        echo -e "${BLUE}Access points:${NC}"
        echo "Frontend: http://localhost:8501"
        echo "API: http://localhost:8000"
        echo "API Docs: http://localhost:8000/docs"
        echo "Qdrant: http://localhost:6333"
        echo "Grafana: http://localhost:3000 (admin/admin123)"
        echo "Prometheus: http://localhost:9090"
        ;;
    "stop")
        stop_services
        ;;
    "restart")
        stop_services
        sleep 5
        start_services
        ;;
    "status")
        show_status
        ;;
    "logs")
        show_logs $2
        ;;
    "health")
        health_check
        ;;
    "init")
        initialize
        ;;
    "monitor")
        monitor
        ;;
    "backup")
        backup
        ;;
    "restore")
        restore $2
        ;;
    "cleanup")
        cleanup
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