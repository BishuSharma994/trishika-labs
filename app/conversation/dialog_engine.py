import json
from datetime import datetime

from app.astro_engine import ParashariEngine
from app.conversation.state_manager import StateManager
from app.conversation.prompt_builder import AstrologerPrompts
from app.conversation.memory_engine import MemoryEngine
from app.conversation.intent_router import IntentRouter
from app.conversation.timing_router import TimingRouter
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

        # --------------------------------------------------
        # START
        # --------------------------------------------------

        if text == "/start":

            StateManager.update_session(user_id, step="language")

            return {
                "text": "Please select your language\n\nकृपया अपनी भाषा चुनें",
                "keyboard": LANGUAGE_MENU
            }

        # --------------------------------------------------
        # LANGUAGE SELECTION
        # --------------------------------------------------

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

            return {
                "text": "Please choose a language / कृपया भाषा चुनें",
                "keyboard": LANGUAGE_MENU
            }

        # --------------------------------------------------
        # MENU SELECTION
        # --------------------------------------------------

        if session.step == "menu":

            t = text.lower()

            if "quick" in t or "turant" in t or "त्वरित" in text:

                StateManager.update_session(user_id, step="birthdata")

                if language == "hi" and script == "devanagari":
                    return "कृपया अपनी जन्म जानकारी भेजें:\nजन्म तिथि\nजन्म समय\nजन्म स्थान"

                if language == "hi" and script == "roman":
                    return "Kripya apni birth details bheje:\nJanm tareekh\nJanm samay\nJanm sthan"

                return "Please send your birth details:\nDate of birth\nTime of birth\nBirth place"

            if "chart" in t or "kundli" in t or "कुंडली" in text:

                StateManager.update_session(user_id, step="birthdata")

                if language == "hi" and script == "devanagari":
                    return "पूर्ण कुंडली पढ़ने के लिए अपनी जन्म जानकारी भेजें।"

                if language == "hi" and script == "roman":
                    return "Poori kundli ke liye apni birth details bheje."

                return "Send your birth details for full chart reading."

        # --------------------------------------------------
        # BIRTH DATA COLLECTION
        # --------------------------------------------------

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

        # --------------------------------------------------
        # DOMAIN ANALYSIS + TIMING DETECTION
        # --------------------------------------------------

        if session.step == "question":

            domain = IntentRouter.detect_domain(text)

            if not domain:

                if language == "hi":
                    return {
                        "text": "कृपया कोई विषय चुनें या अपना प्रश्न पूछें।",
                        "keyboard": DOMAIN_MENU_DEV
                    }

                return {
                    "text": "Choose a topic or ask your question.",
                    "keyboard": DOMAIN_MENU_EN
                }

            chart = DialogEngine.load_chart(user_id, session)

            domain_data = chart["domain_scores"].get(domain)

            is_timing = TimingRouter.is_timing_question(text)

            if is_timing:
                domain_data["timing_focus"] = True
            else:
                domain_data["timing_focus"] = False

            prompt = AstrologerPrompts.build_domain_prompt(
                domain,
                domain_data,
                language,
                script,
                user_id,
                text
            )

            reply = ask_ai("", prompt)

            MemoryEngine.add_bot_message(user_id, reply)

            return reply

        return "Type /start to begin."