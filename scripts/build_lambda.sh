#!/bin/bash
set -e

echo "🔨 Building Lambda package..."

# Criar diretório temporário
BUILD_DIR="lambda_build"
rm -rf $BUILD_DIR
mkdir -p $BUILD_DIR

# Copiar código fonte
echo "📦 Copying source code..."
cp -r src $BUILD_DIR/
cp -r config $BUILD_DIR/
cp lambda_handler.py $BUILD_DIR/

# Instalar dependências
echo "📥 Installing dependencies..."
pip install -r requirements.txt -t $BUILD_DIR/ --upgrade

# Criar arquivo zip
echo "🗜️  Creating zip file..."
cd $BUILD_DIR
zip -r ../lambda_function.zip . -x "*.pyc" -x "*__pycache__*"
cd ..

# Limpar
rm -rf $BUILD_DIR

echo "✅ Lambda package created: lambda_function.zip"
echo "📊 Package size: $(du -h lambda_function.zip | cut -f1)"
