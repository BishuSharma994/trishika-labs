import json
import logging
import os
import time  # Imported for the human-like typing delay

import requests
from dotenv import load_dotenv
from fastapi import FastAPI, Request

from app.ai import ask_ai
from app.conversation.dialog_engine import DialogEngine

load_dotenv()

app = FastAPI()
logger = logging.getLogger(__name__)

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
        try:
            result = DialogEngine.process(user_id, text, None)

            if isinstance(result, dict):
                reply_text = result.get("text")
                reply_keyboard = result.get("keyboard")
            else:
                reply_text = result
        except Exception:
            logger.exception("Astrology webhook processing failed for user_id=%s", user_id)
            reply_text = "I'm facing a temporary server issue. Please try again in a moment."

    # =====================================================
    # INTERVIEW BOT
    # =====================================================

    elif bot_token == INTERVIEW_TOKEN:

        reply_text = ask_ai(
            [
                {
                    "role": "system",
                    "content": """Evaluate candidate answer.

Score 0-10
Breakdown
Strengths
Weaknesses
Improved Answer
""",
                },
                {
                    "role": "user",
                    "content": text,
                },
            ]
        )

    else:
        reply_text = "Invalid bot token"

    # -----------------------------------------------------

    if not reply_text:
        reply_text = "Please try again."

    # Split the response into separate bubbles based on double newlines
    message_bubbles = reply_text.split("\n\n")

    # Loop through each bubble and send them individually
    for index, bubble in enumerate(message_bubbles):
        bubble = bubble.strip()

        if not bubble:
            continue  # Skip empty lines

        payload = {
            "chat_id": chat_id,
            "text": bubble
        }

        # Attach the keyboard ONLY to the very last bubble
        if index == len(message_bubbles) - 1 and reply_keyboard:
            payload["reply_markup"] = reply_keyboard

        # Send the individual bubble to Telegram
        try:
            requests.post(
                f"https://api.telegram.org/bot{bot_token}/sendMessage",
                json=payload,
                timeout=15,
            )
        except Exception as e:
            logger.error(f"Failed to send message chunk: {e}")

        # Add a 1.5-second delay before sending the next bubble, 
        # but don't delay after the very last bubble
        if index < len(message_bubbles) - 1:
            time.sleep(1.5)

    return {"ok": True}