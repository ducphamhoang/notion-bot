#!/bin/bash
# Deployment script for Notion Bot API

set -e  # Exit on error

echo "🚀 Starting Notion Bot API Deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Check if .env exists
if [ ! -f .env ]; then
    print_warning ".env file not found. Creating from .env.example..."
    cp .env.example .env
    print_error "⚠️  IMPORTANT: Please update .env file with your actual NOTION_API_KEY before continuing!"
    echo ""
    echo "Edit the .env file and set:"
    echo "  NOTION_API_KEY=secret_your_actual_notion_token"
    echo ""
    read -p "Press Enter after updating .env file..."
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

print_status "Docker is running"

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    print_warning "docker-compose command not found, using 'docker compose' instead"
    DOCKER_COMPOSE="docker compose"
else
    DOCKER_COMPOSE="docker-compose"
fi

# Stop existing containers
echo ""
echo "📦 Stopping existing containers..."
$DOCKER_COMPOSE down

# Build the application
echo ""
echo "🔨 Building application Docker image..."
$DOCKER_COMPOSE build app

# Start services
echo ""
echo "🚀 Starting services..."
$DOCKER_COMPOSE up -d

# Wait for services to be healthy
echo ""
echo "⏳ Waiting for services to be healthy..."
sleep 5

# Check MongoDB health
echo ""
echo "Checking MongoDB..."
if docker exec notion-bot-mongodb mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
    print_status "MongoDB is healthy"
else
    print_warning "MongoDB health check failed, but may still be starting..."
fi

# Wait for app to be ready
echo ""
echo "Checking API health..."
MAX_RETRIES=10
RETRY_COUNT=0

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -sf http://localhost:8000/health > /dev/null 2>&1; then
        print_status "API is healthy and responding"
        break
    fi
    RETRY_COUNT=$((RETRY_COUNT + 1))
    echo "Waiting for API to be ready... ($RETRY_COUNT/$MAX_RETRIES)"
    sleep 3
done

if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then
    print_error "API health check failed after $MAX_RETRIES attempts"
    echo ""
    echo "Checking logs..."
    $DOCKER_COMPOSE logs app
    exit 1
fi

# Show running containers
echo ""
echo "📊 Running containers:"
$DOCKER_COMPOSE ps

# Show API info
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
print_status "✅ Deployment successful!"
echo ""
echo "🌐 API Endpoints:"
echo "   • API Base:    http://localhost:8000"
echo "   • Swagger UI:  http://localhost:8000/docs"
echo "   • ReDoc:       http://localhost:8000/redoc"
echo "   • Health:      http://localhost:8000/health"
echo ""
echo "📊 MongoDB:"
echo "   • Host:        localhost:27017"
echo "   • Database:    notion-bot"
echo "   • Username:    admin"
echo "   • Password:    password123"
echo ""
echo "📝 Useful commands:"
echo "   • View logs:       $DOCKER_COMPOSE logs -f"
echo "   • View app logs:   $DOCKER_COMPOSE logs -f app"
echo "   • Stop services:   $DOCKER_COMPOSE down"
echo "   • Restart app:     $DOCKER_COMPOSE restart app"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
