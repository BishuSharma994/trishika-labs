from fastapi import FastAPI, Request
import requests
import os
import json
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
    return {"status": "Trishika Labs running (Deterministic + Conversational Engine)"}


@app.post("/webhook/{bot_token}")
async def telegram_webhook(bot_token: str, request: Request):

    data = await request.json()
    message = data.get("message")

    if not message:
        return {"ok": True}

    chat_id = message["chat"]["id"]
    user_id = str(message["from"]["id"])
    text = message.get("text", "").strip().lower()

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

        # =====================================================
        # START FLOW
        # =====================================================
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
            reply = "Birth details saved. Ask about Career, Marriage, Finance, or Health."

        # =====================================================
        # CONVERSATIONAL ENGINE
        # =====================================================
        elif session.step == "question":

            # =============================
            # NORMALIZE DOB + TIME
            # =============================
            try:
                dob_obj = datetime.strptime(session.dob, "%d-%m-%Y")
                dob_normalized = dob_obj.strftime("%Y-%m-%d")

                try:
                    time_obj = datetime.strptime(session.tob, "%H:%M")
                except ValueError:
                    time_obj = datetime.strptime(session.tob, "%I:%M %p")

                time_normalized = time_obj.strftime("%H:%M")

            except Exception:
                reply = "Invalid date or time format. Restart with /start"
                session.step = "start"
                db.commit()
                db.close()

                requests.post(
                    f"https://api.telegram.org/bot{bot_token}/sendMessage",
                    json={"chat_id": chat_id, "text": reply}
                )
                return {"ok": True}

            lat = 28.6139
            lon = 77.2090

            # =============================
            # CHART CACHE
            # =============================
            if not session.chart_data:
                chart_data = ParashariEngine.generate_chart(
                    dob_normalized,
                    time_normalized,
                    lat,
                    lon
                )
                session.chart_data = json.dumps(chart_data)
            else:
                chart_data = json.loads(session.chart_data)

            domains = chart_data.get("domain_scores", {})

            # =============================
            # DOMAIN RESOLUTION
            # =============================
            domain_keywords = {
                "finance": ["finance", "money", "income"],
                "career": ["career", "job", "promotion"],
                "marriage": ["marriage", "relationship", "love"],
                "health": ["health", "disease", "fitness"]
            }

            resolved_domain = None

            for domain, words in domain_keywords.items():
                if any(word in text for word in words):
                    resolved_domain = domain
                    break

            if resolved_domain:
                session.last_domain = resolved_domain
            elif session.last_domain:
                resolved_domain = session.last_domain
            else:
                resolved_domain = "career"

            domain_data = domains.get(resolved_domain)

            # =============================
            # PROJECTION HANDLER
            # =============================
            if text in ["next", "future", "projection", "next year"]:

                projection = domain_data.get("projection_12m", [])
                volatility = domain_data.get("volatility")
                dominant = chart_data.get("dominance", {}).get("dominant_planet")

                reply = (
                    f"{resolved_domain.upper()} PROJECTION (12 Months):\n"
                    f"{projection}\n\n"
                    f"Volatility Index: {volatility}\n"
                    f"Dominant Planet Phase: {dominant}"
                )

            # =============================
            # STANDARD DOMAIN RESPONSE
            # =============================
            else:

                header = (
                    f"{resolved_domain.capitalize()} Score: {domain_data['score']}/100\n"
                    f"Primary Driver: {domain_data['primary_driver']}\n"
                    f"Risk Factor: {domain_data['risk_factor']}\n"
                    f"Momentum: {domain_data['momentum']}\n"
                    f"Volatility: {domain_data.get('volatility')}\n"
                    f"Dominant Planet: {chart_data.get('dominance', {}).get('dominant_planet')}\n\n"
                )

                deterministic_data = domain_data.copy()
                deterministic_data["domain"] = resolved_domain

                ai_prompt = AstrologerPrompts.build_deterministic_prompt(
                    resolved_domain,
                    deterministic_data
                )

                try:
                    ai_response = ask_ai("", ai_prompt)

                    if ai_response and len(ai_response.strip()) > 5:
                        reply = header + ai_response
                    else:
                        reply = header

                except Exception:
                    reply = header

            # 🔁 KEEP USER IN QUESTION MODE
            session.step = "question"

        else:
            reply = "Type /start to begin."

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
                reply = "Evaluation unavailable."

        except Exception:
            reply = "Evaluation service temporarily unavailable."

    else:
        reply = "Invalid bot token."

    # =========================================================
    # TELEGRAM SAFE SEND
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