import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
url = "https://api.groq.com/openai/v1/models"

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

response = requests.get(url, headers=headers)

if response.status_code == 200:
    models = response.json()['data']
    print("\n✅ AVAILABLE GROQ MODELS:")
    for model in models:
        print(f" - {model['id']}")
else:
    print(f"❌ Error: {response.status_code} - {response.text}")