#!/bin/bash
# Notion Bot API Deployment Script
# This script automates the deployment of the Notion Bot API application

set -e  # Exit immediately if a command exits with a non-zero status

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default configuration
ENVIRONMENT="dev"
DOCKER_COMPOSE_FILE="docker-compose.yml"
DOCKER_COMPOSE_PROD_FILE="docker-compose.prod.yml"
ENV_FILE=".env"

# Function to print colored output
print_info() {
    printf "${BLUE}INFO:${NC} $1\n"
}

print_success() {
    printf "${GREEN}SUCCESS:${NC} $1\n"
}

print_warn() {
    printf "${YELLOW}WARN:${NC} $1\n"
}

print_error() {
    printf "${RED}ERROR:${NC} $1\n"
}

# Function to check prerequisites
check_prerequisites() {
    print_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker before running this script."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose before running this script."
        exit 1
    fi
    
    # Check for .env file
    if [ ! -f "$ENV_FILE" ]; then
        print_info "Environment file ($ENV_FILE) not found. Creating from example..."
        if [ -f "$ENV_FILE.example" ]; then
            cp "$ENV_FILE.example" "$ENV_FILE"
            print_success "Created $ENV_FILE from example. Please update it with your Notion API key before deployment."
            exit 0
        else
            print_error "Neither $ENV_FILE nor $ENV_FILE.example found. Cannot proceed."
            exit 1
        fi
    fi
    
    print_success "All prerequisites met."
}

# Function to validate environment configuration
validate_env() {
    print_info "Validating environment configuration..."
    
    # Check if NOTION_API_KEY is set in .env file
    if ! grep -q "^NOTION_API_KEY=" "$ENV_FILE" || grep -q "^NOTION_API_KEY=$" "$ENV_FILE" || grep -q "^NOTION_API_KEY=secret_" "$ENV_FILE"; then
        print_warn "NOTION_API_KEY is not set or has default value in $ENV_FILE"
        read -p "Do you want to continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_info "Please update $ENV_FILE with your Notion API key and run again."
            exit 1
        fi
    fi
    
    print_success "Environment configuration validated."
}

# Function to build and start services
deploy_services() {
    print_info "Building and starting Notion Bot API services..."
    
    if [ "$ENVIRONMENT" = "prod" ]; then
        COMPOSE_FILE="$DOCKER_COMPOSE_PROD_FILE"
        COMPOSE_ENV_FILE="$ENV_FILE.prod"
        if [ ! -f "$COMPOSE_ENV_FILE" ]; then
            print_error "Production environment file $COMPOSE_ENV_FILE not found."
            exit 1
        fi
        print_info "Using production compose file: $COMPOSE_FILE with environment: $COMPOSE_ENV_FILE"
        docker-compose -f "$COMPOSE_FILE" --env-file "$COMPOSE_ENV_FILE" up -d --build
    else
        print_info "Using development compose file: $DOCKER_COMPOSE_FILE"
        docker-compose -f "$DOCKER_COMPOSE_FILE" up -d --build
    fi
    
    print_success "Services started. Waiting for health check..."
    
    # Wait for services to be healthy
    local max_attempts=30
    local attempt=1
    while [ $attempt -le $max_attempts ]; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            print_success "API is healthy after $attempt attempts."
            break
        fi
        print_info "Waiting for API to be healthy... ($attempt/$max_attempts)"
        sleep 10
        attempt=$((attempt + 1))
    done
    
    if [ $attempt -gt $max_attempts ]; then
        print_error "API did not become healthy within the timeout period."
        docker-compose logs
        exit 1
    fi
}

# Function to run tests to verify deployment
verify_deployment() {
    print_info "Verifying deployment..."
    
    # Test health endpoint
    if curl -s http://localhost:8000/health | grep -q "healthy"; then
        print_success "Health check passed."
    else
        print_error "Health check failed."
        exit 1
    fi
    
    # Test root endpoint
    if curl -s http://localhost:8000/ | grep -q "Notion Bot API"; then
        print_success "Root endpoint check passed."
    else
        print_error "Root endpoint check failed."
        exit 1
    fi
    
    # Check if Docker services are running
    if docker-compose ps | grep -q "Up"; then
        print_success "All services are running."
    else
        print_error "Some services may not be running properly."
        docker-compose ps
        exit 1
    fi
}

# Function to display deployment information
display_info() {
    print_success "=== Notion Bot API Deployment Complete ==="
    echo
    print_info "API Endpoints:"
    print_info "  - Main API: http://localhost:8000"
    print_info "  - API Documentation: http://localhost:8000/docs"
    print_info "  - Health Check: http://localhost:8000/health"
    echo
    print_info "Docker Services Status:"
    docker-compose ps
    echo
    print_info "To view logs: docker-compose logs -f"
    print_info "To stop services: docker-compose down"
    echo
    print_success "Deployment completed successfully!"
}

# Function to display help
display_help() {
    echo "Notion Bot API Deployment Script"
    echo
    echo "Usage: $0 [OPTIONS]"
    echo
    echo "Options:"
    echo "  -h, --help     Display this help message"
    echo "  -e, --env      Environment to deploy (dev/prod) - default: dev"
    echo "  --stop         Stop running services"
    echo "  --restart      Restart services"
    echo "  --logs         View service logs"
    echo "  --status       Check service status"
    echo
    echo "Examples:"
    echo "  $0                    # Deploy in development mode"
    echo "  $0 -e prod           # Deploy in production mode"
    echo "  $0 --stop            # Stop services"
    echo "  $0 --restart         # Restart services"
    echo "  $0 --logs            # View logs"
    echo
}

# Main function to handle command line arguments
main() {
    local action="deploy"
    
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -e|--env)
                ENVIRONMENT="$2"
                shift 2
                ;;
            --stop)
                action="stop"
                shift
                ;;
            --restart)
                action="restart"
                shift
                ;;
            --logs)
                action="logs"
                shift
                ;;
            --status)
                action="status"
                shift
                ;;
            -h|--help)
                display_help
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                display_help
                exit 1
                ;;
        esac
    done
    
    # Execute the appropriate action
    case $action in
        deploy)
            print_info "Starting Notion Bot API deployment in $ENVIRONMENT mode..."
            check_prerequisites
            validate_env
            deploy_services
            verify_deployment
            display_info
            ;;
        stop)
            print_info "Stopping Notion Bot API services..."
            docker-compose down
            print_success "Services stopped."
            ;;
        restart)
            print_info "Restarting Notion Bot API services..."
            docker-compose down
            main deploy  # Recursive call to deploy after stopping
            ;;
        logs)
            print_info "Showing service logs..."
            docker-compose logs -f
            ;;
        status)
            print_info "Checking service status..."
            docker-compose ps
            ;;
        *)
            print_error "Unknown action: $action"
            exit 1
            ;;
    esac
}

# Run the main function with all arguments
main "$@"