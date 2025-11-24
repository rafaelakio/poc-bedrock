#!/bin/bash
set -e

echo "🔧 Setting up development environment..."

# Verificar Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.9 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✅ Python version: $PYTHON_VERSION"

# Criar ambiente virtual
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
else
    echo "✅ Virtual environment already exists"
fi

# Ativar ambiente
echo "🔌 Activating virtual environment..."
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate

# Atualizar pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip -q

# Instalar dependências
echo "📥 Installing dependencies..."
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Configurar pre-commit
echo "🪝 Setting up pre-commit hooks..."
pre-commit install

# Criar diretórios necessários
echo "📁 Creating directories..."
mkdir -p output
mkdir -p input
mkdir -p tests/fixtures

# Copiar arquivo de configuração
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your AWS credentials"
fi

# Verificar AWS CLI
if command -v aws &> /dev/null; then
    echo "✅ AWS CLI found"
    aws --version
else
    echo "⚠️  AWS CLI not found. Install it for AWS integration."
fi

# Verificar Terraform
if command -v terraform &> /dev/null; then
    echo "✅ Terraform found"
    terraform version
else
    echo "⚠️  Terraform not found. Install it for infrastructure deployment."
fi

echo ""
echo "✅ Development environment setup complete!"
echo ""
echo "📋 Next steps:"
echo "  1. Edit .env with your AWS credentials"
echo "  2. Run tests: ./scripts/test_local.sh"
echo "  3. Process a document: python main.py --input test.pdf"
echo ""
echo "💡 Activate environment with:"
echo "  source venv/bin/activate"
