from dotenv import load_dotenv
import os
import requests

load_dotenv()

AI_KEY = os.getenv("AI_API_KEY")

def ask_ai(messages_array):
    headers = {
        "Authorization": f"Bearer {AI_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-4o-mini",
        "temperature": 0.2,
        "presence_penalty": 0.1,
        "messages": messages_array
    }

    try:
        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=15
        )
        response_json = r.json()

        if "choices" not in response_json:
            return "Maaf kijiye, abhi server mein thodi samasya hai. Kripya thodi der baad prayas karein."

        return response_json["choices"][0]["message"]["content"]
    except Exception as e:
        return "Maaf kijiye, connection error. Kripya dobara likhein."