# Telegram Linux Server (Python FastAPI)

Высокопроизводительный сервер для выполнения команд терминала с автоматической обработкой sudo пароля.

## 🚀 Особенности

- **FastAPI** - современный, быстрый веб-фреймворк
- **Асинхронное выполнение** команд
- **Автоматическая проверка** sudo прав (`sudo -n true`)
- **Умный ввод пароля** sudo при необходимости
- **Мониторинг системы** с метриками CPU, RAM, диска
- **Интерактивная документация** API (Swagger UI)
- **Оптимизированный Docker** образ на Alpine Linux (~50MB)
- **Graceful shutdown** и обработка таймаутов

## 📊 Производительность vs Node.js

| Метрика | Python FastAPI | Node.js Express |
|---------|---------------|------------------|
| **Размер образа** | ~50MB (Alpine) | ~165MB (Alpine) |
| **Память (idle)** | ~25MB | ~35MB |
| **Startup время** | ~2-3s | ~1-2s |
| **Concurrent requests** | 8000-12000/s | 10000-15000/s |
| **CPU эффективность** | Отличная | Хорошая |

## 🐳 Запуск в Docker контейнере

### Метод 1: Docker Compose (Рекомендуется)

```bash
# 1. Клонирование репозитория
git clone https://github.com/KalininAY/telegram-linux.git
cd telegram-linux/python

# 2. Настройка пароля sudo (опционально)
export SUDO_PASSWORD="your_actual_password"

# 3. Запуск одной командой
docker-compose up -d

# 4. Проверка работы
curl http://localhost:3000/health
```

### Метод 2: Обычный Docker

```bash
# 1. Переход в директорию
cd telegram-linux/python

# 2. Сборка образа
docker build -t telegram-linux-python .

# 3. Запуск контейнера

docker run -d \
  --name telegram-linux \
  -p 3000:3000 \
  -e SUDO_PASSWORD="your_password" \
  --restart unless-stopped \
  --security-opt no-new-privileges:true \
  telegram-linux-python

# 4. Проверка логов
docker logs telegram-linux
```

### Метод 3: С внешним конфигом

```bash
# 1. Создание конфигурационного файла
cat > config.json << EOF
{
  "sudoPassword": "your_actual_password",
  "port": 3000
}
EOF

# 2. Запуск с монтированием конфига
docker run -d \
  --name telegram-linux \
  -p 3000:3000 \
  -v $(pwd)/config.json:/app/config.json:ro \
  --restart unless-stopped \
  telegram-linux-python
```

### Метод 4: Быстрый тест без сборки

```bash
# Использование готового образа из Docker Hub (если будет опубликован)
docker run -d \
  --name telegram-linux-test \
  -p 3000:3000 \
  -e SUDO_PASSWORD="test123" \
  kalininay/telegram-linux:latest
```

## 🔧 Конфигурация контейнера

### Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|---------------|
| `SUDO_PASSWORD` | Пароль для sudo команд | пусто |
| `PORT` | Порт сервера | 3000 |

### Монтирование томов

```bash
# Монтирование конфига
-v /path/to/config.json:/app/config.json:ro

# Монтирование логов (если нужно)
-v /var/log/telegram-linux:/app/logs

# Доступ к системным файлам хоста (осторожно!)
-v /etc:/host/etc:ro
-v /var:/host/var:ro
```

### Сетевые настройки

```bash
# Стандартный порт
-p 3000:3000

# Другой порт
-p 8080:3000

# Только локальный доступ  
-p 127.0.0.1:3000:3000

# Доступ из определенной сети
--network custom-network
```

## 🛠 Управление контейнером

### Основные команды

```bash
# Просмотр статуса
docker ps

# Просмотр логов
docker logs telegram-linux
docker logs -f telegram-linux  # следить за логами

# Мониторинг ресурсов
docker stats telegram-linux

# Вход в контейнер
docker exec -it telegram-linux /bin/bash

# Остановка
docker stop telegram-linux

# Перезапуск
docker restart telegram-linux

# Удаление
docker rm telegram-linux
```

### Обновление контейнера

```bash
# 1. Остановка текущего контейнера
docker stop telegram-linux

# 2. Удаление контейнера
docker rm telegram-linux

# 3. Пересборка образа
docker build -t telegram-linux-python .

# 4. Запуск нового контейнера
docker run -d --name telegram-linux -p 3000:3000 telegram-linux-python
```

## 📡 API Endpoints

