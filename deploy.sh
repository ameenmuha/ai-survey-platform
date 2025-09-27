#!/bin/bash

# AI-Powered Multilingual Survey Platform Deployment Script
# This script automates the deployment process for both frontend and backend

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
FRONTEND_URL=""
BACKEND_URL=""
DEPLOYMENT_TYPE=""

# Function to print colored output
print_status() {
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

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    # Check if git is installed
    if ! command -v git &> /dev/null; then
        print_error "Git is not installed. Please install Git first."
        exit 1
    fi
    
    print_success "All prerequisites are satisfied"
}

# Function to build Docker images
build_images() {
    print_status "Building Docker images..."
    
    # Build backend image
    print_status "Building backend image..."
    docker build -t ai-survey-backend ./backend
    
    # Build frontend image
    print_status "Building frontend image..."
    docker build -t ai-survey-frontend ./frontend
    
    print_success "Docker images built successfully"
}

# Function to deploy to local environment
deploy_local() {
    print_status "Deploying to local environment..."
    
    # Start services with docker-compose
    docker-compose up -d
    
    print_success "Local deployment completed"
    print_status "Frontend: http://localhost:3000"
    print_status "Backend API: http://localhost:8000"
    print_status "API Documentation: http://localhost:8000/docs"
}

# Function to deploy to production
deploy_production() {
    print_status "Deploying to production environment..."
    
    # Check if environment variables are set
    if [ -z "$FRONTEND_URL" ] || [ -z "$BACKEND_URL" ]; then
        print_error "Please set FRONTEND_URL and BACKEND_URL environment variables"
        exit 1
    fi
    
    # Create production docker-compose file
    cat > docker-compose.prod.yml << EOF
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: ai_survey_db
      POSTGRES_USER: \${POSTGRES_USER:-postgres}
      POSTGRES_PASSWORD: \${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    restart: unless-stopped

  backend:
    image: ai-survey-backend
    environment:
      - DATABASE_URL=\${DATABASE_URL}
      - REDIS_URL=\${REDIS_URL}
      - SECRET_KEY=\${SECRET_KEY}
      - DEBUG=False
      - ENVIRONMENT=production
      - CORS_ORIGINS=["${FRONTEND_URL}"]
      - GOOGLE_AI_API_KEY=\${GOOGLE_AI_API_KEY}
      - OPENAI_API_KEY=\${OPENAI_API_KEY}
      - TWILIO_ACCOUNT_SID=\${TWILIO_ACCOUNT_SID}
      - TWILIO_AUTH_TOKEN=\${TWILIO_AUTH_TOKEN}
      - TWILIO_PHONE_NUMBER=\${TWILIO_PHONE_NUMBER}
    depends_on:
      - postgres
      - redis
    restart: unless-stopped

  frontend:
    image: ai-survey-frontend
    environment:
      - NEXT_PUBLIC_API_URL=${BACKEND_URL}
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  postgres_data:
EOF
    
    # Deploy with production compose file
    docker-compose -f docker-compose.prod.yml up -d
    
    print_success "Production deployment completed"
    print_status "Frontend: ${FRONTEND_URL}"
    print_status "Backend API: ${BACKEND_URL}"
}

# Function to deploy to cloud platforms
deploy_cloud() {
    case $DEPLOYMENT_TYPE in
        "render")
            deploy_render
            ;;
        "railway")
            deploy_railway
            ;;
        "heroku")
            deploy_heroku
            ;;
        "vercel")
            deploy_vercel
            ;;
        *)
            print_error "Unknown deployment type: $DEPLOYMENT_TYPE"
            exit 1
            ;;
    esac
}

# Function to deploy to Render
deploy_render() {
    print_status "Deploying to Render..."
    
    # Check if Render CLI is installed
    if ! command -v render &> /dev/null; then
        print_warning "Render CLI not found. Please install it or deploy manually through Render dashboard."
        print_status "Visit: https://render.com/docs/deploy-fastapi"
        return
    fi
    
    # Deploy backend
    render deploy --service ai-survey-backend
    
    # Deploy frontend
    render deploy --service ai-survey-frontend
    
    print_success "Render deployment completed"
}

