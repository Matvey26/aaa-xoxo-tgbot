# aaa-xoxo-tgbot
Телеграмм бот для игры в крестики-нолики

Запуск:

```bash
# cd /path/to/project

# билдим образ, если ещё не сделали этого
docker build -t xoxo-bot .

# запускаем контейнер
docker run -d \
    --name xoxo-bot \
    -e TG_TOKEN=ваш_токен \
    -v "$(pwd)/data:/data" \
    --restart unless-stopped \
    xoxo-bot
```