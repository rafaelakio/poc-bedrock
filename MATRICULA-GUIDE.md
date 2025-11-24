# Guia de Validação de Matrículas de Imóveis

## Visão Geral

O sistema está preparado para processar e validar matrículas de imóveis brasileiros com validações específicas e detalhadas.

## Funcionalidades Específicas

### 1. Detecção Automática
O sistema detecta automaticamente quando o documento é uma matrícula de imóvel baseado em palavras-chave como:
- "Matrícula"
- "Registro de Imóveis"
- "Cartório"
- Padrões R.1, R.2, AV.1, AV.2

### 2. Validações Especializadas

#### Estrutura da Matrícula
- ✅ Número da matrícula
- ✅ Livro e folha
- ✅ Cartório e comarca
- ✅ Data de abertura

#### Dados do Imóvel
- ✅ Endereço completo com CEP
- ✅ Área do terreno e construída
- ✅ Inscrição municipal (IPTU)
- ✅ Confrontações

#### Proprietário
- ✅ Nome completo
- ✅ CPF/CNPJ com validação de dígitos verificadores
- ✅ Estado civil
- ✅ Regime de bens

#### Registros e Averbações
- ✅ Numeração sequencial (R.1, R.2, R.3...)
- ✅ Averbações (AV.1, AV.2, AV.3...)
- ✅ Datas válidas
- ✅ Consistência cronológica

#### Ônus e Gravames
- ⚠️ Detecção de hipotecas ativas
- ⚠️ Detecção de penhoras
- ⚠️ Detecção de alienação fiduciária
- ⚠️ Verificação de cancelamentos

## Como Usar

### Processar uma Matrícula

```bash
python main.py --input matricula.pdf
```

### Usar Exemplo Específico

```bash
python examples/example_matricula.py
```

### Processar Múltiplas Matrículas

```bash
python main.py --input-dir ./matriculas/
```

## Prompt Customizado

O sistema usa um prompt especializado que extrai:

```json
{
  "numero_matricula": "12.345",
  "imovel": {
    "tipo": "Casa",
    "endereco_completo": "Rua X, 123",
    "area_terreno": "250.00 m²",
    "inscricao_municipal": "XXX.XXX.XXX"
  },
  "proprietario_atual": {
    "nome": "João Silva",
    "cpf_cnpj": "123.456.789-00",
    "estado_civil": "Casado"
  },
  "registros": [...],
  "onus_gravames": [...],
  "averbacoes": [...]
}
```

## Alertas Importantes

O sistema emite alertas para:

- ⚠️ Imóvel com ônus ativos (hipoteca, penhora)
- ⚠️ CPF/CNPJ inválido
- ⚠️ Área inconsistente
- ⚠️ Falta de inscrição municipal
- ⚠️ Confrontações incompletas
- ⚠️ Datas inconsistentes

## Validações Automáticas

### CPF
- 11 dígitos
- Dígitos verificadores corretos
- Não pode ser sequência repetida

### CNPJ
- 14 dígitos
- Dígitos verificadores corretos

### CEP
- Formato: XXXXX-XXX
- 8 dígitos numéricos

### Área
- Valor positivo
- Unidade em m²
- Área construída ≤ área do terreno

## Base de Conhecimento

O arquivo `knowledge_base/padroes_matricula_imovel.txt` contém:

- Estrutura completa de matrículas brasileiras
- Padrões de registros e averbações
- Tipos de ônus e gravames
- Validações obrigatórias
- Exemplos de estrutura

## Resultado da Validação

O sistema retorna:

```json
{
  "status": "success",
  "document_type": "matricula_imovel",
  "validation": {
    "is_valid": true,
    "confidence": 0.95,
    "issues": [],
    "warnings": ["⚠️ Imóvel possui ônus ativos"],
    "specialized_validation": {
      "matricula_number": "12.345",
      "registros": ["R.1", "R.2"],
      "averbacoes": ["AV.1", "AV.2"],
      "has_onus": true,
      "area": {"valid": true, "area": 250.0, "unit": "m²"},
      "valid_cpfs": ["123.456.789-00"]
    }
  }
}
```

## Casos de Uso

### 1. Due Diligence Imobiliária
Valide matrículas antes de transações imobiliárias

### 2. Análise de Crédito
Verifique ônus e gravames para concessão de crédito

### 3. Auditoria Documental
Valide consistência de documentos em lote

### 4. Digitalização de Acervo
Extraia e estruture dados de matrículas antigas

## Próximos Passos

1. Adicione suas matrículas em `./input/`
2. Execute o processamento
3. Verifique os resultados em `./output/`
4. Analise os alertas e recomendações

## Suporte

Para adicionar novos padrões de validação, edite:
- `knowledge_base/padroes_matricula_imovel.txt`
- `src/validators/matricula_validator.py`
