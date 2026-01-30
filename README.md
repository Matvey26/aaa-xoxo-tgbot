# aaa-xoxo-tgbot
Телеграмм бот для игры в крестики-нолики

Запуск:

```bash
docker stop xoxo-bot || true
docker rm xoxo-bot || true

echo "Build new image..."
docker build -t xoxo-bot .

echo "Run container"
docker run -d \
    --name xoxo-bot \
    -e TG_TOKEN=... \
    -v "$(pwd)/data:/data" \
    --restart unless-stopped \
    xoxo-bot

echo "Deploy complete"
```