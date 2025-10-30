# Telegram Linux Server (Python FastAPI)

Высокопроизводительный сервер для выполнения команд терминала с автоматической обработкой sudo пароля.

## 🚀 Особенности

- **FastAPI** - современный, быстрый веб-фреймворк
- **Асинхронное выполнение** команд
- **Автоматическая проверка** sudo прав (`sudo -n true`)
- **Умный ввод пароля** sudo при необходимости
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

```bash
# Перейти в рабочий каталог проекта
cd telegram-linux

# Обновить локальный репозиторий
git pull origin main

# Остановить и удалить запущенные контейнеры
 docker-compose down

# Построить докер образ без кеша
 docker-compose build --no-cache

# Установить sudo пароль в shell
 export SUDO_PASSWORD="your_sudo_password"

# Запустить контейнер в фоне с автоперезапуском
 docker-compose up -d

# Проверить логи (опционально)
 docker-compose logs -f

# Проверить статус сервера
 curl http://localhost:3000/

# Выполнить тестовую команду
 curl -X POST http://localhost:3000/execute \
    -H "Content-Type: application/json" \
    -d '{"command":"whoami"}'

# Остановить контейнер
 docker-compose stop
```

## 🔧 Конфигурация контейнера

### Переменные окружения

| Переменная | Описание | По умолчанию |
|------------|----------|---------------|
| `SUDO_PASSWORD` | Пароль для sudo команд | пусто |
| `PORT` | Порт сервера | 3000 |

### Сетевые настройки

```bash
# Переопределение порта
-p 8080:3000

# Только локальный доступ
-p 127.0.0.1:3000:3000

# Доступ для определенной сети
--network custom-network
```

## 🔒 Безопасность

- Непривилегированный пользователь `appuser`
- Опция `--security-opt no-new-privileges:true`
- Ограничение ресурсов (CPU, RAM)
- Read only режим для config.json

## 📡 API Endpoints

### POST /execute
Выполнение команды терминала

```bash
curl -X POST http://localhost:3000/execute \
  -H "Content-Type: application/json" \
  -d '{"command": "ls -la"}'
```

**Пример ответа:**

```json
{
  "success": true,
  "exit_code": 0,
  "stdout": "total 12\ndrwxr-xr-x ...",
  "stderr": "",
  "command": "ls -la"
}
```

## 📝 Лицензия

MIT License
