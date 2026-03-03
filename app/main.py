from fastapi import FastAPI, Request
import requests
import os
from dotenv import load_dotenv

from app.ai import ask_ai
from app.database import SessionLocal, Session
from app.astrologer_prompts import AstrologerPrompts
from app.astro_engine import ParashariEngine

load_dotenv()

app = FastAPI()

ASTRO_TOKEN = os.getenv("ASTRO_TOKEN")
INTERVIEW_TOKEN = os.getenv("INTERVIEW_TOKEN")


@app.get("/")
def health():
    return {"status": "Trishika Labs running (WSL + Swiss)"}


@app.post("/webhook/{bot_token}")
async def telegram_webhook(bot_token: str, request: Request):

    try:
        data = await request.json()
    except Exception:
        return {"ok": True}

    message = data.get("message")
    if not message:
        return {"ok": True}

    chat_id = message["chat"]["id"]
    user_id = str(message["from"]["id"])
    text = message.get("text", "").strip()

    # ==============================
    # ASTROLOGY BOT
    # ==============================
    if bot_token == ASTRO_TOKEN:

        db = SessionLocal()
        session = db.query(Session).filter(Session.user_id == user_id).first()

        if not session:
            session = Session(user_id=user_id, step="start")
            db.add(session)
            db.commit()

        if text == "/start":
            session.step = "dob"
            reply = "Enter Date of Birth (DD-MM-YYYY)"

        elif session.step == "dob":
            session.dob = text
            session.step = "tob"
            reply = "Enter Time of Birth (HH:MM or H:MM AM/PM)"

        elif session.step == "tob":
            session.tob = text
            session.step = "place"
            reply = "Enter Place of Birth (City, India)"

        elif session.step == "place":
            session.place = text
            session.step = "question"
            reply = "What would you like to know? (Career, Marriage, Finance, Health)"

        elif session.step == "question":

            user_query = text

            # TEMP: Hardcoded Delhi coordinates
            lat = 28.6139
            lon = 77.2090

            try:
                chart_data = ParashariEngine.generate_chart(
                    session.dob,
                    session.tob,
                    lat,
                    lon
                )
            except Exception as e:
                db.close()
                return {
                    "ok": True
                }

             astro_data = chart_data

            full_prompt = AstrologerPrompts.build_qa_prompt(
                user_query,
                astro_data
            )

            reply = ask_ai("", full_prompt)

            session.step = "start"

        else:
            reply = "Type /start to begin astrology reading."

        db.commit()
        db.close()

    # ==============================
    # INTERVIEW BOT
    # ==============================
    elif bot_token == INTERVIEW_TOKEN:

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
            text,
        )

    else:
        reply = "Invalid bot token."

    # Send reply to Telegram
    requests.post(
        f"https://api.telegram.org/bot{bot_token}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": reply
        }
    )

    return {"ok": True}