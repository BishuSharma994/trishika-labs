from fastapi import FastAPI, Request
import requests
import os
import json
from dotenv import load_dotenv

from app.database import SessionLocal, Session
from app.conversation.dialog_engine import DialogEngine
from app.ai import ask_ai

load_dotenv()

app = FastAPI()

ASTRO_TOKEN = os.getenv("ASTRO_TOKEN")
INTERVIEW_TOKEN = os.getenv("INTERVIEW_TOKEN")


# ---------------------------------------------------------
# HEALTH CHECK
# ---------------------------------------------------------

@app.get("/")
def health():
    return {"status": "Trishika Labs running"}


# ---------------------------------------------------------
# TELEGRAM WEBHOOK
# ---------------------------------------------------------

@app.post("/webhook/{bot_token}")
async def telegram_webhook(bot_token: str, request: Request):

    data = await request.json()
    message = data.get("message")

    if not message:
        return {"ok": True}

    chat_id = message["chat"]["id"]
    user_id = str(message["from"]["id"])
    text = message.get("text", "").strip()

    reply_text = None
    reply_keyboard = None

    # =====================================================
    # ASTROLOGY BOT
    # =====================================================

    if bot_token == ASTRO_TOKEN:

        db = SessionLocal()

        # Always load fresh session
        session = db.query(Session).filter(Session.user_id == user_id).first()

        if not session:
            session = Session(user_id=user_id, step="start")
            db.add(session)
            db.commit()

            # reload newly created row
            session = db.query(Session).filter(Session.user_id == user_id).first()

        # -------------------------------------------------
        # PROCESS MESSAGE
        # -------------------------------------------------

        result = DialogEngine.process(user_id, text, session)

        # Reload session again to ensure latest updates
        session = db.query(Session).filter(Session.user_id == user_id).first()

        if isinstance(result, dict):
            reply_text = result.get("text")
            reply_keyboard = result.get("keyboard")
        else:
            reply_text = result

        db.commit()
        db.close()

    # =====================================================
    # INTERVIEW BOT
    # =====================================================

    elif bot_token == INTERVIEW_TOKEN:

        reply_text = ask_ai(
            """Evaluate candidate answer.

Score 0-10
Breakdown
Strengths
Weaknesses
Improved Answer
""",
            text
        )

    else:
        reply_text = "Invalid bot token"

    # -----------------------------------------------------

    if not reply_text:
        reply_text = "Please try again."

    payload = {
        "chat_id": chat_id,
        "text": reply_text
    }

    # Telegram keyboards must be JSON encoded
    if reply_keyboard:
        payload["reply_markup"] = json.dumps(reply_keyboard)

    requests.post(
        f"https://api.telegram.org/bot{bot_token}/sendMessage",
        json=payload
    )

    return {"ok": True}