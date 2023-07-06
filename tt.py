import requests
ID = 1410223644

url = f"https://api.telegram.org/bot5633216566:AAGVHIaZZIHZ3ge-6ZLDbqsZX0F67szyRDo/sendMessage"
payload = {"chat_id": ID, "text": "success"}

r = requests.post(url, json=payload)
