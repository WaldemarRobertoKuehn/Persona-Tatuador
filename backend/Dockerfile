# Usa a versão de Python definida para o contêiner da API.
FROM python:3.12-slim

# Define a pasta de trabalho da aplicação dentro do contêiner.
WORKDIR /app

# Copia primeiro a lista de dependências para aproveitar o cache entre builds.
COPY requirements.txt .

# Instala as dependências antes de copiar o código da aplicação.
RUN pip install --no-cache-dir -r requirements.txt

# Copia o backend para a pasta de trabalho.
COPY . .

# Inicia o FastAPI na porta interna 8000.
CMD ["fastapi", "run", "main.py", "--port", "8000"]
