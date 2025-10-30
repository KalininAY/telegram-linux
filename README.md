# Telegram Linux Server

Сервер для выполнения команд терминала с автоматической обработкой sudo пароля.

## Возможности

- Выполнение команд терминала
- Автоматическая проверка sudo прав (`sudo -n true`)
- Автоматический ввод sudo пароля из конфига при необходимости
- Возврат полного вывода команды (stdout и stderr)
- Таймаут выполнения команд (30 секунд)
- Health check endpoint
- Graceful shutdown

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/KalininAY/telegram-linux.git
cd telegram-linux
```

2. Установите зависимости:
```bash
npm install
```

3. Настройте конфигурацию в `config.json`:
```json
{
  "sudoPassword": "ваш_sudo_пароль",
  "port": 3000
}
```

## Использование

### Запуск сервера

```bash
# Обычный запуск
npm start

# Запуск в режиме разработки (с автоперезапуском)
npm run dev

# Или напрямую
node server.js
```

### API

#### POST /execute
Выполнить команду терминала.

**Запрос:**
```json
{
  "command": "ls -la"
}
```

**Ответ:**
```json
{
  "success": true,
  "exitCode": 0,
  "stdout": "total 12\ndrwxr-xr-x 3 user user 4096 Oct 30 20:00 .\n...",
  "stderr": "",
  "command": "ls -la"
}
```

## Лицензия

MIT License
