FROM python:3.11-alpine

# Установка системных пакетов
RUN apk add --no-cache \
    sudo \
    bash \
    procps \
    curl

# Создание пользователя приложения
RUN addgroup -g 1001 -S appuser && \
    adduser -S appuser -u 1001 -G appuser

# Настройка sudo для пользователя
RUN echo 'appuser ALL=(ALL) NOPASSWD: ALL' >> /etc/sudoers

WORKDIR /app

# Копирование зависимостей
COPY requirements.txt .

# Установка python-зависимостей (без psutil)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Копирование исходного кода
COPY server.py .
COPY config.json.example config.json

# Смена пользователя
USER appuser

EXPOSE 3000

# Команда запуска
CMD ["python", "-m", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "3000"]
