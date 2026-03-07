import json
from datetime import datetime

from app.astro_engine import ParashariEngine
from app.conversation.state_manager import StateManager
from app.conversation.prompt_builder import PromptBuilder
from app.ai import ask_ai


class DialogEngine:

    # ----------------------------------------------------
    # LANGUAGE DETECTION
    # ----------------------------------------------------

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

    # ----------------------------------------------------
    # DOMAIN DETECTION
    # ----------------------------------------------------

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

        if "vehicle" in t or "car" in t or "gadi" in t:
            return "vehicle"

        if "property" in t or "ghar" in t or "house" in t:
            return "property"

        return None

    # ----------------------------------------------------
    # INTENT DETECTION
    # ----------------------------------------------------

    @staticmethod
    def detect_intent(text):

        t = text.lower()

        if "future" in t or "bhavishya" in t:
            return "future"

        if "decision" in t or "kya karu" in t:
            return "decision"

        if "when" in t or "kab" in t:
            return "timing"

        if "next year" in t or "projection" in t:
            return "projection"

        return "general"

    # ----------------------------------------------------
    # NORMALIZE DOB + TIME
    # ----------------------------------------------------

    @staticmethod
    def normalize_birth_data(session):

        dob = datetime.strptime(session.dob, "%d-%m-%Y").strftime("%Y-%m-%d")

        try:
            time = datetime.strptime(session.tob, "%H:%M").strftime("%H:%M")
        except:
            time = datetime.strptime(session.tob, "%I:%M %p").strftime("%H:%M")

        return dob, time

    # ----------------------------------------------------
    # LOAD OR GENERATE CHART
    # ----------------------------------------------------

    @staticmethod
    def load_chart(user_id, session):

        lat = 28.6139
        lon = 77.2090

        if not session.chart_data:

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

        return json.loads(session.chart_data)

    # ----------------------------------------------------
    # DOMAIN RESPONSE
    # ----------------------------------------------------

    @staticmethod
    def domain_response(domain, domain_data, language):

        prompt = PromptBuilder.build_domain_prompt(
            domain,
            domain_data,
            language
        )

        try:
            reply = ask_ai("", prompt)

            if reply and len(reply.strip()) > 10:
                return reply

        except Exception:
            pass

        # fallback deterministic

        driver = domain_data["primary_driver"]
        risk = domain_data["risk_factor"]
        momentum = domain_data["momentum"]

        if language == "hi":

            return (
                f"Aapke {domain} par iss samay {driver} ka prabhav hai.\n"
                f"Momentum {momentum} hai aur {risk} kuch challenges la sakta hai.\n"
                "Aap kis decision ke baare mein soch rahe hain?"
            )

        else:

            return (
                f"Your {domain} is currently influenced by {driver}.\n"
                f"The momentum is {momentum}, while {risk} may create some challenges.\n"
                "Are you considering any specific decision?"
            )

    # ----------------------------------------------------
    # DECISION RESPONSE
    # ----------------------------------------------------

    @staticmethod
    def decision_response(domain, domain_data, language):

        prompt = PromptBuilder.build_decision_prompt(
            domain,
            domain_data,
            language
        )

        try:
            reply = ask_ai("", prompt)

            if reply and len(reply.strip()) > 10:
                return reply

        except Exception:
            pass

        if language == "hi":

            return (
                f"{domain} se jude decisions jaise job change, promotion "
                "ya financial commitments aa sakte hain.\n"
                "Decision lene se pehle stability evaluate karna zaroori hai."
            )

        else:

            return (
                f"Decisions related to {domain} such as job change, "
                "promotion or financial commitments may arise.\n"
                "Evaluate stability before acting."
            )

    # ----------------------------------------------------
    # FUTURE RESPONSE
    # ----------------------------------------------------

    @staticmethod
    def future_response(domain, domain_data, language):

        prompt = PromptBuilder.build_future_prompt(
            domain,
            domain_data,
            language
        )

        try:
            reply = ask_ai("", prompt)

            if reply and len(reply.strip()) > 10:
                return reply

        except Exception:
            pass

        if language == "hi":

            return (
                f"Agle kuch samay mein {domain} mein dheere dheere parivartan dekhne ko mil sakte hain.\n"
                "Stability maintain karna important rahega."
            )

        else:

            return (
                f"The coming period may bring gradual changes in your {domain}.\n"
                "Maintaining stability will be important."
            )

    # ----------------------------------------------------
    # MAIN PROCESSOR
    # ----------------------------------------------------

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

        # ----------------------------------------------------
        # DOMAIN MEMORY FIX
        # ----------------------------------------------------

        if not domain and session.last_domain:
            domain = session.last_domain

        # ----------------------------------------------------
        # START FLOW
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # CONVERSATION MODE
        # ----------------------------------------------------

        if session.step == "question":

            chart = DialogEngine.load_chart(user_id, session)

            domains = chart["domain_scores"]

            if not domain:

                if language == "hi":
                    return "Aap kis shetra ke baare mein jaana chahte hain? Career, paisa, shaadi ya health?"
                else:
                    return "Which area would you like to explore? Career, finance, marriage or health?"

            StateManager.update_session(user_id, last_domain=domain)

            domain_data = domains.get(domain)

            # intent routing

            if intent == "decision":
                return DialogEngine.decision_response(domain, domain_data, language)

            if intent in ["future", "projection"]:
                return DialogEngine.future_response(domain, domain_data, language)

            return DialogEngine.domain_response(domain, domain_data, language)

        return "Please start with /start."