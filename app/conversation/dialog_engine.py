import json
from datetime import datetime
from dateutil import parser

from app.astro_engine import ParashariEngine
from app.conversation.state_manager import StateManager
from app.conversation.prompt_builder import PromptBuilder
from app.conversation.memory_engine import MemoryEngine
from app.ai import ask_ai


MAIN_OPTIONS = {
    "keyboard": [
        ["Career", "Finance"],
        ["Marriage", "Health"],
        ["Future outlook"]
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

        if "marriage" in t or "relationship" in t or "shaadi" in t:
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
        time = session.tob

        return dob, time

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
    def domain_response(user_id, domain, domain_data, language, question):

        prompt = PromptBuilder.build_domain_prompt(
            domain,
            domain_data,
            language,
            user_id,
            question
        )

        try:

            reply = ask_ai("", prompt)

            if reply and len(reply.strip()) > 10:
                return reply

        except:
            pass

        driver = domain_data.get("primary_driver")
        risk = domain_data.get("risk_factor")

        if language == "hi":
            return f"Aapke {domain} par {driver} ka prabhav hai. {risk} kuch challenges la sakta hai."

        return f"Your {domain} is influenced by {driver}. {risk} may introduce challenges."

    @staticmethod
    def process(user_id, text, session):

        MemoryEngine.add_user_message(user_id, text)

        language = session.language or DialogEngine.detect_language(text)

        domain = DialogEngine.detect_domain(text)

        if text == "/start":

            StateManager.update_session(user_id, step="dob")

            reply = "Enter your Date of Birth (example: 12-06-1994)"

            MemoryEngine.add_bot_message(user_id, reply)

            return reply

        if session.step == "dob":

            dob = DialogEngine.parse_dob(text)

            if not dob:
                return "Please enter date like 12-06-1994."

            StateManager.update_session(user_id, dob=dob, step="tob")

            reply = "Enter your Time of Birth"

            MemoryEngine.add_bot_message(user_id, reply)

            return reply

        if session.step == "tob":

            time = DialogEngine.parse_time(text)

            if not time:
                return "Enter time like 3:45 am or 15:45."

            StateManager.update_session(user_id, tob=time, step="place")

            reply = "Enter your Place of Birth"

            MemoryEngine.add_bot_message(user_id, reply)

            return reply

        if session.step == "place":

            StateManager.update_session(user_id, place=text, step="question")

            reply = {
                "text": "What would you like to explore?",
                "keyboard": MAIN_OPTIONS
            }

            return reply

        if session.step == "question":

            chart = DialogEngine.load_chart(user_id, session)

            domains = chart.get("domain_scores")

            if not domain:

                return {
                    "text": "Choose a topic",
                    "keyboard": MAIN_OPTIONS
                }

            domain_data = domains.get(domain)

            reply = DialogEngine.domain_response(
                user_id,
                domain,
                domain_data,
                language,
                text
            )

            MemoryEngine.add_bot_message(user_id, reply)

            return {
                "text": reply,
                "keyboard": MAIN_OPTIONS
            }

        return "Type /start to begin."