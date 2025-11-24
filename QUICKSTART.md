# Guia Rápido - OCR com Bedrock

## Instalação Rápida

```bash
cd poc-bedrock
pip install -r requirements.txt
```

## Configuração AWS

1. Configure suas credenciais:
```bash
aws configure
```

2. Habilite os modelos no Bedrock Console:
   - Claude 3 Sonnet
   - Titan Embeddings

## Uso Básico

### Processar um documento

```bash
python main.py --input documento.jpg
```

### Processar múltiplos documentos

```bash
python main.py --input-dir ./meus_documentos/
```

### Personalizar base de conhecimento

```bash
python main.py --input doc.pdf --knowledge-base ./minha_base/
```

## Estrutura de Arquivos

```
poc-bedrock/
├── main.py                    # Script principal
├── knowledge_base/            # Base de conhecimento (padrões)
│   ├── padroes_documentos.txt
│   └── padroes_notas_fiscais.txt
├── output/                    # Resultados (gerado automaticamente)
└── examples/                  # Exemplos de uso
```

## Adicionar Novos Padrões

Crie arquivos `.txt` em `knowledge_base/` com os padrões:

```txt
PADRÃO: Nome do Documento

Campos obrigatórios:
- Campo 1
- Campo 2

Validações:
- Regra 1
- Regra 2
```

## Exemplos de Código

Ver `examples/example_usage.py` para exemplos completos.

## Troubleshooting

**Erro de credenciais AWS:**
```bash
aws configure
# Insira suas credenciais
```

**Modelo não disponível:**
- Acesse AWS Console > Bedrock > Model Access
- Solicite acesso aos modelos Claude 3 e Titan

**Erro de tamanho de arquivo:**
- Limite padrão: 5MB
- Ajuste em `config/settings.py`