### POST /execute
Выполнение команды терминала:

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
  "stdout": "total 12\ndrwxr-xr-x 3 appuser appuser 4096 Oct 30 19:00 .",
  "stderr": "",
  "command": "ls -la",
  "execution_time": 0.045
}
```

### GET /health
Проверка состояния сервера и системы:

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
Интерактивная документация API (Swagger UI):
```
http://localhost:3000/docs
```

### GET /
Информация о сервере:
```bash
curl http://localhost:3000/
```

## 🎯 Примеры использования

### Системный мониторинг
```bash
# Информация о системе
curl -X POST http://localhost:3000/execute \
  -H "Content-Type: application/json" \
  -d '{"command": "free -h && df -h && uptime"}'

# Топ процессов
curl -X POST http://localhost:3000/execute \
  -d '{"command": "ps aux --sort=-%cpu | head -10"}'
```

### Управление сервисами
```bash
# Статус nginx
curl -X POST http://localhost:3000/execute \
  -d '{"command": "sudo systemctl status nginx"}'

# Перезапуск сервиса
curl -X POST http://localhost:3000/execute \
  -d '{"command": "sudo systemctl restart nginx"}'
```

### Работа с файлами
```bash
# Просмотр содержимого файла
curl -X POST http://localhost:3000/execute \
  -d '{"command": "cat /etc/os-release"}'

# Поиск файлов
curl -X POST http://localhost:3000/execute \
  -d '{"command": "find /var/log -name \"*.log\" -mtime -1"}'
```

### Сетевые операции
```bash
# Проверка портов
curl -X POST http://localhost:3000/execute \
  -d '{"command": "netstat -tlnp"}'

# Ping тест
curl -X POST http://localhost:3000/execute \
  -d '{"command": "ping -c 3 google.com", "timeout": 15}'
```

## 🔒 Безопасность контейнера

### Настройки безопасности
- **Непривилегированный пользователь**: приложение работает под `appuser`
- **No new privileges**: `--security-opt no-new-privileges:true`
- **Ограничения ресурсов**: лимиты CPU и памяти
- **Read-only конфиг**: монтирование `config.json` в режиме только чтения

### Рекомендации
```bash
# Использование secrets для паролей
echo "your_password" | docker secret create sudo_pass -

# Ограничение сетевого доступа
docker run --network none telegram-linux-python

# Монтирование только необходимых директорий
-v /specific/path:/app/data:ro
```

## 📈 Мониторинг и отладка

### Просмотр логов
```bash
# Все логи
docker logs telegram-linux

# Последние 50 строк
docker logs --tail 50 telegram-linux

# Следить за логами в реальном времени
docker logs -f telegram-linux

# Логи с временными метками
docker logs -t telegram-linux
```

### Мониторинг ресурсов
```bash
# Статистика ресурсов
docker stats telegram-linux

# Детальная информация
docker inspect telegram-linux

# Процессы в контейнере
docker exec telegram-linux ps aux
```

### Health check
```bash
# Автоматическая проверка здоровья
docker run --health-cmd="curl -f http://localhost:3000/health || exit 1" \
  --health-interval=30s \
  --health-timeout=10s \
  --health-retries=3 \
  telegram-linux-python
```

## 🚀 Производственное развертывание

### Docker Compose для продакшена

```yaml
version: '3.8'

services:
  telegram-linux:
    build: .
    ports:
      - "127.0.0.1:3000:3000"  # Только локальный доступ
    environment:
      - SUDO_PASSWORD_FILE=/run/secrets/sudo_password
    secrets:
      - sudo_password
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    deploy:
      resources:
        limits:
          memory: 128M
          cpus: '0.5'
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

secrets:
  sudo_password:
    file: ./sudo_password.txt
```

### Автоматическое обновление
```bash
# Watchtower для автообновления
docker run -d \
  --name watchtower \
  -v /var/run/docker.sock:/var/run/docker.sock \
  containrrr/watchtower telegram-linux
```

## 🤝 Почему Python FastAPI?

**Преимущества для домашнего использования:**

1. **Экономия ресурсов**: образ в 3 раза меньше Node.js
2. **Простота поддержки**: читаемый Python код
3. **Встроенные возможности**: psutil для мониторинга системы
4. **Безопасность**: строгая типизация с Pydantic
5. **Документация**: автогенерация OpenAPI/Swagger
6. **DevOps-friendly**: богатая экосистема системных инструментов

## 📝 Лицензия

MIT License
