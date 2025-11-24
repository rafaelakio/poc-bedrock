# Guia de Testes

## Testes Locais

### Pré-requisitos

```bash
# Instalar dependências
pip install -r requirements.txt
pip install pytest pytest-cov pytest-mock
```

### Configuração

1. Configure suas credenciais AWS:
```bash
aws configure
```

2. Crie arquivo `.env`:
```bash
cp .env.example .env
# Edite .env com suas configurações
```

### Executar Testes Unitários

```bash
# Todos os testes
pytest

# Com cobertura
pytest --cov=src --cov-report=html

# Teste específico
pytest tests/test_matricula_validator.py

# Modo verbose
pytest -v
```

### Testes de Integração

```bash
# Teste com documento real
python main.py --input examples/sample_document.jpg

# Teste de matrícula
python examples/example_matricula.py
```

## Testes Manuais

### 1. Teste de OCR

```python
from src.ocr import BedrockOCR

ocr = BedrockOCR(model_id="anthropic.claude-3-sonnet-20240229-v1:0")
result = ocr.extract_from_image("test_document.jpg")
print(result)
```

### 2. Teste de Validação

```python
from src.rag import KnowledgeBase, DocumentValidator

kb = KnowledgeBase(
    knowledge_path="./knowledge_base",
    embedding_model_id="amazon.titan-embed-text-v1"
)

validator = DocumentValidator(
    knowledge_base=kb,
    model_id="anthropic.claude-3-sonnet-20240229-v1:0"
)

result = validator.validate(extracted_data)
print(result)
```


### 3. Teste de Pipeline Completo

```python
from src.orchestrator import DocumentPipeline

pipeline = DocumentPipeline(
    ocr_model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    validation_model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    embedding_model_id="amazon.titan-embed-text-v1",
    knowledge_base_path="./knowledge_base",
    output_path="./output"
)

result = pipeline.process_document("test.pdf")
print(result)
```

## Testes com Docker

### Build da Imagem

```bash
docker build -t bedrock-ocr:latest .
```

### Executar Container

```bash
docker run -it \
  -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
  -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
  -e AWS_REGION=us-east-1 \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  bedrock-ocr:latest \
  python main.py --input-dir /app/input
```

### Docker Compose

```bash
docker-compose up
```

## Testes na AWS

### Teste Lambda Local (SAM)

```bash
# Instalar SAM CLI
pip install aws-sam-cli

# Invocar Lambda localmente
sam local invoke DocumentProcessor \
  --event tests/events/s3_event.json
```

### Teste via S3

```bash
# Upload de documento
aws s3 cp test_document.pdf s3://bedrock-ocr-input-dev/

# Verificar logs
aws logs tail /aws/lambda/bedrock-ocr-processor-dev --follow

# Baixar resultado
aws s3 cp s3://bedrock-ocr-output-dev/results/test_document.pdf.json ./
```

### Teste via API Gateway

```bash
# Obter URL da API
API_URL=$(cd terraform && terraform output -raw api_gateway_url)

# Testar endpoint
curl -X POST $API_URL/process \
  -H "Content-Type: application/json" \
  -d '{
    "bucket": "bedrock-ocr-input-dev",
    "key": "test_document.pdf"
  }'
```

## Testes de Performance

### Benchmark de Processamento

```python
import time
from src.orchestrator import DocumentPipeline

pipeline = DocumentPipeline(...)

documents = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]

start = time.time()
results = pipeline.process_batch(documents)
end = time.time()

print(f"Tempo total: {end - start:.2f}s")
print(f"Média por documento: {(end - start) / len(documents):.2f}s")
```

### Teste de Carga

```bash
# Usando Apache Bench
ab -n 100 -c 10 -p payload.json -T application/json \
  $API_URL/process
```

## Validação de Documentos de Teste

### Criar Documentos de Teste

```bash
# Diretório de testes
mkdir -p tests/fixtures

# Adicionar documentos de exemplo
cp sample_rg.jpg tests/fixtures/
cp sample_matricula.pdf tests/fixtures/
```

### Script de Validação

```bash
#!/bin/bash
# tests/validate_all.sh

for file in tests/fixtures/*; do
  echo "Testando: $file"
  python main.py --input "$file"
  
  if [ $? -eq 0 ]; then
    echo "✅ Sucesso"
  else
    echo "❌ Falha"
  fi
done
```

## Testes de Regressão

```bash
# Salvar resultados baseline
python main.py --input test.pdf > baseline.json

# Após mudanças, comparar
python main.py --input test.pdf > current.json
diff baseline.json current.json
```

## Cobertura de Testes

```bash
# Gerar relatório de cobertura
pytest --cov=src --cov-report=html --cov-report=term

# Visualizar relatório
open htmlcov/index.html
```

## CI/CD Testing

### GitHub Actions

Veja `.github/workflows/test.yml` para configuração de testes automáticos.

### Testes Obrigatórios

- ✅ Testes unitários passando
- ✅ Cobertura > 80%
- ✅ Linting (flake8, black)
- ✅ Type checking (mypy)
- ✅ Security scan (bandit)

## Troubleshooting

### Erro de Credenciais AWS

```bash
# Verificar credenciais
aws sts get-caller-identity

# Reconfigurar
aws configure
```

### Erro de Modelo Bedrock

```bash
# Listar modelos disponíveis
aws bedrock list-foundation-models --region us-east-1

# Verificar acesso
aws bedrock get-foundation-model \
  --model-identifier anthropic.claude-3-sonnet-20240229-v1:0
```

### Timeout em Testes

Aumente o timeout em `pytest.ini`:
```ini
[pytest]
timeout = 300
```

## Métricas de Qualidade

### Objetivos
- Cobertura de testes: > 80%
- Tempo de execução: < 30s para suite completa
- Taxa de sucesso: > 95%
- Tempo de processamento: < 60s por documento
