#!/bin/bash

# Farm Marketplace Deployment Script
# This script automates the deployment process for production

set -e  # Exit on any error

echo "🚀 Starting Farm Marketplace Deployment..."

# Check if required environment variables are set
check_env_vars() {
    echo "📋 Checking environment variables..."
    required_vars=("SECRET_KEY" "DB_PASSWORD" "EMAIL_HOST_USER" "EMAIL_HOST_PASSWORD" "STRIPE_SECRET_KEY")
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            echo "❌ Error: $var environment variable is not set"
            exit 1
        fi
    done
    echo "✅ All required environment variables are set"
}

# Build and start services
deploy_with_docker() {
    echo "🐳 Building and deploying with Docker..."
    
    # Build the application
    docker-compose build
    
    # Start services
    docker-compose up -d
    
    # Wait for database to be ready
    echo "⏳ Waiting for database to be ready..."
    sleep 10
    
    # Run migrations
    docker-compose exec web python manage.py migrate
    
    # Collect static files
    docker-compose exec web python manage.py collectstatic --noinput
    
    # Create superuser if it doesn't exist
    docker-compose exec web python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@farmmarket.com', 'admin123')
    print('Superuser created')
else:
    print('Superuser already exists')
"
    
    echo "✅ Docker deployment completed"
}

# Manual deployment (without Docker)
deploy_manual() {
    echo "📦 Manual deployment process..."
    
    # Install dependencies
    pip install -r requirements.txt
    pip install gunicorn psycopg2-binary
    
    # Run migrations
    python manage.py migrate
    
    # Collect static files
    python manage.py collectstatic --noinput
    
    # Create superuser if needed
    python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@farmmarket.com', 'admin123')
    print('Superuser created')
else:
    print('Superuser already exists')
"
    
    echo "✅ Manual deployment completed"
}

# Health check
health_check() {
    echo "🏥 Running health checks..."
    
    # Check if web service is running
    if docker-compose ps | grep -q "web.*Up"; then
        echo "✅ Web service is running"
    else
        echo "❌ Web service is not running"
        return 1
    fi
    
    # Check if database is accessible
    if docker-compose exec db pg_isready -U farmmarket; then
        echo "✅ Database is accessible"
    else
        echo "❌ Database is not accessible"
        return 1
    fi
    
    # Check if Redis is running
    if docker-compose exec redis redis-cli ping | grep -q "PONG"; then
        echo "✅ Redis is running"
    else
        echo "❌ Redis is not running"
        return 1
    fi
    
    echo "✅ All health checks passed"
}

# SSL certificate setup
setup_ssl() {
    echo "🔒 Setting up SSL certificates..."
    
    # Create SSL directory
    mkdir -p ssl
    
    # Generate self-signed certificate for development
    if [ ! -f ssl/cert.pem ] || [ ! -f ssl/key.pem ]; then
        openssl req -x509 -newkey rsa:4096 -keyout ssl/key.pem -out ssl/cert.pem -days 365 -nodes \
            -subj "/C=US/ST=State/L=City/O=Organization/CN=farmmarket.com"
        echo "✅ Self-signed SSL certificate generated"
        echo "⚠️  For production, replace with valid SSL certificates"
    else
        echo "✅ SSL certificates already exist"
    fi
}

# Backup database
backup_database() {
    echo "💾 Creating database backup..."
    
    timestamp=$(date +"%Y%m%d_%H%M%S")
    backup_file="backup_${timestamp}.sql"
    
    docker-compose exec db pg_dump -U farmmarket farmmarket_db > $backup_file
    echo "✅ Database backup created: $backup_file"
}

# Show usage information
show_usage() {
    echo "Usage: $0 [OPTION]"
    echo "Options:"
    echo "  docker     Deploy using Docker Compose"
    echo "  manual     Manual deployment without Docker"
    echo "  health     Run health checks"
    echo "  ssl        Setup SSL certificates"
    echo "  backup     Backup database"
    echo "  help       Show this help message"
}

# Main deployment logic
main() {
    case "${1:-docker}" in
        "docker")
            check_env_vars
            setup_ssl
            deploy_with_docker
            health_check
            echo "🎉 Deployment completed successfully!"
            echo "📱 Access your application at: https://localhost"
            ;;
        "manual")
            check_env_vars
            deploy_manual
            echo "🎉 Manual deployment completed!"
            echo "📱 Start the server with: gunicorn farmmarket.wsgi:application"
            ;;
        "health")
            health_check
            ;;
        "ssl")
            setup_ssl
            ;;
        "backup")
            backup_database
            ;;
        "help"|"-h"|"--help")
            show_usage
            ;;
        *)
            echo "❌ Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
