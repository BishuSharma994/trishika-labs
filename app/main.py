from fastapi import FastAPI, Request
import requests
import os
from dotenv import load_dotenv
from datetime import datetime

from app.ai import ask_ai
from app.database import SessionLocal, Session
from app.astro_engine import ParashariEngine
from app.astrologer_prompts import AstrologerPrompts

load_dotenv()

app = FastAPI()

ASTRO_TOKEN = os.getenv("ASTRO_TOKEN")
INTERVIEW_TOKEN = os.getenv("INTERVIEW_TOKEN")


@app.get("/")
def health():
    return {"status": "Trishika Labs running (Deterministic + LLM Layer)"}


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

    # =========================================================
    # ASTROLOGY BOT
    # =========================================================
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
            reply = "Enter Time of Birth (HH:MM, 24hr or AM/PM)"

        elif session.step == "tob":
            session.tob = text
            session.step = "place"
            reply = "Enter Place of Birth (City, India)"

        elif session.step == "place":
            session.place = text
            session.step = "question"
            reply = "What would you like to know? (Career, Marriage, Finance, Health)"

        elif session.step == "question":

            user_query = text.lower()

            # Temporary fixed coordinates (Delhi)
            lat = 28.6139
            lon = 77.2090

            # =====================================================
            # INPUT NORMALIZATION (CRITICAL FIX)
            # =====================================================

            try:
                # Normalize DOB: DD-MM-YYYY → YYYY-MM-DD
                dob_obj = datetime.strptime(session.dob, "%d-%m-%Y")
                dob_normalized = dob_obj.strftime("%Y-%m-%d")

                # Normalize Time
                try:
                    time_obj = datetime.strptime(session.tob, "%H:%M")
                except ValueError:
                    time_obj = datetime.strptime(session.tob, "%I:%M %p")

                time_normalized = time_obj.strftime("%H:%M")

            except Exception:
                reply = "Invalid date or time format. Use DD-MM-YYYY and HH:MM."
                session.step = "start"
                db.commit()
                db.close()

                requests.post(
                    f"https://api.telegram.org/bot{bot_token}/sendMessage",
                    json={"chat_id": chat_id, "text": reply}
                )

                return {"ok": True}

            # =====================================================
            # GENERATE CHART (CACHED SAFE)
            # =====================================================

            chart_data = ParashariEngine.generate_chart(
                dob_normalized,
                time_normalized,
                lat,
                lon
            )

            domains = chart_data.get("domain_scores", {})

            if user_query not in domains:
                reply = "Invalid selection. Choose Career, Marriage, Finance, or Health."
            else:
                deterministic_data = domains[user_query].copy()
                deterministic_data["domain"] = user_query

                header = (
                    f"{user_query.capitalize()} Score: {deterministic_data['score']}/100\n"
                    f"Primary Driver: {deterministic_data['primary_driver']}\n"
                    f"Risk Factor: {deterministic_data['risk_factor']}\n"
                    f"Momentum: {deterministic_data['momentum']}\n\n"
                )

                ai_prompt = AstrologerPrompts.build_deterministic_prompt(
                    user_query,
                    deterministic_data
                )

                try:
                    ai_response = ask_ai("", ai_prompt)

                    if ai_response and isinstance(ai_response, str) and len(ai_response.strip()) > 5:
                        reply = header + ai_response
                    else:
                        reply = header

                except Exception:
                    reply = header

            session.step = "start"

        else:
            reply = "Type /start to begin astrology reading."

        db.commit()
        db.close()

    # =========================================================
    # INTERVIEW BOT
    # =========================================================
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
                text,
            )

            if not reply:
                reply = "Evaluation service unavailable."

        except Exception:
            reply = "Evaluation service temporarily unavailable."

    else:
        reply = "Invalid bot token."

    # =========================================================
    # TELEGRAM SAFETY CHECK
    # =========================================================
    if not reply or not isinstance(reply, str):
        reply = "System error. Please try again."

    requests.post(
        f"https://api.telegram.org/bot{bot_token}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": reply
        }
    )

    return {"ok": True}