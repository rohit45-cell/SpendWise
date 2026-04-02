#!/bin/bash
# SpendWise Pro — One-Click Setup Script
# Usage: bash setup.sh

set -e

echo ""
echo "╔══════════════════════════════════════╗"
echo "║   SpendWise Pro — Setup Script       ║"
echo "╚══════════════════════════════════════╝"
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install it first."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo "✅ Python $PYTHON_VERSION detected"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate
echo "⚡ Activating virtual environment..."
source venv/bin/activate 2>/dev/null || . venv/Scripts/activate 2>/dev/null

# Install requirements
echo "📥 Installing requirements..."
pip install -r requirements.txt -q

# Migrations
echo "🗃️  Running database migrations..."
python manage.py makemigrations tracker
python manage.py migrate

echo ""
echo "╔══════════════════════════════════════╗"
echo "║   ✅ Setup Complete!                 ║"
echo "╚══════════════════════════════════════╝"
echo ""
echo "👉 Next steps:"
echo "   1. python manage.py createsuperuser"
echo "   2. python manage.py runserver"
echo "   3. Open http://127.0.0.1:8000/"
echo ""
