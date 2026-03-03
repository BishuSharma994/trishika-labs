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


# =========================================================
# LANGUAGE DETECTION
# =========================================================

def detect_language(text: str):
    hindi_keywords = [
        "kaun", "kab", "kya", "kaunsi", "shubh",
        "ghar", "gadi", "vivah", "shaadi"
    ]
    if any(word in text.lower() for word in hindi_keywords):
        return "hi"
    return "en"


# =========================================================
# INTENT DETECTION
# =========================================================

def detect_intent(text: str):
    text = text.lower()

    if "gadi" in text or "vehicle" in text or "car" in text:
        return "vehicle"

    if "ghar" in text or "property" in text or "house" in text:
        return "property"

    if "promotion" in text:
        return "promotion"

    if "kab" in text or "when" in text:
        return "timing"

    if text in ["next", "future", "projection", "next year"]:
        return "projection"

    return "general"


@app.get("/")
def health():
    return {"status": "Trishika Labs running (Conversational Astrology Engine)"}


@app.post("/webhook/{bot_token}")
async def telegram_webhook(bot_token: str, request: Request):

    data = await request.json()
    message = data.get("message")

    if not message:
        return {"ok": True}

    chat_id = message["chat"]["id"]
    user_id = str(message["from"]["id"])
    text_raw = message.get("text", "").strip()
    text = text_raw.lower()

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

        # -----------------------------------------------------
        # START FLOW
        # -----------------------------------------------------
        if text == "/start":
            session.step = "dob"
            reply = "Enter Date of Birth (DD-MM-YYYY)"

        elif session.step == "dob":
            session.dob = text_raw
            session.step = "tob"
            reply = "Enter Time of Birth (HH:MM, 24hr or AM/PM)"

        elif session.step == "tob":
            session.tob = text_raw
            session.step = "place"
            reply = "Enter Place of Birth (City, India)"

        elif session.step == "place":
            session.place = text_raw
            session.step = "question"
            reply = "Birth details saved. Ask about Career, Marriage, Finance, Health, Gadi, or Ghar."

        # -----------------------------------------------------
        # CONVERSATIONAL ENGINE
        # -----------------------------------------------------
        elif session.step == "question":

            language = detect_language(text)
            intent = detect_intent(text)

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

            # =====================================================
            # VEHICLE INTENT (4th House)
            # =====================================================
            if intent == "vehicle":

                if language == "hi":
                    reply = (
                        "Aapke 4th house mein grahon ka prabhav dikh raha hai.\n"
                        "Moon aur Venus ka support vehicle purchase ke liye shubh mana jata hai.\n\n"
                        "Aap colour ya timing ke baare mein pooch sakte hain."
                    )
                else:
                    reply = (
                        "Your 4th house governs vehicles and property.\n"
                        "Support from Moon and Venus indicates favorable vehicle purchase.\n\n"
                        "You may ask about color or timing."
                    )

            # =====================================================
            # PROPERTY INTENT
            # =====================================================
            elif intent == "property":

                if language == "hi":
                    reply = (
                        "4th house ghar aur property ka pratinidhi hai.\n"
                        "Current dasha moderate support dikha rahi hai.\n\n"
                        "Aap timing ya direction pooch sakte hain."
                    )
                else:
                    reply = (
                        "The 4th house represents home and property.\n"
                        "Current planetary period shows moderate support.\n\n"
                        "You may ask about timing or direction."
                    )

            # =====================================================
            # DOMAIN RESOLUTION
            # =====================================================
            else:

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

                # --------------------------
                # PROJECTION
                # --------------------------
                if intent == "projection":

                    projection = domain_data.get("projection_12m", [])
                    volatility = domain_data.get("volatility")
                    dominant = chart_data.get("dominance", {}).get("dominant_planet")

                    if language == "hi":
                        reply = (
                            f"{resolved_domain.capitalize()} ke agle 12 mahino ka trend:\n"
                            f"{projection}\n\n"
                            f"Volatility Index: {volatility}\n"
                            f"Dominant Planet Phase: {dominant}"
                        )
                    else:
                        reply = (
                            f"{resolved_domain.capitalize()} 12-Month Projection:\n"
                            f"{projection}\n\n"
                            f"Volatility Index: {volatility}\n"
                            f"Dominant Planet Phase: {dominant}"
                        )

                # --------------------------
                # STANDARD DOMAIN OUTPUT
                # --------------------------
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
                text_raw,
            )

            if not reply:
                reply = "Evaluation unavailable."

        except Exception:
            reply = "Evaluation service temporarily unavailable."

    else:
        reply = "Invalid bot token."

    # =========================================================
    # TELEGRAM SAFE SEND + BUTTONS
    # =========================================================

    keyboard = {
        "keyboard": [
            ["Kaunsi colour ki gadi shubh rahegi?", "Gadi kab leni chahiye?"],
            ["Which car brand suits me?", "Best time to buy vehicle?"]
        ],
        "resize_keyboard": True
    }

    if not reply or not isinstance(reply, str):
        reply = "System error. Please try again."

    requests.post(
        f"https://api.telegram.org/bot{bot_token}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": reply,
            "reply_markup": keyboard
        }
    )

    return {"ok": True}