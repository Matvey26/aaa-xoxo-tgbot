# aaa-xoxo-tgbot
Телеграмм бот для игры в крестики-нолики

Тесты:

```
pytest test.py
```

Первичная настройка (и после каждого git pull origin main):

```bash
docker stop xoxo-bot || true
docker rm xoxo-bot || true

echo "Build new image..."
docker build -t xoxo-bot .
```

Запуск:

```bash
echo "Run container"
docker run -d \
    --name xoxo-bot \
    -e TG_TOKEN=... \
    -v "$(pwd)/data:/data" \
    --restart unless-stopped \
    xoxo-bot

echo "Deploy complete"
```