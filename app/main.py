from fastapi import FastAPI, Request
import requests
import os
from dotenv import load_dotenv

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

            chart_data = ParashariEngine.generate_chart(
                session.dob,
                session.tob,
                lat,
                lon
            )

            domains = chart_data.get("domain_scores", {})

            if "career" in user_query:
                domain_key = "career"
            elif "marriage" in user_query:
                domain_key = "marriage"
            elif "finance" in user_query:
                domain_key = "finance"
            elif "health" in user_query:
                domain_key = "health"
            else:
                domain_key = None

            if not domain_key or domain_key not in domains:
                reply = "Invalid selection. Choose Career, Marriage, Finance, or Health."
            else:
                deterministic_data = domains[domain_key]

                structured_payload = {
                    "domain": domain_key,
                    "score": deterministic_data["score"],
                    "primary_driver": deterministic_data["primary_driver"],
                    "risk_factor": deterministic_data["risk_factor"],
                    "momentum": deterministic_data["momentum"]
                }

                deterministic_header = (
                    f"{domain_key.capitalize()} Score: {structured_payload['score']}/100\n"
                    f"Primary Driver: {structured_payload['primary_driver']}\n"
                    f"Risk Factor: {structured_payload['risk_factor']}\n"
                    f"Momentum: {structured_payload['momentum']}\n\n"
                )

                ai_prompt = AstrologerPrompts.build_deterministic_prompt(
                    user_query,
                    structured_payload
                )

                try:
                    ai_response = ask_ai("", ai_prompt)

                    if ai_response and len(ai_response.strip()) > 5:
                        reply = deterministic_header + ai_response
                    else:
                        reply = deterministic_header

                except Exception:
                    reply = deterministic_header

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
    # TELEGRAM RESPONSE SAFETY
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