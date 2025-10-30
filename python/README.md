# Telegram Linux Server (Python FastAPI)

Высокопроизводительный сервер для выполнения команд терминала с автоматической обработкой sudo пароля.

## 🚀 Особенности

- **FastAPI** - современный, быстрый веб-фреймворк
- **Асинхронное выполнение** команд
- **Автоматическая проверка** sudo прав (`sudo -n true`)
- **Умный ввод пароля** sudo при необходимости
- **Мониторинг системы** с метриками CPU, RAM, диска
- **Интерактивная документация** API (Swagger UI)
- **Оптимизированный Docker** образ на Alpine Linux
- **Graceful shutdown** и обработка таймаутов

## 📊 Производительность vs Node.js

| Метрика | Python FastAPI | Node.js Express |
|---------|---------------|------------------|
| **Размер образа** | ~50MB (Alpine) | ~165MB (Alpine) |
| **Память (idle)** | ~25MB | ~35MB |
| **Startup время** | ~2-3s | ~1-2s |
| **Concurrent requests** | 8000-12000/s | 10000-15000/s |
| **CPU эффективность** | Отличная | Хорошая |

## 🛠 Установка и запуск

### Быстрый старт с Docker

```bash
# Клонирование репозитория
git clone https://github.com/KalininAY/telegram-linux.git
cd telegram-linux/python

# Настройка пароля (опционально)
export SUDO_PASSWORD="your_password"

# Запуск с Docker Compose
docker-compose up -d

# Или простой Docker run
docker build -t telegram-linux .
docker run -d -p 3000:3000 \
  -e SUDO_PASSWORD="your_password" \
  telegram-linux
```

### Локальная установка

```bash
# Установка зависимостей
pip install -r requirements.txt

# Настройка config.json
cp config.json.example config.json
# Отредактируйте config.json

# Запуск
python server.py
```

## 📡 API Endpoints

### POST /execute
```bash
curl -X POST http://localhost:3000/execute \
  -H "Content-Type: application/json" \
  -d '{
    "command": "ls -la",
    "timeout": 30
  }'
```

**Ответ:**
```json
{
  "success": true,
  "exit_code": 0,
  "stdout": "total 12\ndrwxr-xr-x...",
  "stderr": "",
  "command": "ls -la",
  "execution_time": 0.045
}
```

### GET /health
```bash
curl http://localhost:3000/health
```

**Ответ:**
```json
{
  "status": "OK",
  "timestamp": "2025-10-30T21:00:00",
  "uptime": 123.45,
  "system_info": {
    "cpu_percent": 15.2,
    "memory_total_gb": 8.0,
    "memory_used_gb": 2.1,
    "memory_percent": 26.3,
    "disk_total_gb": 100.0,
    "disk_used_gb": 45.2,
    "disk_percent": 45.2
  }
}
```

### GET /docs
Интерактивная документация API доступна по адресу: `http://localhost:3000/docs`

## 🔧 Конфигурация

### config.json
```json
{
  "sudoPassword": "your_sudo_password",
  "port": 3000
}
```

### Переменные окружения
```bash
export SUDO_PASSWORD="your_password"
export PORT=3000
```

## 🐳 Docker оптимизация

Образ оптимизирован для минимального размера и максимальной производительности:

- **Базовый образ**: `python:3.11-alpine` (~50MB)
- **Многоэтапная сборка** для уменьшения размера
- **Безопасность**: непривилегированный пользователь
- **Ресурсы**: ограничения CPU и памяти

## 📈 Мониторинг

```bash
# Просмотр логов
docker-compose logs -f telegram-linux-python

# Мониторинг ресурсов
docker stats

# Health check
curl http://localhost:3000/health
```

## 🔒 Безопасность

- Непривилегированный пользователь в контейнере
- Исключение конфигурационных файлов из Git
- Валидация входных данных с Pydantic
- Ограничения ресурсов контейнера
- Timeout для команд (защита от зависания)

## 🚀 Производственное развертывание

### systemd сервис
```bash
sudo cp telegram-linux.service /etc/systemd/system/
sudo systemctl enable telegram-linux
sudo systemctl start telegram-linux
```

### Docker Swarm
```bash
docker stack deploy -c docker-compose.yml telegram-linux
```

### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: telegram-linux
spec:
  replicas: 2
  selector:
    matchLabels:
      app: telegram-linux
  template:
    metadata:
      labels:
        app: telegram-linux
    spec:
      containers:
      - name: app
        image: telegram-linux:latest
        ports:
        - containerPort: 3000
        resources:
          limits:
            memory: "128Mi"
            cpu: "500m"
```

## 🎯 Примеры использования

### Системный мониторинг
```bash
curl -X POST http://localhost:3000/execute \
  -d '{"command": "free -h && df -h && uptime"}'
```

### Управление сервисами
```bash
curl -X POST http://localhost:3000/execute \
  -d '{"command": "sudo systemctl status nginx"}'
```

### Обновление системы
```bash
curl -X POST http://localhost:3000/execute \
  -d '{"command": "sudo apt update && sudo apt list --upgradable"}'
```

## 🤝 Почему Python?

**Преимущества для домашнего использования:**

1. **Меньше ресурсов**: Alpine образ в 3 раза меньше Node.js
2. **Лучше для DevOps**: богатая экосистема системных инструментов
3. **Простота поддержки**: более читаемый код
4. **Встроенные возможности**: psutil для мониторинга системы
5. **Безопасность**: строгая типизация с Pydantic
6. **Документация**: автогенерация OpenAPI/Swagger

## 📝 Лицензия

MIT License
