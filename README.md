# aaa-xoxo-tgbot
Телеграмм бот для игры в крестики-нолики

Запуск:

```bash
docker run -d --name aaa-xoxo-bot -e TG_TOKEN=... -v ~/workspace/aaa-xoxo-bot/data:/data --restart unless-stopped aaa-xoxo-bot
```