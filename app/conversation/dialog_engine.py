import json
from datetime import datetime
from dateutil import parser

from app.astro_engine import ParashariEngine
from app.conversation.state_manager import StateManager
from app.conversation.prompt_builder import PromptBuilder
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

    # --------------------------------------------------
    # LANGUAGE DETECTION
    # --------------------------------------------------

    @staticmethod
    def detect_language(text):

        hindi_words = [
            "kya", "kab", "kaun", "kaunsi",
            "bhavishya", "gadi", "ghar",
            "shaadi", "paisa", "naukri"
        ]

        for word in hindi_words:
            if word in text.lower():
                return "hi"

        return "en"

    # --------------------------------------------------
    # DOMAIN DETECTION
    # --------------------------------------------------

    @staticmethod
    def detect_domain(text):

        t = text.lower()

        if "career" in t or "job" in t or "promotion" in t:
            return "career"

        if "finance" in t or "money" in t or "income" in t or "paisa" in t:
            return "finance"

        if "marriage" in t or "relationship" in t or "shaadi" in t:
            return "marriage"

        if "health" in t:
            return "health"

        return None

    # --------------------------------------------------
    # INTENT DETECTION
    # --------------------------------------------------

    @staticmethod
    def detect_intent(text):

        t = text.lower()

        if "future" in t or "bhavishya" in t:
            return "future"

        if "decision" in t or "kya karu" in t:
            return "decision"

        if "when" in t or "kab" in t:
            return "timing"

        return "general"

    # --------------------------------------------------
    # DOB PARSER
    # --------------------------------------------------

    @staticmethod
    def parse_dob(text):

        try:
            dt = parser.parse(text, dayfirst=True)
            return dt.strftime("%d-%m-%Y")
        except:
            return None

    # --------------------------------------------------
    # TIME PARSER
    # --------------------------------------------------

    @staticmethod
    def parse_time(text):

        try:
            dt = parser.parse(text)
            return dt.strftime("%H:%M")
        except:
            return None

    # --------------------------------------------------
    # NORMALIZE BIRTH DATA
    # --------------------------------------------------

    @staticmethod
    def normalize_birth_data(session):

        dob = datetime.strptime(session.dob, "%d-%m-%Y").strftime("%Y-%m-%d")
        time = session.tob

        return dob, time

    # --------------------------------------------------
    # LOAD OR GENERATE CHART
    # --------------------------------------------------

    @staticmethod
    def load_chart(user_id, session):

        lat = 28.6139
        lon = 77.2090

        # chart already stored
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

    # --------------------------------------------------
    # DOMAIN RESPONSE
    # --------------------------------------------------

    @staticmethod
    def domain_response(domain, domain_data, language):

        if not domain_data:
            return "I need a little more information before answering that."

        prompt = PromptBuilder.build_domain_prompt(
            domain,
            domain_data,
            language
        )

        try:

            reply = ask_ai("", prompt)

            if reply and len(reply.strip()) > 10:
                return reply

        except:
            pass

        # deterministic fallback

        driver = domain_data.get("primary_driver", "planetary influences")
        risk = domain_data.get("risk_factor", "some factors")

        if language == "hi":
            return f"Aapke {domain} par {driver} ka prabhav hai. {risk} kuch challenges la sakta hai."

        return f"Your {domain} is influenced by {driver}. {risk} may introduce challenges."

    # --------------------------------------------------
    # MAIN PROCESSOR
    # --------------------------------------------------

    @staticmethod
    def process(user_id, text, session):

        text_lower = text.lower()

        # language override

        if "hindi" in text_lower:

            StateManager.update_session(user_id, language="hi")

            return "Theek hai. Ab hum Hindi mein baat karenge."

        if "english" in text_lower:

            StateManager.update_session(user_id, language="en")

            return "Sure. We will continue in English."

        language = session.language or DialogEngine.detect_language(text)

        domain = DialogEngine.detect_domain(text)
        intent = DialogEngine.detect_intent(text)

        # --------------------------------------------------
        # DOMAIN MEMORY
        # --------------------------------------------------

        if not domain and session.last_domain:
            domain = session.last_domain

        # --------------------------------------------------
        # START FLOW
        # --------------------------------------------------

        if text == "/start":

            if session.dob and session.tob and session.place:

                return {
                    "text": "Welcome back. What would you like to explore?",
                    "keyboard": MAIN_OPTIONS
                }

            StateManager.update_session(user_id, step="dob")

            return "Enter your Date of Birth (example: 12-06-1994)"

        # --------------------------------------------------
        # DOB STEP
        # --------------------------------------------------

        if session.step == "dob":

            dob = DialogEngine.parse_dob(text)

            if not dob:
                return "Please enter date like 12-06-1994 or 12/06/1994."

            StateManager.update_session(
                user_id,
                dob=dob,
                step="tob"
            )

            return "Enter your Time of Birth (example: 3:45 am)"

        # --------------------------------------------------
        # TIME STEP
        # --------------------------------------------------

        if session.step == "tob":

            time = DialogEngine.parse_time(text)

            if not time:
                return "Please enter time like 3:45 am or 15:45."

            StateManager.update_session(
                user_id,
                tob=time,
                step="place"
            )

            return "Enter your Place of Birth"

        # --------------------------------------------------
        # PLACE STEP
        # --------------------------------------------------

        if session.step == "place":

            StateManager.update_session(
                user_id,
                place=text,
                step="question"
            )

            return {
                "text": "What would you like to explore first?",
                "keyboard": MAIN_OPTIONS
            }

        # --------------------------------------------------
        # CONVERSATION MODE
        # --------------------------------------------------

        if session.step == "question":

            chart = DialogEngine.load_chart(user_id, session)

            domains = chart.get("domain_scores", {})

            if not domain:

                return {
                    "text": "Choose a topic to explore.",
                    "keyboard": MAIN_OPTIONS
                }

            StateManager.update_session(user_id, last_domain=domain)

            domain_data = domains.get(domain)

            reply = DialogEngine.domain_response(
                domain,
                domain_data,
                language
            )

            return {
                "text": reply,
                "keyboard": MAIN_OPTIONS
            }

        return "Please start with /start."