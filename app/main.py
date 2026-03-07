from fastapi import FastAPI, Request
import requests
import os
from dotenv import load_dotenv
from datetime import datetime
from dateutil import parser as dateparser

from app.ai import ask_ai
from app.database import SessionLocal, Session
from app.astro_engine import ParashariEngine
from app.astrologer_prompts import AstrologerPrompts

load_dotenv()

app = FastAPI()

ASTRO_TOKEN = os.getenv("ASTRO_TOKEN")
INTERVIEW_TOKEN = os.getenv("INTERVIEW_TOKEN")


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

DOMAIN_KEYWORDS = {
    "career": ["career", "job", "promotion", "work", "profession"],
    "finance": ["finance", "money", "income", "wealth", "business"],
    "marriage": ["marriage", "love", "relationship", "partner", "shaadi"],
    "health": ["health", "disease", "fitness", "illness"]
}

HINDI_WORDS = [
    "mera", "mujhe", "shaadi", "paisa", "kaam",
    "bhavishya", "kya", "kab", "kaise", "ghar", "gadi"
]


def detect_language(text: str):
    text = text.lower()
    for w in HINDI_WORDS:
        if w in text:
            return "hi"
    return "en"


def detect_domain(text: str):
    text = text.lower()
    for domain, words in DOMAIN_KEYWORDS.items():
        for w in words:
            if w in text:
                return domain
    return None


def normalize_dob(text):
    try:
        dt = dateparser.parse(text, dayfirst=True)
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return None


def normalize_time(text):
    try:
        dt = dateparser.parse(text)
        return dt.strftime("%H:%M")
    except Exception:
        return None


# ---------------------------------------------------------
# API
# ---------------------------------------------------------

@app.get("/")
def health():
    return {"status": "Trishika Labs running"}


@app.post("/webhook/{bot_token}")
async def telegram_webhook(bot_token: str, request: Request):

    data = await request.json()
    message = data.get("message")

    if not message:
        return {"ok": True}

    chat_id = message["chat"]["id"]
    user_id = str(message["from"]["id"])
    text = message.get("text", "").strip()

    reply = ""

    # =====================================================
    # ASTRO BOT
    # =====================================================
    if bot_token == ASTRO_TOKEN:

        db = SessionLocal()
        session = db.query(Session).filter(Session.user_id == user_id).first()

        if not session:
            session = Session(user_id=user_id, step="dob")
            db.add(session)
            db.commit()

        lang = detect_language(text)

        # -------------------------------
        # START
        # -------------------------------

        if text == "/start":

            session.step = "dob"

            if lang == "hi":
                reply = "Namaste. Pehle apni janam tareekh batayein."
            else:
                reply = "Welcome. Tell me your date of birth."

        # -------------------------------
        # DOB
        # -------------------------------

        elif session.step == "dob":

            dob = normalize_dob(text)

            if not dob:
                reply = "Please send your date of birth. Example: 6 Dec 1994"
            else:
                session.dob = dob
                session.step = "tob"

                if lang == "hi":
                    reply = "Janam ka samay batayein."
                else:
                    reply = "Now tell me your birth time."

        # -------------------------------
        # TIME
        # -------------------------------

        elif session.step == "tob":

            tob = normalize_time(text)

            if not tob:
                reply = "Send time like: 3:45 am or 15:45"
            else:
                session.tob = tob
                session.step = "place"

                if lang == "hi":
                    reply = "Janam ka shehar?"
                else:
                    reply = "Which city were you born in?"

        # -------------------------------
        # PLACE
        # -------------------------------

        elif session.step == "place":

            session.place = text
            session.step = "chat"

            if lang == "hi":
                reply = "Theek hai. Ab aap kya jaana chahte hain?"
            else:
                reply = "Alright. What would you like to know?"

        # -------------------------------
        # MAIN CONVERSATION
        # -------------------------------

        elif session.step == "chat":

            domain = detect_domain(text)

            # fixed coords (replace later with geocoder)
            lat = 28.6139
            lon = 77.2090

            chart = ParashariEngine.generate_chart(
                session.dob,
                session.tob,
                lat,
                lon
            )

            if domain:

                d = chart["domain_scores"][domain]

                header = (
                    f"{domain.capitalize()} Score: {d['score']}/100\n"
                    f"Primary Driver: {d['primary_driver']}\n"
                    f"Risk Factor: {d['risk_factor']}\n"
                    f"Momentum: {d['momentum']}\n\n"
                )

                prompt = AstrologerPrompts.build_deterministic_prompt(
                    domain,
                    d,
                    text,
                    lang
                )

                ai = ask_ai("", prompt)

                reply = header + ai

            else:

                prompt = AstrologerPrompts.build_general_prompt(
                    chart,
                    text,
                    lang
                )

                ai = ask_ai("", prompt)

                reply = ai

        db.commit()
        db.close()

    # =====================================================
    # INTERVIEW BOT
    # =====================================================

    elif bot_token == INTERVIEW_TOKEN:

        reply = ask_ai(
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
        reply = "Invalid bot token"

    # -----------------------------------------------------

    if not reply:
        reply = "Please try again."

    requests.post(
        f"https://api.telegram.org/bot{bot_token}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": reply
        }
    )

    return {"ok": True}