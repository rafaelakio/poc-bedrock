# Setup Local - Guia Completo

## Windows

### 1. Instalar Python

```powershell
# Baixe Python 3.11 de python.org
# Ou use winget
winget install Python.Python.3.11
```

### 2. Instalar AWS CLI

```powershell
# Baixe de aws.amazon.com/cli
# Ou use winget
winget install Amazon.AWSCLI
```

### 3. Configurar Projeto

```powershell
# Clone o repositório
git clone https://github.com/seu-usuario/poc-bedrock.git
cd poc-bedrock

# Crie ambiente virtual
python -m venv venv
venv\Scripts\activate

# Instale dependências
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Configure AWS
aws configure

# Copie arquivo de configuração
copy .env.example .env
# Edite .env com suas credenciais
```

### 4. Testar

```powershell
# Executar testes
pytest

# Processar documento
python main.py --input test.pdf
```

## Linux/Mac

### 1. Instalar Python

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip

# Mac (Homebrew)
brew install python@3.11
```

### 2. Instalar AWS CLI

```bash
# Linux
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Mac
brew install awscli
```

### 3. Setup Rápido

```bash
# Clone
git clone https://github.com/seu-usuario/poc-bedrock.git
cd poc-bedrock

# Execute script de setup
chmod +x scripts/setup_dev.sh
./scripts/setup_dev.sh

# Ative ambiente
source venv/bin/activate

# Configure AWS
aws configure
```

### 4. Testar

```bash
# Executar testes
make test

# Processar documento
python main.py --input test.pdf
```

## Docker

### Setup com Docker

```bash
# Build imagem
docker build -t bedrock-ocr:latest .

# Executar
docker run -it \
  -e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
  -e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
  -v $(pwd)/input:/app/input \
  -v $(pwd)/output:/app/output \
  bedrock-ocr:latest \
  python main.py --input-dir /app/input
```

### Docker Compose

```bash
# Edite docker-compose.yml com suas credenciais
docker-compose up
```

## Verificação da Instalação

### Verificar Python

```bash
python --version
# Deve mostrar Python 3.9+
```

### Verificar AWS CLI

```bash
aws --version
# Deve mostrar aws-cli/2.x
```

### Verificar Credenciais AWS

```bash
aws sts get-caller-identity
# Deve mostrar suas informações da conta
```

### Verificar Acesso ao Bedrock

```bash
aws bedrock list-foundation-models --region us-east-1
# Deve listar modelos disponíveis
```

## Configuração do Bedrock

### 1. Acessar Console AWS

1. Vá para https://console.aws.amazon.com/bedrock
2. Selecione região (us-east-1 recomendado)
3. Clique em "Model access"

### 2. Solicitar Acesso aos Modelos

Solicite acesso para:
- ✅ Claude 3 Sonnet
- ✅ Claude 3 Haiku
- ✅ Titan Embeddings Text

### 3. Aguardar Aprovação

Geralmente é instantâneo, mas pode levar alguns minutos.

## Estrutura de Diretórios

Após setup, você terá:

```
poc-bedrock/
├── venv/                 # Ambiente virtual
├── input/                # Documentos para processar
├── output/               # Resultados
├── knowledge_base/       # Base de conhecimento
├── src/                  # Código fonte
├── tests/                # Testes
└── .env                  # Configurações locais
```

## Variáveis de Ambiente

Edite `.env`:

```bash
# AWS
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=sua_chave
AWS_SECRET_ACCESS_KEY=sua_chave_secreta

# Modelos
OCR_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0
EMBEDDING_MODEL_ID=amazon.titan-embed-text-v1
VALIDATION_MODEL_ID=anthropic.claude-3-sonnet-20240229-v1:0

# App
MAX_IMAGE_SIZE=5242880
LOG_LEVEL=INFO
```

## Troubleshooting

### Erro: "Module not found"

```bash
# Reinstale dependências
pip install -r requirements.txt --force-reinstall
```

### Erro: "AWS credentials not found"

```bash
# Reconfigure AWS
aws configure
```

### Erro: "Bedrock model not accessible"

1. Verifique se solicitou acesso aos modelos
2. Verifique a região (deve ser us-east-1)
3. Aguarde aprovação do acesso

### Erro: "Permission denied" (Linux/Mac)

```bash
# Dê permissão aos scripts
chmod +x scripts/*.sh
```

### Erro de Memória

Aumente a memória disponível ou use modelos menores:
```python
# Use Claude 3 Haiku em vez de Sonnet
OCR_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
```

## Próximos Passos

1. ✅ Ambiente configurado
2. 📖 Leia [TESTING.md](TESTING.md) para testar
3. 🚀 Leia [DEPLOYMENT.md](DEPLOYMENT.md) para deploy
4. 🤝 Leia [CONTRIBUTING.md](CONTRIBUTING.md) para contribuir

## Suporte

- Issues: https://github.com/seu-usuario/poc-bedrock/issues
- Documentação AWS Bedrock: https://docs.aws.amazon.com/bedrock/
- Python: https://www.python.org/
