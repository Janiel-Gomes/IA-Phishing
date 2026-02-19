FROM python:3.10-slim

WORKDIR /app

# Copiar dependências primeiro (melhor aproveitamento do cache do Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o restante do projeto
COPY . .

# HF Spaces expõe a porta 7860
EXPOSE 7860

CMD ["python", "app.py"]
