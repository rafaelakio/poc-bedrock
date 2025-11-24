# Guia de Contribuição

Obrigado por considerar contribuir com o projeto Bedrock OCR! 🎉

## Como Contribuir

### 1. Fork e Clone

```bash
# Fork o repositório no GitHub
# Clone seu fork
git clone https://github.com/seu-usuario/poc-bedrock.git
cd poc-bedrock

# Adicione o repositório original como upstream
git remote add upstream https://github.com/original/poc-bedrock.git
```

### 2. Configure o Ambiente

```bash
# Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# Instale dependências
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 3. Crie uma Branch

```bash
# Atualize main
git checkout main
git pull upstream main

# Crie branch para sua feature
git checkout -b feature/minha-feature
# ou
git checkout -b fix/meu-bugfix
```

## Padrões de Código

### Python Style Guide

Seguimos PEP 8 com algumas adaptações:

```python
# Bom ✅
def process_document(document_path: str) -> Dict[str, Any]:
    """
    Processa um documento e retorna resultado.
    
    Args:
        document_path: Caminho para o documento
        
    Returns:
        Dicionário com resultado do processamento
    """
    result = extract_data(document_path)
    return validate_result(result)

# Ruim ❌
def proc_doc(path):
    r = extract(path)
    return r
```

### Formatação

```bash
# Black para formatação
black src/ tests/

# isort para imports
isort src/ tests/

# flake8 para linting
flake8 src/ tests/
```

### Type Hints

Use type hints em todas as funções:

```python
from typing import Dict, List, Optional, Any

def validate_cpf(cpf: str) -> bool:
    """Valida CPF brasileiro"""
    pass

def process_batch(documents: List[str]) -> List[Dict[str, Any]]:
    """Processa múltiplos documentos"""
    pass
```

## Testes

### Escrever Testes

Todo código novo deve ter testes:

```python
# tests/test_new_feature.py
import unittest
from src.module import NewFeature

class TestNewFeature(unittest.TestCase):
    
    def setUp(self):
        self.feature = NewFeature()
    
    def test_basic_functionality(self):
        result = self.feature.process("input")
        self.assertEqual(result, "expected")
    
    def test_edge_case(self):
        with self.assertRaises(ValueError):
            self.feature.process(None)
```

### Executar Testes

```bash
# Todos os testes
pytest

# Com cobertura
pytest --cov=src --cov-report=html

# Teste específico
pytest tests/test_new_feature.py::TestNewFeature::test_basic_functionality
```

### Cobertura Mínima

- Código novo: 90%
- Código existente: 80%

## Documentação

### Docstrings

Use Google Style docstrings:

```python
def complex_function(param1: str, param2: int, param3: Optional[bool] = None) -> Dict[str, Any]:
    """
    Descrição breve da função.
    
    Descrição mais detalhada se necessário, explicando o comportamento,
    casos especiais, etc.
    
    Args:
        param1: Descrição do primeiro parâmetro
        param2: Descrição do segundo parâmetro
        param3: Descrição do parâmetro opcional. Defaults to None.
    
    Returns:
        Dicionário contendo:
            - key1: Descrição
            - key2: Descrição
    
    Raises:
        ValueError: Quando param2 é negativo
        TypeError: Quando param1 não é string
    
    Example:
        >>> result = complex_function("test", 42)
        >>> print(result['key1'])
        'value'
    """
    pass
```

### README e Guias

Atualize documentação relevante:
- README.md
- ARCHITECTURE.md
- API.md (se aplicável)

## Commit Messages

### Formato

```
tipo(escopo): descrição curta

Descrição mais detalhada se necessário.

Fixes #123
```

### Tipos

- `feat`: Nova funcionalidade
- `fix`: Correção de bug
- `docs`: Documentação
- `style`: Formatação
- `refactor`: Refatoração
- `test`: Testes
- `chore`: Manutenção

### Exemplos

```bash
feat(ocr): adiciona suporte para documentos TIFF

Implementa processamento de imagens TIFF usando Pillow.
Adiciona testes para validação de formato.

Fixes #42

---

fix(validator): corrige validação de CPF com zeros

CPFs começando com zero não eram validados corretamente.

Fixes #56

