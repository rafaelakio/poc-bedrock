# POC - AWS Bedrock OCR com RAG

Sistema de OCR inteligente usando AWS Bedrock para extração e validação de dados de documentos com base em conhecimento (RAG).

## Funcionalidades

- **OCR de Documentos**: Extração de texto de imagens e PDFs usando modelos multimodais do Bedrock
- **Validação com RAG**: Validação dos dados extraídos usando base de conhecimento sobre padrões de documentos
- **Orquestração**: Pipeline completo de processamento de documentos
- **Suporte a múltiplos formatos**: PDF, PNG, JPG, JPEG
- **Validação Especializada**: Validadores específicos para documentos brasileiros
  - Matrículas de imóveis (com validação de CPF/CNPJ, ônus, registros)
  - RG, CPF, CNH
  - Notas fiscais (NF-e, NFS-e)

## Arquitetura

```
documento → OCR (Bedrock) → extração → RAG (validação) → resultado validado
                                          ↑
                                    base de conhecimento
```

## Requisitos

- Python 3.9+
- AWS Account com acesso ao Bedrock
- Credenciais AWS configuradas

## Instalação

```bash
pip install -r requirements.txt
```

## Configuração

1. Configure suas credenciais AWS:
```bash
aws configure
```

2. Edite `config/settings.py` com suas preferências

3. Adicione documentos de padrões em `knowledge_base/`

## Uso

### Processar um documento

```bash
python main.py --input documento.pdf
```

### Processar múltiplos documentos

```bash
python main.py --input-dir ./documentos/
```

### Com validação customizada

```bash
python main.py --input documento.pdf --knowledge-base ./minha_base/
```

### Processar matrícula de imóvel

```bash
python examples/example_matricula.py
```

## Estrutura do Projeto

```
poc-bedrock/
├── src/
│   ├── ocr/              # Módulo de OCR com Bedrock
│   ├── rag/              # Sistema RAG para validação
│   ├── orchestrator/     # Orquestração do pipeline
│   └── utils/            # Utilitários
├── knowledge_base/       # Base de conhecimento (padrões)
├── config/               # Configurações
├── tests/                # Testes
└── examples/             # Exemplos de uso
```

## Modelos Suportados

- Claude 3 Sonnet (multimodal)
- Claude 3 Haiku (multimodal)
- Titan Embeddings (para RAG)

## Documentação Completa

- [LOCAL-SETUP.md](LOCAL-SETUP.md) - Setup do ambiente local (Windows/Linux/Mac)
- [QUICKSTART.md](QUICKSTART.md) - Guia rápido de início
- [TESTING.md](TESTING.md) - Como testar a aplicação
- [DEPLOYMENT.md](DEPLOYMENT.md) - Deploy na AWS com Terraform
- [CONTRIBUTING.md](CONTRIBUTING.md) - Como contribuir com o projeto
- [ARCHITECTURE.md](ARCHITECTURE.md) - Arquitetura do sistema
- [MATRICULA-GUIDE.md](MATRICULA-GUIDE.md) - Guia específico para matrículas
- [API.md](API.md) - Documentação da API

## Scripts Úteis

```bash
# Setup ambiente de desenvolvimento
make setup

# Executar testes locais
make test

# Formatar código
make format

# Deploy na AWS
make deploy

# Build Docker
make docker
```

## CI/CD

O projeto inclui workflows do GitHub Actions para:
- Testes automáticos em múltiplas versões do Python
- Linting e formatação
- Security scanning
- Deploy automático para AWS

## Licença

MIT
