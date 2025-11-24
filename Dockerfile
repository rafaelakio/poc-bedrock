FROM python:3.11-slim

WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copia requirements
COPY requirements.txt .

# Instala dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia código da aplicação
COPY . .

# Cria diretórios necessários
RUN mkdir -p /app/output /app/input /app/knowledge_base

# Define variáveis de ambiente padrão
ENV PYTHONUNBUFFERED=1
ENV AWS_REGION=us-east-1

CMD ["python", "main.py", "--help"]
