from fastapi import FastAPI, Request
import requests
import os
from dotenv import load_dotenv

from app.ai import ask_ai
from app.conversation.dialog_engine import DialogEngine
from app.conversation.state_manager import StateManager

load_dotenv()

app = FastAPI()

ASTRO_TOKEN = os.getenv("ASTRO_TOKEN")
INTERVIEW_TOKEN = os.getenv("INTERVIEW_TOKEN")


@app.get("/")
def health():
    return {"status": "Trishika Labs conversational astrology engine running"}


@app.post("/webhook/{bot_token}")
async def telegram_webhook(bot_token: str, request: Request):

    data = await request.json()

    message = data.get("message")

    if not message:
        return {"ok": True}

    chat_id = message["chat"]["id"]
    user_id = str(message["from"]["id"])
    text = message.get("text", "").strip()

    reply = None

    # ======================================================
    # ASTROLOGY BOT
    # ======================================================

    if bot_token == ASTRO_TOKEN:

        try:

            session = StateManager.get_session(user_id)

            reply = DialogEngine.process(
                user_id=user_id,
                text=text,
                session=session
            )

        except Exception as e:

            reply = "System error. Please try again."

    # ======================================================
    # INTERVIEW BOT
    # ======================================================

    elif bot_token == INTERVIEW_TOKEN:

        try:

            reply = ask_ai(
                """You are a strict interview evaluator.

Evaluate the candidate's answer.

Respond exactly in this format:

Score (0-10):
Breakdown:
- Relevance:
- Depth:
- Structure:
- Clarity:
Strengths:
Weaknesses:
Improved Model Answer:
""",
                text
            )

            if not reply:
                reply = "Evaluation unavailable."

        except Exception:
            reply = "Evaluation service temporarily unavailable."

    else:

        reply = "Invalid bot token."

    # ======================================================
    # TELEGRAM MESSAGE SEND
    # ======================================================

    if not reply or not isinstance(reply, str):
        reply = "System error."

    try:

        requests.post(
            f"https://api.telegram.org/bot{bot_token}/sendMessage",
            json={
                "chat_id": chat_id,
                "text": reply
            }
        )

    except Exception:
        pass

    return {"ok": True}