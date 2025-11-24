# API Documentation

## REST API

### Endpoint: POST /process

Processa um documento armazenado no S3.

#### Request

```json
{
  "bucket": "bedrock-ocr-input-dev",
  "key": "documento.pdf"
}
```

#### Response (Success)

```json
{
  "message": "Document processed successfully",
  "result_location": "s3://bedrock-ocr-output-dev/results/documento.pdf.json",
  "validation": {
    "is_valid": true,
    "confidence": 0.95,
    "document_type": "matricula_imovel",
    "issues": [],
    "warnings": ["⚠️ Imóvel possui ônus ativos"]
  }
}
```

#### Response (Error)

```json
{
  "error": "Error message"
}
```

#### cURL Example

```bash
curl -X POST https://api-url.execute-api.us-east-1.amazonaws.com/process \
  -H "Content-Type: application/json" \
  -d '{
    "bucket": "bedrock-ocr-input-dev",
    "key": "documento.pdf"
  }'
```

## Python SDK

### Instalação

```bash
pip install bedrock-ocr
```

### Uso Básico

```python
from src.orchestrator import DocumentPipeline

# Inicializar pipeline
pipeline = DocumentPipeline(
    ocr_model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    validation_model_id="anthropic.claude-3-sonnet-20240229-v1:0",
    embedding_model_id="amazon.titan-embed-text-v1",
    knowledge_base_path="./knowledge_base",
    output_path="./output"
)

# Processar documento
result = pipeline.process_document("documento.pdf")
print(result)
```

### Processar em Lote

```python
documents = ["doc1.pdf", "doc2.pdf", "doc3.pdf"]
results = pipeline.process_batch(documents)

for result in results:
    print(f"Documento: {result['document_path']}")
    print(f"Status: {result['status']}")
```

### Prompt Customizado

```python
custom_prompt = """
Extraia as seguintes informações:
1. Nome completo
2. CPF
3. Endereço
Retorne em formato JSON.
"""

result = pipeline.process_document(
    "documento.pdf",
    custom_prompt=custom_prompt
)
```

## Classes Principais

### DocumentPipeline

Orquestra o pipeline completo de OCR e validação.

```python
class DocumentPipeline:
    def __init__(
        self,
        ocr_model_id: str,
        validation_model_id: str,
        embedding_model_id: str,
        knowledge_base_path: str,
        output_path: str = "./output",
        region: str = "us-east-1"
    )
    
    def process_document(
        self,
        document_path: str,
        custom_prompt: str = None
    ) -> Dict[str, Any]
    
    def process_batch(
        self,
        document_paths: List[str]
    ) -> List[Dict[str, Any]]
```

### BedrockOCR

Cliente para OCR usando AWS Bedrock.

```python
class BedrockOCR:
    def __init__(
        self,
        model_id: str,
        region: str = "us-east-1"
    )
    
    def extract_from_image(
        self,
        image_path: str,
        prompt: Optional[str] = None
    ) -> Dict[str, Any]
```

### KnowledgeBase

Gerencia base de conhecimento com embeddings.

```python
class KnowledgeBase:
    def __init__(
        self,
        knowledge_path: str,
        embedding_model_id: str,
        region: str = "us-east-1"
    )
    
    def add_document(
        self,
        content: str,
        metadata: Dict[str, Any] = None
    )
    
    def search_similar(
        self,
        query: str,
        top_k: int = 3
    ) -> List[Dict[str, Any]]
```

### DocumentValidator

Valida documentos usando RAG.

```python
class DocumentValidator:
    def __init__(
        self,
        knowledge_base: KnowledgeBase,
        model_id: str,
        region: str = "us-east-1"
    )
    
    def validate(
        self,
        extracted_data: Dict[str, Any],
        document_type: str = None
    ) -> Dict[str, Any]
```

### MatriculaValidator

Validador especializado para matrículas.

```python
class MatriculaValidator:
    @staticmethod
    def validate_cpf(cpf: str) -> bool
    
    @staticmethod
    def validate_cnpj(cnpj: str) -> bool
    
    @staticmethod
    def validate_structure(
        extracted_data: Dict[str, Any]
    ) -> Dict[str, Any]
```

## Estrutura de Resposta

### Resultado Completo

```json
{
  "timestamp": "2024-01-15T10:30:00",
  "document_path": "documento.pdf",
  "status": "success",
  "result": {
    "extracted_data": {
      "raw_text": "...",
      "model_id": "anthropic.claude-3-sonnet-20240229-v1:0",
      "source": "documento.pdf"
    },
    "document_type": "matricula_imovel",
    "validation": {
      "is_valid": true,
      "confidence": 0.95,
      "issues": [],
      "warnings": ["⚠️ Imóvel possui ônus ativos"],
      "document_type": "matricula_imovel",
      "extracted_fields": {
        "numero_matricula": "12.345",
        "proprietario": "João Silva",
        "cpf": "123.456.789-00"
      },
      "specialized_validation": {
        "matricula_number": "12.345",
        "registros": ["R.1", "R.2"],
        "averbacoes": ["AV.1"],
        "has_onus": true,
        "area": {
          "valid": true,
          "area": 250.0,
          "unit": "m²"
        }
      }
    }
  }
}
```

## Códigos de Status

- `200` - Sucesso
- `400` - Requisição inválida
- `500` - Erro interno

## Rate Limits

- Lambda: 1000 invocações concorrentes
- Bedrock: Varia por modelo (consulte AWS)
- API Gateway: 10,000 requisições/segundo

## Custos

### Por Requisição (estimativa)

- Lambda: ~$0.003
- Bedrock OCR: ~$0.006 - $0.030
- Bedrock Embeddings: ~$0.0001
- S3: ~$0.0001

**Total**: ~$0.01 - $0.04 por documento

## Exemplos Avançados

### Processar com Callback

```python
def on_complete(result):
    print(f"Processado: {result['document_path']}")
    if result['status'] == 'success':
        print(f"Válido: {result['result']['validation']['is_valid']}")

pipeline.process_document("doc.pdf", callback=on_complete)
```

### Validação Customizada

```python
from src.validators import MatriculaValidator

# Validar CPF
is_valid = MatriculaValidator.validate_cpf("123.456.789-09")

# Extrair número de matrícula
text = "MATRÍCULA Nº: 12.345"
numero = MatriculaValidator.extract_matricula_number(text)
```

### Adicionar Documentos à Base de Conhecimento

```python
kb = KnowledgeBase(
    knowledge_path="./knowledge_base",
    embedding_model_id="amazon.titan-embed-text-v1"
)

kb.add_document(
    content="Padrões de validação...",
    metadata={"type": "validation_rules", "version": "1.0"}
)
```

## Webhooks

Configure webhooks para notificações:

```python
# Em desenvolvimento
```

## Monitoramento

### CloudWatch Metrics

- `Invocations` - Número de invocações
- `Duration` - Tempo de execução
- `Errors` - Número de erros
- `Throttles` - Requisições limitadas

### Custom Metrics

```python
import boto3

cloudwatch = boto3.client('cloudwatch')

cloudwatch.put_metric_data(
    Namespace='BedrockOCR',
    MetricData=[
        {
            'MetricName': 'DocumentsProcessed',
            'Value': 1,
            'Unit': 'Count'
        }
    ]
)
```
