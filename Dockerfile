FROM python:3.10-slim

WORKDIR /app

# Install system dependencies for ONNX and Redis
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create models directory if it doesn't exist
RUN mkdir -p models

# Make start.sh executable
RUN chmod +x start.sh

EXPOSE 8000

CMD ["./start.sh"]
