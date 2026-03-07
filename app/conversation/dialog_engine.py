import json
from datetime import datetime

from app.astro_engine import ParashariEngine
from app.conversation.state_manager import StateManager
from app.conversation.prompt_builder import AstrologerPrompts
from app.conversation.memory_engine import MemoryEngine
from app.utils.birth_data_parser import BirthDataParser
from app.ai import ask_ai


MAIN_MENU = {
    "keyboard": [
        ["🔮 Quick Astrology Question"],
        ["📜 Full Birth Chart Reading"]
    ],
    "resize_keyboard": True
}

DOMAIN_MENU = {
    "keyboard": [
        ["Career", "Finance"],
        ["Marriage", "Health"]
    ],
    "resize_keyboard": True
}


class DialogEngine:

    @staticmethod
    def detect_language(text):

        hindi_words = [
            "kya", "kab", "bhavishya",
            "shaadi", "paisa", "naukri"
        ]

        for word in hindi_words:
            if word in text.lower():
                return "hi"

        return "en"

    @staticmethod
    def detect_domain(text):

        t = text.lower()

        if "career" in t or "job" in t:
            return "career"

        if "finance" in t or "money" in t:
            return "finance"

        if "marriage" in t or "relationship" in t:
            return "marriage"

        if "health" in t:
            return "health"

        return None

    @staticmethod
    def normalize_birth_data(session):

        dob = datetime.strptime(session.dob, "%Y-%m-%d").strftime("%Y-%m-%d")

        return dob, session.tob

    @staticmethod
    def load_chart(user_id, session):

        lat = 28.6139
        lon = 77.2090

        if session.chart_data:

            try:
                return json.loads(session.chart_data)
            except:
                pass

        dob, time = DialogEngine.normalize_birth_data(session)

        chart = ParashariEngine.generate_chart(
            dob,
            time,
            lat,
            lon
        )

        StateManager.update_session(
            user_id,
            chart_data=json.dumps(chart)
        )

        return chart

    @staticmethod
    def process(user_id, text, session):

        MemoryEngine.add_user_message(user_id, text)

        language = session.language or DialogEngine.detect_language(text)

        # --------------------------------------------------
        # START
        # --------------------------------------------------

        if text == "/start":

            StateManager.update_session(user_id, step="menu")

            return {
                "text": "Welcome.\n\nI read birth charts using Vedic astrology and can answer questions about career, relationships, finances and life timing.\n\nChoose how you would like to begin.",
                "keyboard": MAIN_MENU
            }

        # --------------------------------------------------
        # MENU SELECTION
        # --------------------------------------------------

        if session.step == "menu":

            if "quick" in text.lower():

                StateManager.update_session(user_id, step="birthdata_quick")

                return (
                    "Alright.\n\n"
                    "To answer your question I first need your birth details.\n\n"
                    "Please send:\n"
                    "Date of birth\n"
                    "Time of birth\n"
                    "Birth place (city)\n\n"
                    "Example:\n"
                    "6 Dec 1994 3:45 AM Delhi"
                )

            if "birth chart" in text.lower():

                StateManager.update_session(user_id, step="birthdata_full")

                return (
                    "Good.\n\n"
                    "For a full birth chart reading I need your birth details.\n\n"
                    "Please send:\n"
                    "Date of birth\n"
                    "Time of birth\n"
                    "Birth place (city)\n\n"
                    "Example:\n"
                    "6 Dec 1994 3:45 AM Delhi"
                )

        # --------------------------------------------------
        # BIRTH DATA COLLECTION (QUICK / FULL)
        # --------------------------------------------------

        if session.step in ["birthdata_quick", "birthdata_full"]:

            parsed = BirthDataParser.parse_birth_data(text)

            dob = parsed.get("date")
            tob = parsed.get("time")
            place = parsed.get("place")

            if not dob or not tob or not place:

                return (
                    "I could not detect complete birth details.\n\n"
                    "Please send:\n"
                    "Date of birth\n"
                    "Time of birth\n"
                    "Birth place\n\n"
                    "Example:\n"
                    "6 Dec 1994 3:45 AM Delhi"
                )

            StateManager.update_session(
                user_id,
                dob=dob,
                tob=tob,
                place=place,
                step="question"
            )

            return {
                "text": "Your birth details are received.\n\nWhat area would you like to explore?",
                "keyboard": DOMAIN_MENU
            }

        # --------------------------------------------------
        # DOMAIN ANALYSIS
        # --------------------------------------------------

        if session.step == "question":

            domain = DialogEngine.detect_domain(text)

            if not domain:

                return {
                    "text": "Choose a topic.",
                    "keyboard": DOMAIN_MENU
                }

            chart = DialogEngine.load_chart(user_id, session)

            domain_data = chart["domain_scores"].get(domain)

            prompt = AstrologerPrompts.build_domain_prompt(
                domain,
                domain_data,
                language,
                user_id,
                text
            )

            reply = ask_ai("", prompt)

            MemoryEngine.add_bot_message(user_id, reply)

            return reply

        return "Type /start to begin."