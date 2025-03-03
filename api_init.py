import requests
from config import HUGGINGFACE_API_TOKEN  # 匯入 token

API_URL = "https://api-inference.huggingface.co/models/cardiffnlp/twitter-roberta-base-sentiment-latest"
headers = {"Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}"}
payload = {
    "inputs": "Today is a great day",
}

response = requests.post(API_URL, headers=headers, json=payload)
print(response.json())
