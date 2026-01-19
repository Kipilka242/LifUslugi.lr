import requests
import json
import os
import time

TOKEN = os.getenv("TELEGRAM_TOKEN")
URL = f"https://api.telegram.org/bot{TOKEN}/getUpdates"

DATA_FILE = "data.json"
OFFSET_FILE = "offset.txt"
MAX_AGE = 24 * 3600  # 24 часа

# Загружаем старые данные
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
else:
    data = {"updTime": "", "chats": {}}

# Загружаем offset
if os.path.exists(OFFSET_FILE):
    with open(OFFSET_FILE, "r") as f:
        offset = int(f.read().strip())
else:
    offset = 0

# Получаем обновления
resp = requests.get(URL, params={"offset": offset}).json()

now = int(time.time())
data["updTime"] = time.strftime("%H:%M")

for update in resp.get("result", []):
    update_id = update["update_id"]
    msg = update.get("message")
    if not msg:
        continue

    # Должен быть автофорвард
    if not msg.get("is_automatic_forward"):
        continue

    # Определяем канал
    channel = None

    if msg.get("sender_chat", {}).get("type") == "channel":
        channel = msg["sender_chat"]

    elif msg.get("forward_origin", {}).get("type") == "channel":
        channel = msg["forward_origin"]["chat"]

    elif msg.get("forward_from_chat", {}).get("type") == "channel":
        channel = msg["forward_from_chat"]

    if not channel:
        continue

    chat_title = channel.get("title", "Без названия")
    text = msg.get("text", "")
    date = msg.get("forward_date", msg.get("date", now))

    if chat_title not in data["chats"]:
        data["chats"][chat_title] = []

    data["chats"][chat_title].append({
        "text": text,
        "date": date
    })

    # Обновляем offset
    offset = update_id + 1

# Сохраняем offset
with open(OFFSET_FILE, "w") as f:
    f.write(str(offset))

# Удаляем посты старше 24 часов
for chat in list(data["chats"].keys()):
    data["chats"][chat] = [
        post for post in data["chats"][chat]
        if now - post["date"] <= MAX_AGE
    ]

    if not data["chats"][chat]:
        del data["chats"][chat]

# Сохраняем данные
with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
