import os
import requests

def send(text):
    url = f"https://api.telegram.org/bot6758725446:AAHsGUtzyHDNW9hihYggXhL1_4kOoliTagQ/sendMessage"
    payload = {"chat_id": ID, "text": text}

    r = requests.post(url, json=payload)
    return r


username = os.getlogin()

send(f"{username} completed the task!")