# Function to deploy to Railway
deploy_railway() {
    print_status "Deploying to Railway..."
    
    # Check if Railway CLI is installed
    if ! command -v railway &> /dev/null; then
        print_warning "Railway CLI not found. Please install it or deploy manually through Railway dashboard."
        print_status "Visit: https://docs.railway.app/deploy/deployments"
        return
    fi
    
    # Deploy to Railway
    railway up
    
    print_success "Railway deployment completed"
}

# Function to deploy to Heroku
deploy_heroku() {
    print_status "Deploying to Heroku..."
    
    # Check if Heroku CLI is installed
    if ! command -v heroku &> /dev/null; then
        print_warning "Heroku CLI not found. Please install it or deploy manually through Heroku dashboard."
        print_status "Visit: https://devcenter.heroku.com/articles/getting-started-with-python"
        return
    fi
    
    # Create Heroku apps if they don't exist
    heroku create ai-survey-backend || true
    heroku create ai-survey-frontend || true
    
    # Deploy backend
    cd backend
    git init
    git add .
    git commit -m "Deploy backend to Heroku"
    heroku git:remote -a ai-survey-backend
    git push heroku main
    cd ..
    
    # Deploy frontend
    cd frontend
    git init
    git add .
    git commit -m "Deploy frontend to Heroku"
    heroku git:remote -a ai-survey-frontend
    git push heroku main
    cd ..
    
    print_success "Heroku deployment completed"
}

# Function to deploy to Vercel
deploy_vercel() {
    print_status "Deploying to Vercel..."
    
    # Check if Vercel CLI is installed
    if ! command -v vercel &> /dev/null; then
        print_warning "Vercel CLI not found. Please install it or deploy manually through Vercel dashboard."
        print_status "Visit: https://vercel.com/docs/cli"
        return
    fi
    
    # Deploy frontend to Vercel
    cd frontend
    vercel --prod
    cd ..
    
    print_success "Vercel deployment completed"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS] COMMAND"
    echo ""
    echo "Commands:"
    echo "  local       Deploy to local environment using Docker Compose"
    echo "  production  Deploy to production environment"
    echo "  cloud       Deploy to cloud platform"
    echo "  build       Build Docker images only"
    echo ""
    echo "Options:"
    echo "  -t, --type TYPE     Deployment type (render, railway, heroku, vercel)"
    echo "  -f, --frontend URL  Frontend URL for production deployment"
    echo "  -b, --backend URL   Backend URL for production deployment"
    echo "  -h, --help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 local"
    echo "  $0 production -f https://myapp.vercel.app -b https://myapi.render.com"
    echo "  $0 cloud -t render"
}

# Main script
main() {
    # Parse command line arguments
    while [[ $# -gt 0 ]]; do
        case $1 in
            -t|--type)
                DEPLOYMENT_TYPE="$2"
                shift 2
                ;;
            -f|--frontend)
                FRONTEND_URL="$2"
                shift 2
                ;;
            -b|--backend)
                BACKEND_URL="$2"
                shift 2
                ;;
            -h|--help)
                show_usage
                exit 0
                ;;
            local)
                COMMAND="local"
                shift
                ;;
            production)
                COMMAND="production"
                shift
                ;;
            cloud)
                COMMAND="cloud"
                shift
                ;;
            build)
                COMMAND="build"
                shift
                ;;
            *)
                print_error "Unknown option: $1"
                show_usage
                exit 1
                ;;
        esac
    done
    
    # Check if command is provided
    if [ -z "$COMMAND" ]; then
        print_error "No command specified"
        show_usage
        exit 1
    fi
    
    # Execute command
    case $COMMAND in
        "local")
            check_prerequisites
            build_images
            deploy_local
            ;;
        "production")
            check_prerequisites
            build_images
            deploy_production
            ;;
        "cloud")
            check_prerequisites
            build_images
            deploy_cloud
            ;;
        "build")
            check_prerequisites
            build_images
            ;;
        *)
            print_error "Unknown command: $COMMAND"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