---

docs(readme): atualiza instruções de instalação

Adiciona seção sobre configuração do Bedrock.
```

## Pull Request

### Checklist

Antes de abrir um PR, verifique:

- [ ] Código segue os padrões do projeto
- [ ] Testes foram adicionados/atualizados
- [ ] Todos os testes passam
- [ ] Documentação foi atualizada
- [ ] Commit messages seguem o padrão
- [ ] Branch está atualizada com main

### Template

```markdown
## Descrição

Breve descrição das mudanças.

## Tipo de Mudança

- [ ] Bug fix
- [ ] Nova funcionalidade
- [ ] Breaking change
- [ ] Documentação

## Como Testar

1. Passo 1
2. Passo 2
3. Resultado esperado

## Screenshots (se aplicável)

## Checklist

- [ ] Testes passando
- [ ] Documentação atualizada
- [ ] Code review solicitado
```

## Estrutura do Projeto

```
poc-bedrock/
├── src/
│   ├── ocr/              # Módulo de OCR
│   ├── rag/              # Sistema RAG
│   ├── validators/       # Validadores específicos
│   ├── orchestrator/     # Orquestração
│   └── utils/            # Utilitários
├── tests/                # Testes
├── knowledge_base/       # Base de conhecimento
├── terraform/            # Infraestrutura
├── examples/             # Exemplos
└── docs/                 # Documentação adicional
```

## Adicionando Novos Validadores

### 1. Criar Validador

```python
# src/validators/novo_documento_validator.py
class NovoDocumentoValidator:
    """Validador para novo tipo de documento"""
    
    @staticmethod
    def validate_structure(extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida estrutura do documento"""
        issues = []
        warnings = []
        
        # Implementar validações
        
        return {
            'is_valid': len(issues) == 0,
            'issues': issues,
            'warnings': warnings
        }
```

### 2. Adicionar Base de Conhecimento

```
# knowledge_base/padroes_novo_documento.txt
PADRÕES DO NOVO DOCUMENTO

1. Estrutura
   - Campo obrigatório 1
   - Campo obrigatório 2

2. Validações
   - Regra 1
   - Regra 2
```

### 3. Integrar no Validator

```python
# src/rag/validator.py
from ..validators.novo_documento_validator import NovoDocumentoValidator

# Adicionar detecção
if 'palavra_chave' in text_lower:
    return 'novo_documento'

# Adicionar validação
if document_type == 'novo_documento':
    specialized_validation = NovoDocumentoValidator.validate_structure(extracted_data)
```

### 4. Adicionar Testes

```python
# tests/test_novo_documento_validator.py
class TestNovoDocumentoValidator(unittest.TestCase):
    def test_validation(self):
        # Implementar testes
        pass
```

## Adicionando Novos Modelos Bedrock

### 1. Atualizar Configuração

```python
# config/settings.py
class Settings(BaseSettings):
    novo_model_id: str = "novo-modelo-id"
```

### 2. Atualizar Terraform

```hcl
# terraform/variables.tf
variable "novo_model_id" {
  description = "Novo modelo Bedrock"
  type        = string
  default     = "novo-modelo-id"
}
```

### 3. Documentar

Adicione informações sobre o novo modelo no README.md

## Code Review

### O que Procuramos

- ✅ Código limpo e legível
- ✅ Testes adequados
- ✅ Documentação clara
- ✅ Performance aceitável
- ✅ Segurança
- ✅ Tratamento de erros

### Processo

1. Abra PR
2. Aguarde review automático (CI/CD)
3. Aguarde review manual
4. Faça ajustes se necessário
5. Aprovação e merge

## Comunicação

### Issues

- Use templates de issue
- Seja claro e objetivo
- Inclua exemplos quando possível
- Adicione labels apropriadas

### Discussões

- Use GitHub Discussions para perguntas
- Stack Overflow para questões técnicas
- Slack/Discord para chat (se disponível)

## Licença

Ao contribuir, você concorda que suas contribuições serão licenciadas sob a mesma licença do projeto (MIT).

## Dúvidas?

- Abra uma issue
- Entre em contato com os mantenedores
- Consulte a documentação

Obrigado por contribuir! 🚀
