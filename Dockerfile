# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Системные зависимости на случай, если Pillow/ReportLab решат собираться из исходников
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libjpeg62-turbo-dev zlib1g-dev libpng-dev libfreetype6-dev \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -U pip && pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
CMD ["python", "main.py"]

