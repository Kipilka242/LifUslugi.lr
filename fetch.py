import requests
import json
import os
import time
      - name: Run script
        env:
          TELEGRAM_TOKEN: ${{ secrets.TELEGRAM_TOKEN }}
        run: python fetch.py


TOKEN = os.getenv("TELEGRAM_TOKEN")
URL = f"https://api.telegram.org/bot{TOKEN}/getUpdates"

DATA_FILE = "data.json"
MAX_AGE = 24 * 3600  # 24 часа

# Загружаем старые данные
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
else:
    data = {"updTime": "", "chats": {}}

resp = requests.get(URL).json()

now = int(time.time())
data["updTime"] = time.strftime("%H:%M")

for update in resp.get("result", []):
    msg = update.get("message")
    if not msg:
        continue

    chat_title = msg["chat"].get("title")
    if not chat_title:
        continue  # пропускаем лички

    text = msg.get("text", "")
    date = msg.get("date", now)

    if chat_title not in data["chats"]:
        data["chats"][chat_title] = []

    data["chats"][chat_title].append({
        "text": text,
        "date": date
    })

# Удаляем посты старше 24 часов
for chat in list(data["chats"].keys()):
    data["chats"][chat] = [
        post for post in data["chats"][chat]
        if now - post["date"] <= MAX_AGE
    ]

    if not data["chats"][chat]:
        del data["chats"][chat]

# Сохраняем
with open(DATA_FILE, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
