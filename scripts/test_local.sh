#!/bin/bash
set -e

echo "🧪 Running local tests..."

# Verificar ambiente virtual
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Ativar ambiente
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate

# Instalar dependências
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt
pip install -q -r requirements-dev.txt

# Linting
echo "🔍 Running linting..."
echo "  - flake8"
flake8 src tests --max-line-length=127 --extend-ignore=E203,W503

echo "  - black"
black --check src tests

echo "  - isort"
isort --check-only src tests

# Type checking
echo "🔎 Running type checking..."
mypy src --ignore-missing-imports

# Security
echo "🔒 Running security checks..."
bandit -r src -ll -q

# Testes unitários
echo "🧪 Running unit tests..."
pytest tests/ -v --cov=src --cov-report=term-missing

echo ""
echo "✅ All tests passed!"
