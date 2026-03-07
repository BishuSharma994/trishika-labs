import json
from datetime import datetime
from dateutil import parser

from app.astro_engine import ParashariEngine
from app.conversation.state_manager import StateManager
from app.conversation.prompt_builder import PromptBuilder
from app.conversation.memory_engine import MemoryEngine
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
    def parse_dob(text):

        try:
            dt = parser.parse(text, dayfirst=True)
            return dt.strftime("%d-%m-%Y")
        except:
            return None

    @staticmethod
    def parse_time(text):

        try:
            dt = parser.parse(text)
            return dt.strftime("%H:%M")
        except:
            return None

    @staticmethod
    def normalize_birth_data(session):

        dob = datetime.strptime(session.dob, "%d-%m-%Y").strftime("%Y-%m-%d")

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
                "text": "Welcome. How would you like to explore astrology today?",
                "keyboard": MAIN_MENU
            }

        # --------------------------------------------------
        # MENU SELECTION
        # --------------------------------------------------

        if session.step == "menu":

            if "quick" in text.lower():

                StateManager.update_session(user_id, step="quick")

                return "Ask any astrology question."

            if "birth chart" in text.lower():

                StateManager.update_session(user_id, step="dob")

                return "Please send your date of birth. Example: 6 Dec 1994"

        # --------------------------------------------------
        # QUICK QUESTION MODE
        # --------------------------------------------------

        if session.step == "quick":

            prompt = PromptBuilder.build_general_prompt(
                {},
                text,
                language,
                user_id
            )

            reply = ask_ai("", prompt)

            MemoryEngine.add_bot_message(user_id, reply)

            return reply

        # --------------------------------------------------
        # DOB STEP
        # --------------------------------------------------

        if session.step == "dob":

            dob = DialogEngine.parse_dob(text)

            if not dob:
                return "Please send your date of birth. Example: 6 Dec 1994"

            StateManager.update_session(user_id, dob=dob, step="tob")

            return "Now tell me your birth time."

        # --------------------------------------------------
        # TIME STEP
        # --------------------------------------------------

        if session.step == "tob":

            time = DialogEngine.parse_time(text)

            if not time:
                return "Please send time like 3:45 am"

            StateManager.update_session(user_id, tob=time, step="place")

            return "Which city were you born in?"

        # --------------------------------------------------
        # PLACE STEP
        # --------------------------------------------------

        if session.step == "place":

            StateManager.update_session(user_id, place=text, step="question")

            return {
                "text": "What area would you like to explore?",
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

            prompt = PromptBuilder.build_domain_prompt(
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