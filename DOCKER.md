# 🐳 Docker Deployment Guide

## Быстрый старт с Docker

### Предварительные требования
- Docker Desktop (Windows/Mac) или Docker Engine (Linux)
- Docker Compose (обычно включен в Docker Desktop)

### 1. Клонирование репозитория
```bash
git clone https://github.com/kioshini/itis.git
cd itis
```

### 2. Настройка переменных окружения
Создайте файл `.env` из примера:
```bash
cp .env.example .env
```

Отредактируйте `.env` и укажите ваши API ключи:
```env
BOT_TOKEN=your_telegram_bot_token
OPENROUTER_API_KEY=your_openrouter_key
RAWG_API_KEY=your_rawg_key
OPENROUTER_MODEL=deepseek/deepseek-chat
DATABASE_PATH=/app/data/bot_database.db
```

### 3. Запуск с Docker Compose (рекомендуется)

**Сборка и запуск:**
```bash
docker-compose up -d
```

**Просмотр логов:**
```bash
docker-compose logs -f
```

**Остановка:**
```bash
docker-compose down
```

**Перезапуск:**
```bash
docker-compose restart
```

### 4. Запуск с Docker (без compose)

**Сборка образа:**
```bash
docker build -t game-finder-bot .
```

**Запуск контейнера:**
```bash
docker run -d \
  --name game-finder-bot \
  --restart unless-stopped \
  -e BOT_TOKEN="your_token" \
  -e OPENROUTER_API_KEY="your_key" \
  -e RAWG_API_KEY="your_key" \
  -v $(pwd)/data:/app/data \
  game-finder-bot
```

**Просмотр логов:**
```bash
docker logs -f game-finder-bot
```

**Остановка:**
```bash
docker stop game-finder-bot
docker rm game-finder-bot
```

## Полезные команды

### Управление контейнером
```bash
# Проверка статуса
docker-compose ps

# Просмотр логов в реальном времени
docker-compose logs -f game-finder-bot

# Вход в контейнер
docker-compose exec game-finder-bot /bin/bash

# Перезапуск после изменений
docker-compose restart

# Пересборка после изменения кода
docker-compose up -d --build
```

### Очистка
```bash
# Удалить контейнер и volumes
docker-compose down -v

# Удалить все неиспользуемые образы
docker system prune -a
```

## Структура данных

База данных и логи сохраняются в директории `./data`:
```
data/
└── bot_database.db    # SQLite база с историей запросов
```

## Мониторинг

### Просмотр использования ресурсов:
```bash
docker stats game-finder-bot
```

### Проверка здоровья контейнера:
```bash
docker inspect game-finder-bot
```

## Обновление

### Обновление до новой версии:
```bash
# Получить последние изменения
git pull

# Пересобрать и перезапустить
docker-compose up -d --build
```

## Troubleshooting

### Бот не запускается:
1. Проверьте логи: `docker-compose logs`
2. Убедитесь, что файл `.env` создан и заполнен
3. Проверьте правильность API ключей

### Ошибки с базой данных:
```bash
# Удалить старую базу и пересоздать
rm -rf data/
docker-compose restart
```

### Контейнер постоянно перезапускается:
```bash
# Смотрим подробные логи
docker logs game-finder-bot --tail 100

# Проверяем конфигурацию
docker-compose config
```

## Production Deployment

Для production окружения рекомендуется:

1. **Использовать secrets для чувствительных данных:**
```yaml
# docker-compose.prod.yml
services:
  game-finder-bot:
    secrets:
      - bot_token
      - openrouter_key
      - rawg_key

secrets:
  bot_token:
    external: true
  openrouter_key:
    external: true
  rawg_key:
    external: true
```

2. **Настроить health checks:**
```dockerfile
HEALTHCHECK --interval=30s --timeout=3s \
  CMD python -c "import sqlite3; sqlite3.connect('/app/data/bot_database.db')" || exit 1
```

3. **Использовать reverse proxy (nginx):**
```nginx
# Для webhook режима (опционально)
location /webhook {
    proxy_pass http://game-finder-bot:8080;
}
```

## Автоматический деплой с GitHub Actions

Создайте `.github/workflows/docker-deploy.yml` для автоматической сборки:
```yaml
name: Docker Build and Push

on:
  push:
    branches: [ main ]
    tags: [ 'v*' ]

jobs:
  docker:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: docker/build-push-action@v5
        with:
          push: true
          tags: ghcr.io/kioshini/game-finder-bot:latest
```

## Безопасность

⚠️ **Важно:**
- Никогда не коммитьте файл `.env` в Git
- Используйте `.dockerignore` для исключения чувствительных данных
- Регулярно обновляйте базовый образ Python
- Используйте read-only volumes где возможно

## Поддержка

При возникновении проблем создайте issue: https://github.com/kioshini/itis/issues
