#!/bin/bash
# Quick Start Script - Laptop Control System
# This script starts all components (Backend, Agent, Mobile App)

set -e

echo "==============================================="
echo "Laptop Control System - Quick Start"
echo "==============================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check Python installation
info "Checking Python installation..."
if ! command -v python3 &> /dev/null; then
    warn "Python3 not found. Using python instead..."
    PYTHON=python
else
    PYTHON=python3
fi

success "Python found: $(${PYTHON} --version)"
echo ""

# ===== Backend Setup =====
info "Setting up Backend..."

if [ ! -d "backend/venv" ]; then
    info "Creating virtual environment for backend..."
    cd backend
    ${PYTHON} -m venv venv
    cd ..
else
    success "Backend virtual environment already exists"
fi

# Activate venv
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    source backend/venv/Scripts/activate
else
    source backend/venv/bin/activate
fi

# Install dependencies
info "Installing backend dependencies..."
pip install -q -r backend/requirements.txt
success "Backend dependencies installed"
echo ""

# ===== Agent Setup =====
info "Setting up Laptop Agent..."

if [ ! -d "agent/venv" ]; then
    info "Creating virtual environment for agent..."
    cd agent
    ${PYTHON} -m venv venv
    cd ..
else
    success "Agent virtual environment already exists"
fi

# Install dependencies
info "Installing agent dependencies..."
pip install -q -r agent/requirements.txt
success "Agent dependencies installed"
echo ""

# ===== Flutter Setup =====
info "Setting up Flutter Mobile App..."

if [ ! -d "mobile_app/build" ]; then
    info "Getting Flutter dependencies..."
    cd mobile_app
    flutter pub get > /dev/null 2>&1 || warn "Flutter pub get might have issues"
    cd ..
else
    success "Flutter app already built"
fi

success "Flutter app setup complete"
echo ""

# ===== Environment Setup =====
info "Setting up environment files..."

if [ ! -f "backend/.env" ]; then
    info "Creating backend .env from example..."
    cp backend/.env.example backend/.env
    warn "Please edit backend/.env with your configuration"
else
    success "Backend .env already exists"
fi

if [ ! -f "agent/.env" ]; then
    info "Creating agent .env from example..."
    cp agent/.env.example agent/.env
    warn "Please edit agent/.env with your device ID and backend URL"
else
    success "Agent .env already exists"
fi

echo ""
echo "==============================================="
echo "Setup Complete!"
echo "==============================================="
echo ""

echo -e "${GREEN}Next steps:${NC}"
echo ""
echo "1. ${YELLOW}Backend${NC} - In terminal 1:"
echo "   cd backend"
echo "   source venv/bin/activate  # or venv\\Scripts\\activate on Windows"
echo "   python run.py"
echo ""
echo "2. ${YELLOW}Laptop Agent${NC} - In terminal 2 (after backend starts):"
echo "   cd agent"
echo "   source venv/bin/activate  # or venv\\Scripts\\activate on Windows"
echo "   python agent.py"
echo ""
echo "3. ${YELLOW}Mobile App${NC} - In terminal 3:"
echo "   cd mobile_app"
echo "   flutter run"
echo ""
echo -e "${BLUE}API Documentation:${NC}"
echo "   Swagger: http://localhost:8000/docs"
echo "   ReDoc:   http://localhost:8000/redoc"
echo ""

# Deactivate venv
deactivate 2>/dev/null || true

success "Ready to start the system!"
