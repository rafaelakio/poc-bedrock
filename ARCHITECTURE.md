# Arquitetura do Sistema

## Visão Geral

Sistema de OCR inteligente que combina AWS Bedrock para extração de dados e RAG (Retrieval-Augmented Generation) para validação baseada em conhecimento.

## Componentes

### 1. OCR Module (`src/ocr/`)
- **BedrockOCR**: Cliente para modelos multimodais do Bedrock
- Suporta Claude 3 (Sonnet/Haiku)
- Extração de texto e dados estruturados de imagens

### 2. RAG Module (`src/rag/`)
- **KnowledgeBase**: Gerencia base de conhecimento com embeddings
- **DocumentValidator**: Valida documentos usando RAG + Bedrock
- Busca semântica com Titan Embeddings

### 3. Orchestrator (`src/orchestrator/`)
- **DocumentPipeline**: Orquestra o fluxo completo
- Gerencia OCR → Validação → Resultado
- Processamento em lote

### 4. Utils (`src/utils/`)
- Logger configurável
- Manipulação de arquivos
- Validações

## Fluxo de Dados

```
┌─────────────┐
│  Documento  │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  BedrockOCR     │ ← Claude 3 (Multimodal)
│  Extração       │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Dados Extraídos │
└──────┬──────────┘
       │
       ▼
┌─────────────────────────┐
│  KnowledgeBase          │
│  Busca Padrões          │ ← Titan Embeddings
│  (Similaridade)         │
└──────┬──────────────────┘
       │
       ▼
┌─────────────────────────┐
│  DocumentValidator      │
│  Validação com RAG      │ ← Claude 3 + Contexto
└──────┬──────────────────┘
       │
       ▼
┌─────────────────┐
│ Resultado Final │
│  + Validação    │
└─────────────────┘
```

## Tecnologias

- **AWS Bedrock**: Modelos de IA gerenciados
  - Claude 3: OCR e validação
  - Titan Embeddings: Busca semântica
  
- **Python 3.9+**: Linguagem principal
- **Boto3**: SDK AWS
- **NumPy**: Cálculos de similaridade
- **Pillow**: Processamento de imagens

## Padrões de Design

### 1. Pipeline Pattern
Processamento sequencial com etapas bem definidas

### 2. Strategy Pattern
Diferentes estratégias de validação baseadas no tipo de documento

### 3. Repository Pattern
KnowledgeBase abstrai acesso aos dados de conhecimento

## Escalabilidade

### Processamento em Lote
- Suporte nativo para múltiplos documentos
- Processamento paralelo (futuro)

### Cache de Embeddings
- Embeddings da base de conhecimento são calculados uma vez
- Reutilizados em múltiplas validações

### Modularidade
- Componentes independentes
- Fácil substituição de modelos
- Extensível para novos tipos de documentos

## Segurança

- Credenciais AWS via IAM
- Sem armazenamento de dados sensíveis
- Logs configuráveis
- Validação de entrada

## Custos

### Por Documento (estimativa)
- OCR (Claude 3): ~$0.003 - $0.015
- Embeddings (Titan): ~$0.0001
- Validação (Claude 3): ~$0.003 - $0.015

**Total estimado**: $0.006 - $0.030 por documento

### Otimizações
- Cache de embeddings
- Processamento em lote
- Modelos menores para casos simples (Haiku)
