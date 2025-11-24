# Guia de Deploy na AWS

## Pré-requisitos

- AWS CLI configurado
- Terraform >= 1.0
- Docker (para build de imagens)
- Conta AWS com permissões adequadas
- Acesso habilitado aos modelos do Bedrock

## Arquitetura AWS

```
┌─────────────┐
│   S3 Input  │ ──┐
└─────────────┘   │
                  ▼
              ┌─────────┐      ┌──────────────┐
              │ Lambda  │ ───► │   Bedrock    │
              │Function │      │   Models     │
              └─────────┘      └──────────────┘
                  │
                  ▼
┌─────────────┐   │   ┌──────────────┐
│ S3 Output   │ ◄─┘   │ S3 Knowledge │
└─────────────┘       └──────────────┘
                  │
                  ▼
              ┌─────────┐
              │   API   │
              │ Gateway │
              └─────────┘
```

## Passo 1: Habilitar Modelos no Bedrock

1. Acesse o AWS Console
2. Navegue para Amazon Bedrock
3. Vá em "Model access"
4. Solicite acesso aos modelos:
   - Claude 3 Sonnet
   - Claude 3 Haiku
   - Titan Embeddings

## Passo 2: Configurar Backend do Terraform

Crie um bucket S3 para o state do Terraform:

```bash
aws s3 mb s3://bedrock-ocr-terraform-state --region us-east-1
aws s3api put-bucket-versioning \
  --bucket bedrock-ocr-terraform-state \
  --versioning-configuration Status=Enabled
```

## Passo 3: Configurar Variáveis

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
```

Edite `terraform.tfvars` com suas configurações:

```hcl
aws_region  = "us-east-1"
environment = "dev"
project_name = "bedrock-ocr"
```

## Passo 4: Deploy da Infraestrutura

```bash
# Inicializa Terraform
terraform init

# Valida configuração
terraform validate

# Visualiza mudanças
terraform plan

# Aplica mudanças
terraform apply
```

## Passo 5: Build e Deploy da Lambda

```bash
# Cria pacote Lambda
./scripts/build_lambda.sh

# Deploy
cd terraform
terraform apply
```

## Passo 6: Upload da Base de Conhecimento

```bash
# Obtém nome do bucket
KNOWLEDGE_BUCKET=$(terraform output -raw knowledge_base_bucket_name)

# Upload dos arquivos
aws s3 sync ../knowledge_base/ s3://$KNOWLEDGE_BUCKET/
```

## Passo 7: Testar o Deploy

### Via S3 (Automático)

```bash
# Obtém nome do bucket de input
INPUT_BUCKET=$(terraform output -raw input_bucket_name)

# Upload de documento
aws s3 cp documento.pdf s3://$INPUT_BUCKET/

# Verifica resultado
OUTPUT_BUCKET=$(terraform output -raw output_bucket_name)
aws s3 ls s3://$OUTPUT_BUCKET/results/
```

### Via API Gateway

```bash
# Obtém URL da API
API_URL=$(terraform output -raw api_gateway_url)

# Envia requisição
curl -X POST $API_URL/process \
  -H "Content-Type: application/json" \
  -d '{
    "bucket": "bedrock-ocr-input-dev",
    "key": "documento.pdf"
  }'
```

## Monitoramento

### CloudWatch Logs

```bash
# Visualiza logs da Lambda
aws logs tail /aws/lambda/bedrock-ocr-processor-dev --follow
```

### Métricas

Acesse CloudWatch no console AWS para visualizar:
- Invocações da Lambda
- Duração de execução
- Erros
- Custos do Bedrock

## Custos Estimados

### Por Documento (média)
- Lambda (900s, 2GB): ~$0.003
- Bedrock Claude 3 Sonnet: ~$0.006 - $0.030
- Bedrock Titan Embeddings: ~$0.0001
- S3 Storage: ~$0.0001
- API Gateway: ~$0.001

**Total estimado**: $0.01 - $0.04 por documento

### Custos Mensais Fixos
- S3 Buckets: ~$1 - $5
- CloudWatch Logs: ~$0.50 - $2
- API Gateway: ~$1

## Ambientes

### Desenvolvimento
```bash
terraform workspace new dev
terraform workspace select dev
terraform apply -var="environment=dev"
```

### Produção
```bash
terraform workspace new prod
terraform workspace select prod
terraform apply -var="environment=prod"
```

## Segurança

### IAM Roles
- Lambda tem acesso mínimo necessário
- Bedrock access limitado aos modelos específicos
- S3 buckets com encryption habilitada

### Secrets
Use AWS Secrets Manager para credenciais sensíveis:

```bash
aws secretsmanager create-secret \
  --name bedrock-ocr/api-key \
  --secret-string "your-secret-key"
```

## Troubleshooting

### Lambda Timeout
Aumente o timeout em `variables.tf`:
```hcl
variable "lambda_timeout" {
  default = 900  # 15 minutos
}
```

### Memória Insuficiente
Aumente a memória em `variables.tf`:
```hcl
variable "lambda_memory" {
  default = 3008  # MB
}
```

### Erro de Permissão Bedrock
Verifique se os modelos estão habilitados:
```bash
aws bedrock list-foundation-models --region us-east-1
```

## Limpeza

Para remover toda a infraestrutura:

```bash
# Remove objetos dos buckets
aws s3 rm s3://$(terraform output -raw input_bucket_name) --recursive
aws s3 rm s3://$(terraform output -raw output_bucket_name) --recursive
aws s3 rm s3://$(terraform output -raw knowledge_base_bucket_name) --recursive

# Destroy infraestrutura
terraform destroy
```

## Próximos Passos

1. Configure CloudWatch Alarms
2. Implemente API authentication
3. Configure VPC para Lambda
4. Adicione WAF no API Gateway
5. Configure backup automático dos buckets
