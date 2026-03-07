import json
from datetime import datetime

from app.astro_engine import ParashariEngine
from app.conversation.state_manager import StateManager
from app.conversation.prompt_builder import AstrologerPrompts
from app.conversation.memory_engine import MemoryEngine
from app.conversation.intent_router import IntentRouter
from app.conversation.timing_router import TimingRouter
from app.conversation.consultation_engine import ConsultationEngine
from app.utils.birth_data_parser import BirthDataParser
from app.ai import ask_ai


LANGUAGE_MENU = {
    "keyboard": [
        ["English"],
        ["हिंदी"],
        ["Hindi (Roman)"]
    ],
    "resize_keyboard": True
}


MAIN_MENU_EN = {
    "keyboard": [
        ["🔮 Quick Astrology Question"],
        ["📜 Full Birth Chart Reading"]
    ],
    "resize_keyboard": True
}

MAIN_MENU_DEV = {
    "keyboard": [
        ["🔮 त्वरित ज्योतिष प्रश्न"],
        ["📜 पूर्ण कुंडली विश्लेषण"]
    ],
    "resize_keyboard": True
}

MAIN_MENU_ROM = {
    "keyboard": [
        ["🔮 Turant Jyotish Prashna"],
        ["📜 Poori Kundli Vishleshan"]
    ],
    "resize_keyboard": True
}


DOMAIN_MENU_EN = {
    "keyboard": [
        ["Career", "Finance"],
        ["Marriage", "Health"]
    ],
    "resize_keyboard": True
}

DOMAIN_MENU_DEV = {
    "keyboard": [
        ["करियर", "धन"],
        ["विवाह", "स्वास्थ्य"]
    ],
    "resize_keyboard": True
}

DOMAIN_MENU_ROM = {
    "keyboard": [
        ["Career", "Paisa"],
        ["Shaadi", "Health"]
    ],
    "resize_keyboard": True
}


class DialogEngine:

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

        language = session.language
        script = getattr(session, "script", None)

        # START

        if text == "/start":

            StateManager.update_session(user_id, step="language")

            return {
                "text": "Please select your language\n\nकृपया अपनी भाषा चुनें",
                "keyboard": LANGUAGE_MENU
            }


        # LANGUAGE SELECTION

        if session.step == "language":

            t = text.lower()

            if "english" in t:

                StateManager.update_session(
                    user_id,
                    language="en",
                    script="latin",
                    step="menu"
                )

                return {
                    "text": "Welcome.\n\nHow would you like to begin?",
                    "keyboard": MAIN_MENU_EN
                }


            if "हिंदी" in text:

                StateManager.update_session(
                    user_id,
                    language="hi",
                    script="devanagari",
                    step="menu"
                )

                return {
                    "text": "नमस्ते।\n\nआप कैसे शुरू करना चाहेंगे?",
                    "keyboard": MAIN_MENU_DEV
                }


            if "roman" in t or "hindi" in t:

                StateManager.update_session(
                    user_id,
                    language="hi",
                    script="roman",
                    step="menu"
                )

                return {
                    "text": "Namaste.\n\nAap kaise shuru karna chahenge?",
                    "keyboard": MAIN_MENU_ROM
                }


        # MENU

        if session.step == "menu":

            t = text.lower()

            quick = "quick" in t or "turant" in t or "त्वरित" in text
            full = "chart" in t or "kundli" in t or "कुंडली" in text

            if quick or full:

                StateManager.update_session(user_id, step="birthdata")

                if language == "hi" and script == "devanagari":

                    return (
                        "कृपया अपनी जन्म जानकारी भेजें:\n"
                        "जन्म तिथि\n"
                        "जन्म समय\n"
                        "जन्म स्थान"
                    )


                if language == "hi" and script == "roman":

                    return (
                        "Kripya apni janm jaankari bheje:\n"
                        "Janm tareekh\n"
                        "Janm samay\n"
                        "Janm sthan"
                    )


                return (
                    "Please send your birth details:\n"
                    "Date of birth\n"
                    "Time of birth\n"
                    "Birth place"
                )


        # BIRTH DATA

        if session.step == "birthdata":

            parsed = BirthDataParser.parse_birth_data(text)

            dob = parsed.get("date")
            tob = parsed.get("time")
            place = parsed.get("place")

            if not dob or not tob or not place:

                if language == "hi":

                    return "कृपया पूरी जन्म जानकारी भेजें।"

                return "Please send complete birth details."


            StateManager.update_session(
                user_id,
                dob=dob,
                tob=tob,
                place=place,
                step="question"
            )


            if language == "hi" and script == "devanagari":

                return {
                    "text": "आप किस विषय के बारे में जानना चाहते हैं?",
                    "keyboard": DOMAIN_MENU_DEV
                }


            if language == "hi" and script == "roman":

                return {
                    "text": "Aap kis vishay ke baare mein jaana chahte hain?",
                    "keyboard": DOMAIN_MENU_ROM
                }


            return {
                "text": "What area would you like to explore?",
                "keyboard": DOMAIN_MENU_EN
            }


        # DOMAIN

        if session.step == "question":

            domain = IntentRouter.detect_domain(text)

            chart = DialogEngine.load_chart(user_id, session)

            opening = None

            if not getattr(session, "theme_shown", False):

                opening = ConsultationEngine.build_opening(
                    chart,
                    language,
                    script
                )

                StateManager.update_session(user_id, theme_shown=True)


            domain_data = chart["domain_scores"].get(domain)

            prompt = AstrologerPrompts.build_domain_prompt(
                domain,
                domain_data,
                language,
                user_id,
                text
            )

            ai = ask_ai("", prompt)

            if opening:

                ai = opening + "\n\n" + ai

            MemoryEngine.add_bot_message(user_id, ai)

            return ai


        return "Type /start to begin."