import json
from datetime import datetime

from app.astro_engine import ParashariEngine
from app.conversation.state_manager import StateManager
from app.conversation.prompt_builder import AstrologerPrompts
from app.conversation.memory_engine import MemoryEngine
from app.conversation.intent_router import IntentRouter
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
    def detect_language_and_script(text):

        # Detect Devanagari Hindi
        for c in text:
            if '\u0900' <= c <= '\u097F':
                return "hi", "devanagari"

        # Detect Roman Hindi
        roman_hindi_words = [
            "hindi", "shaadi", "naukri", "paisa",
            "bhavishya", "mera", "meri", "mujhe",
            "kya", "kab", "kaise", "kyun",
            "baat kijiye", "hindi me", "hindi mein"
        ]

        t = text.lower()

        for w in roman_hindi_words:
            if w in t:
                return "hi", "roman"

        return "en", "latin"

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

        language, script = DialogEngine.detect_language_and_script(text)

        if session.language != language or getattr(session, "script", None) != script:
            StateManager.update_session(user_id, language=language, script=script)

        language = session.language or language
        script = getattr(session, "script", script)

        # --------------------------------------------------
        # START
        # --------------------------------------------------

        if text == "/start":

            StateManager.update_session(user_id, step="menu")

            if language == "hi" and script == "devanagari":
                return {
                    "text": "नमस्ते।\n\nमैं वैदिक ज्योतिष के आधार पर आपकी जन्म कुंडली पढ़कर करियर, विवाह, धन और जीवन के महत्वपूर्ण समय के बारे में बता सकता हूँ।\n\nआप कैसे शुरू करना चाहेंगे?",
                    "keyboard": MAIN_MENU
                }

            if language == "hi" and script == "roman":
                return {
                    "text": "Namaste.\n\nMain Vedic astrology ke aadhaar par aapki kundli dekhkar career, shaadi, paisa aur life timing ke baare mein bata sakta hoon.\n\nAap kaise shuru karna chahenge?",
                    "keyboard": MAIN_MENU
                }

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

                if language == "hi" and script == "devanagari":
                    return (
                        "ठीक है।\n\n"
                        "आपका प्रश्न देखने के लिए मुझे आपकी जन्म जानकारी चाहिए।\n\n"
                        "कृपया भेजें:\n"
                        "जन्म तिथि\n"
                        "जन्म समय\n"
                        "जन्म स्थान (शहर)\n\n"
                        "उदाहरण:\n"
                        "6 Dec 1994 3:45 AM Delhi"
                    )

                if language == "hi" and script == "roman":
                    return (
                        "Theek hai.\n\n"
                        "Aapka prashna dekhne ke liye mujhe aapki birth details chahiye.\n\n"
                        "Please bheje:\n"
                        "Date of birth\n"
                        "Birth time\n"
                        "Birth place (city)\n\n"
                        "Example:\n"
                        "6 Dec 1994 3:45 AM Delhi"
                    )

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

                if language == "hi" and script == "devanagari":
                    return (
                        "अच्छा।\n\n"
                        "पूर्ण कुंडली पढ़ने के लिए मुझे आपकी जन्म जानकारी चाहिए।\n\n"
                        "कृपया भेजें:\n"
                        "जन्म तिथि\n"
                        "जन्म समय\n"
                        "जन्म स्थान (शहर)\n\n"
                        "उदाहरण:\n"
                        "6 Dec 1994 3:45 AM Delhi"
                    )

                if language == "hi" and script == "roman":
                    return (
                        "Achha.\n\n"
                        "Full kundli reading ke liye mujhe aapki birth details chahiye.\n\n"
                        "Please bheje:\n"
                        "Date of birth\n"
                        "Birth time\n"
                        "Birth place\n\n"
                        "Example:\n"
                        "6 Dec 1994 3:45 AM Delhi"
                    )

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
        # BIRTH DATA COLLECTION
        # --------------------------------------------------

        if session.step in ["birthdata_quick", "birthdata_full"]:

            parsed = BirthDataParser.parse_birth_data(text)

            dob = parsed.get("date")
            tob = parsed.get("time")
            place = parsed.get("place")

            if not dob or not tob or not place:

                if language == "hi":
                    return (
                        "मुझे पूरी जन्म जानकारी नहीं मिली।\n\n"
                        "कृपया भेजें:\n"
                        "जन्म तिथि\n"
                        "जन्म समय\n"
                        "जन्म स्थान"
                    )

                return (
                    "I could not detect complete birth details.\n\n"
                    "Please send:\n"
                    "Date of birth\n"
                    "Time of birth\n"
                    "Birth place"
                )

            StateManager.update_session(
                user_id,
                dob=dob,
                tob=tob,
                place=place,
                step="question"
            )

            if language == "hi" and script == "devanagari":
                return {
                    "text": "आपकी जन्म जानकारी मिल गई है।\n\nआप किस विषय के बारे में जानना चाहते हैं?",
                    "keyboard": DOMAIN_MENU
                }

            if language == "hi" and script == "roman":
                return {
                    "text": "Aapki birth details mil gayi hain.\n\nAap kis topic ke baare mein jaana chahte hain?",
                    "keyboard": DOMAIN_MENU
                }

            return {
                "text": "Your birth details are received.\n\nWhat area would you like to explore?",
                "keyboard": DOMAIN_MENU
            }

        # --------------------------------------------------
        # DOMAIN ANALYSIS
        # --------------------------------------------------

        if session.step == "question":

            domain = IntentRouter.detect_domain(text)

            if not domain:

                if language == "hi":
                    return {
                        "text": "कृपया कोई विषय चुनें या अपना प्रश्न पूछें।",
                        "keyboard": DOMAIN_MENU
                    }

                return {
                    "text": "Choose a topic or ask your question.",
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