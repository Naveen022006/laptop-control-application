#!/bin/bash

# Laptop Control Application - Setup Script
# This script automates the initial setup of all components

set -e

echo "================================"
echo "Laptop Control - Setup Script"
echo "================================"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_info() {
    echo -e "${YELLOW}[i]${NC} $1"
}

# Check Python installation
print_info "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed"
    exit 1
fi
print_status "Python 3 found: $(python3 --version)"

# Setup Backend
print_info "Setting up Backend..."
cd backend

if [ ! -d "venv" ]; then
    print_info "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    source venv/Scripts/activate 2>/dev/null || source venv/bin/activate
fi

print_info "Installing dependencies..."
pip install -r requirements.txt -q

# Create .env file if not exists
if [ ! -f ".env" ]; then
    print_info "Creating .env file..."
    cp .env.example .env
    print_status "Created .env - Please edit with your settings"
fi

# Initialize database
print_info "Initializing database..."
python -c "from app.models.database import create_tables; create_tables()"
print_status "Database initialized"

cd ..

# Setup Laptop Agent
print_info "Setting up Laptop Agent..."
cd laptop_agent

if [ ! -d "venv" ]; then
    print_info "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    source venv/Scripts/activate 2>/dev/null || source venv/bin/activate
fi

print_info "Installing dependencies..."
pip install -r requirements.txt -q

# Create .env file if not exists
if [ ! -f ".env" ]; then
    print_info "Creating .env file..."
    cp .env.example .env
    print_status "Created .env - Please edit with your API token"
fi

# Create necessary directories
mkdir -p logs screenshots

cd ..

# Setup Mobile App
print_info "Setting up Mobile App..."
cd mobile_app

if ! command -v flutter &> /dev/null; then
    print_error "Flutter SDK is not installed"
    print_info "Visit https://flutter.dev/docs/get-started/install"
else
    print_info "Fetching Flutter dependencies..."
    flutter pub get -q
    print_status "Flutter setup complete"
fi

cd ..

# Summary
echo ""
echo "================================"
echo -e "${GREEN}Setup Complete!${NC}"
echo "================================"
echo ""
print_info "Next steps:"
echo "1. Edit backend/.env with your settings"
echo "2. Edit laptop_agent/.env with backend URL and API token"
echo "3. Register your laptop: curl -X POST http://localhost:8000/devices/register"
echo "4. Start backend: cd backend && uvicorn app.main:app --reload"
echo "5. Start agent: cd laptop_agent && python agent.py"
echo "6. Start mobile app: cd mobile_app && flutter run"
echo ""
print_info "Documentation:"
echo "- Quick Start: See QUICKSTART.md"
echo "- Full Setup: See SETUP_GUIDE.md"
echo "- API Docs: See API_DOCUMENTATION.md"
echo ""
