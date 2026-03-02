from dotenv import load_dotenv
import os
import requests

load_dotenv()

AI_KEY = os.getenv("AI_API_KEY")

def ask_ai(system_prompt, user_text):
    headers = {
        "Authorization": f"Bearer {AI_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-4.1-mini",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_text}
        ]
    }

    r = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        json=data
    )

    response_json = r.json()

    if "choices" not in response_json:
        return f"AI Error: {response_json}"

    return response_json["choices"][0]["message"]["content"]