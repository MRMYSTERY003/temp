import os
import requests
ID = 1410223644
def send(text):
    url = f"https://api.telegram.org/bot6758725446:AAHsGUtzyHDNW9hihYggXhL1_4kOoliTagQ/sendMessage"
    payload = {"chat_id": ID, "text": text}

    r = requests.post(url, json=payload)
    return r


username = os.getlogin()

send(f"{username} completed the task!")
