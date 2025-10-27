#!/bin/bash

# Learning Cloud Setup Script
# This script sets up the development environment for Learning Cloud

set -e

echo "🚀 Setting up Learning Cloud Development Environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python 3.9+ is installed
check_python() {
    print_status "Checking Python version..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        if [[ $(echo "$PYTHON_VERSION >= 3.9" | bc -l) -eq 1 ]]; then
            print_status "Python $PYTHON_VERSION found ✓"
        else
            print_error "Python 3.9+ is required. Found: $PYTHON_VERSION"
            exit 1
        fi
    else
        print_error "Python 3 is not installed"
        exit 1
    fi
}

# Check if Node.js is installed
check_node() {
    print_status "Checking Node.js version..."
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version | cut -d'v' -f2)
        print_status "Node.js $NODE_VERSION found ✓"
    else
        print_error "Node.js is not installed. Please install Node.js 16+"
        exit 1
    fi
}

# Check if PostgreSQL is installed
check_postgres() {
    print_status "Checking PostgreSQL..."
    if command -v psql &> /dev/null; then
        print_status "PostgreSQL found ✓"
    else
        print_error "PostgreSQL is not installed. Please install PostgreSQL 13+"
        exit 1
    fi
}

# Check if Redis is installed
check_redis() {
    print_status "Checking Redis..."
    if command -v redis-server &> /dev/null; then
        print_status "Redis found ✓"
    else
        print_error "Redis is not installed. Please install Redis 6+"
        exit 1
    fi
}

# Create virtual environment
create_venv() {
    print_status "Creating Python virtual environment..."
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_status "Virtual environment created ✓"
    else
        print_warning "Virtual environment already exists"
    fi
}

# Activate virtual environment
activate_venv() {
    print_status "Activating virtual environment..."
    source venv/bin/activate
    print_status "Virtual environment activated ✓"
}

# Install Python dependencies
install_python_deps() {
    print_status "Installing Python dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    print_status "Python dependencies installed ✓"
}

# Install Node.js dependencies
install_node_deps() {
    print_status "Installing Node.js dependencies..."
    npm install prisma @prisma/client
    print_status "Node.js dependencies installed ✓"
}

# Setup environment file
setup_env() {
    print_status "Setting up environment configuration..."
    if [ ! -f ".env" ]; then
        cp env.example .env
        print_warning "Environment file created from template. Please edit .env with your configuration."
    else
        print_warning "Environment file already exists"
    fi
}

# Setup database
setup_database() {
    print_status "Setting up database..."
    
    # Check if database exists
    if psql -lqt | cut -d \| -f 1 | grep -qw learning_cloud; then
        print_warning "Database 'learning_cloud' already exists"
    else
        print_status "Creating database..."
        createdb learning_cloud
        print_status "Database created ✓"
    fi
    
    # Run Prisma migrations
    print_status "Running Prisma migrations..."
    npx prisma migrate dev --name init
    print_status "Prisma migrations completed ✓"
    
    # Generate Prisma client
    print_status "Generating Prisma client..."
    npx prisma generate
    print_status "Prisma client generated ✓"
}

# Run Django migrations
run_django_migrations() {
    print_status "Running Django migrations..."
    python manage.py migrate
    print_status "Django migrations completed ✓"
}

# Create superuser
create_superuser() {
    print_status "Creating Django superuser..."
    echo "Please create a superuser account:"
    python manage.py createsuperuser
    print_status "Superuser created ✓"
}

# Collect static files
collect_static() {
    print_status "Collecting static files..."
    python manage.py collectstatic --noinput
    print_status "Static files collected ✓"
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    mkdir -p logs
    mkdir -p media
    mkdir -p static
    print_status "Directories created ✓"
}

# Setup Redis
setup_redis() {
    print_status "Starting Redis server..."
    if pgrep -x "redis-server" > /dev/null; then
        print_warning "Redis server is already running"
    else
        redis-server --daemonize yes
        print_status "Redis server started ✓"
    fi
}

# Main setup function
main() {
    print_status "Starting Learning Cloud setup..."
    
    # Check prerequisites
    check_python
    check_node
    check_postgres
    check_redis
    
    # Setup environment
    create_venv
    activate_venv
    install_python_deps
    install_node_deps
    setup_env
    create_directories
    
    # Setup database
    setup_database
    run_django_migrations
    create_superuser
    collect_static
    
    # Setup Redis
    setup_redis
    
    print_status "🎉 Setup completed successfully!"
    print_status ""
    print_status "Next steps:"
    print_status "1. Edit .env file with your configuration"
    print_status "2. Start the development server: python manage.py runserver"
    print_status "3. Start Celery worker: celery -A learning_cloud worker -l info"
    print_status "4. Access the admin panel at: http://localhost:8000/admin/"
    print_status ""
    print_status "For production deployment, see README.md"
}

# Run main function
main "$@"


