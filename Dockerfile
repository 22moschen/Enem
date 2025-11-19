# Usar imagem base do Python
FROM python:3.11-slim

# Definir diretório de trabalho
WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements.txt e instalar dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Criar diretórios necessários
RUN mkdir -p DWStorage DataSources

# Expor porta do Streamlit
EXPOSE 8501

# Comando para executar ETL automatizado e depois iniciar Streamlit
CMD ["sh", "-c", "python automate_etl.py && streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0"]
