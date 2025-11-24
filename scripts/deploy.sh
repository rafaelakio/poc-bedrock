#!/bin/bash
set -e

ENVIRONMENT=${1:-dev}

echo "🚀 Deploying to AWS ($ENVIRONMENT)..."

# Verificar AWS CLI
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI not found. Please install it first."
    exit 1
fi

# Verificar Terraform
if ! command -v terraform &> /dev/null; then
    echo "❌ Terraform not found. Please install it first."
    exit 1
fi

# Build Lambda
echo "📦 Building Lambda package..."
./scripts/build_lambda.sh

# Deploy infraestrutura
echo "🏗️  Deploying infrastructure..."
cd terraform

terraform init
terraform workspace select $ENVIRONMENT || terraform workspace new $ENVIRONMENT
terraform plan -var="environment=$ENVIRONMENT" -out=tfplan
terraform apply tfplan

# Obter outputs
INPUT_BUCKET=$(terraform output -raw input_bucket_name)
KNOWLEDGE_BUCKET=$(terraform output -raw knowledge_base_bucket_name)

cd ..

# Upload base de conhecimento
echo "📚 Uploading knowledge base..."
aws s3 sync knowledge_base/ s3://$KNOWLEDGE_BUCKET/

echo "✅ Deployment complete!"
echo ""
echo "📋 Resources:"
echo "  Input Bucket: $INPUT_BUCKET"
echo "  Knowledge Bucket: $KNOWLEDGE_BUCKET"
echo ""
echo "🧪 Test with:"
echo "  aws s3 cp test.pdf s3://$INPUT_BUCKET/"
