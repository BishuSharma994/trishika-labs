import json

from datetime import datetime

from app.conversation.state_manager import StateManager
from app.conversation.prompt_builder import PromptBuilder
from app.astro_engine import ParashariEngine


class DialogEngine:

    @staticmethod
    def detect_language(text):

        hindi_words = ["kya", "kab", "kaun", "gadi", "ghar", "shaadi", "bhavishya"]

        for word in hindi_words:
            if word in text.lower():
                return "hi"

        return "en"

    @staticmethod
    def detect_domain(text):

        text = text.lower()

        if "career" in text or "job" in text:
            return "career"

        if "marriage" in text or "shaadi" in text:
            return "marriage"

        if "money" in text or "finance" in text or "paisa" in text:
            return "finance"

        if "health" in text:
            return "health"

        return None

    @staticmethod
    def process(user_id, text, session):

        language = session.language or DialogEngine.detect_language(text)

        domain = DialogEngine.detect_domain(text)

        if "hindi" in text.lower():
            StateManager.update_session(user_id, language="hi")
            return "Theek hai. Ab hum Hindi mein baat karenge."

        if text == "/start":

            StateManager.update_session(user_id, step="dob")

            return "Enter your Date of Birth (DD-MM-YYYY)"

        if session.step == "dob":

            StateManager.update_session(user_id, dob=text, step="tob")

            return "Enter your Time of Birth"

        if session.step == "tob":

            StateManager.update_session(user_id, tob=text, step="place")

            return "Enter your Place of Birth"

        if session.step == "place":

            StateManager.update_session(user_id, place=text, step="question")

            return "What would you like to explore first?"

        if session.step == "question":

            lat = 28.6139
            lon = 77.2090

            try:

                dob = datetime.strptime(session.dob, "%d-%m-%Y").strftime("%Y-%m-%d")

                try:
                    time = datetime.strptime(session.tob, "%H:%M").strftime("%H:%M")
                except:
                    time = datetime.strptime(session.tob, "%I:%M %p").strftime("%H:%M")

            except:

                return "Date or time format incorrect. Please restart using /start."

            if not session.chart_data:

                chart = ParashariEngine.generate_chart(dob, time, lat, lon)

                StateManager.update_session(
                    user_id,
                    chart_data=json.dumps(chart)
                )

            else:

                chart = json.loads(session.chart_data)

            domains = chart["domain_scores"]

            if not domain:

                if language == "hi":
                    return "Aap kis cheez ke baare mein jaana chahte hain? Career, paisa, shaadi ya health?"
                else:
                    return "Which area would you like to explore? Career, finance, marriage or health?"

            StateManager.update_session(user_id, last_domain=domain)

            domain_data = domains[domain]

            reply = PromptBuilder.domain_prompt(domain_data, language)

            return reply

        return "Please start with /start."