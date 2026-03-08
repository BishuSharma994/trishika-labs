import json
from datetime import datetime

from app.astro_engine import ParashariEngine
from app.conversation.state_manager import StateManager
from app.conversation.prompt_builder import AstrologerPrompts
from app.conversation.memory_engine import MemoryEngine
from app.conversation.intent_router import IntentRouter
from app.conversation.timing_router import TimingRouter
from app.conversation.followup_router import FollowupRouter
from app.conversation.consultation_engine import ConsultationEngine
from app.conversation.planet_translator import PlanetTranslator
from app.conversation.astrology_response_template import AstrologyResponseTemplate
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
            except Exception:
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

        # Always process with a fresh DB snapshot to avoid stale ORM objects.
        session = StateManager.get_or_create_session(user_id)
        language = session.language or "en"
        script = getattr(session, "script", None) or "latin"

        if text == "/start":
            StateManager.update_session(
                user_id,
                step="language",
                language=None,
                script=None
            )

            return {
                "text": "Please select your language\n\nकृपया अपनी भाषा चुनें",
                "keyboard": LANGUAGE_MENU
            }

        if session.step == "language":
            t = text.lower()

            if "roman" in t:
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

            if "hindi" in t:
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

        if session.step == "menu":
            t = text.lower()

            quick_selected = (
                "quick" in t
                or "turant" in t
                or "त्वरित" in text
            )

            full_selected = (
                "chart" in t
                or "kundli" in t
                or "कुंडली" in text
                or "vishleshan" in t
            )

            if quick_selected:
                StateManager.update_session(user_id, step="birthdata")

                if language == "hi" and script == "devanagari":
                    return "कृपया अपनी जन्म जानकारी भेजें।"

                if language == "hi" and script == "roman":
                    return "Kripya apni janm jaankari bheje."

                return "Please send your birth details."

            if full_selected:
                StateManager.update_session(user_id, step="birthdata")

                if language == "hi" and script == "devanagari":
                    return "कृपया अपनी जन्म जानकारी भेजें।"

                if language == "hi" and script == "roman":
                    return "Kripya apni janm jaankari bheje."

                return "Please send your birth details."

        if session.step == "birthdata":
            parsed = BirthDataParser.parse_birth_data(text)

            dob = parsed.get("date")
            tob = parsed.get("time")
            place = parsed.get("place")

            if not dob or not tob or not place:
                if language == "hi" and script == "roman":
                    return "Kripya apni janm jaankari bheje."

                if language == "hi":
                    return "कृपया अपनी जन्म जानकारी भेजें।"

                return "Please send your birth details."

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

        if session.step == "question":
            domain = IntentRouter.detect_domain(text)

            if not domain:
                last_domain = getattr(session, "last_domain", None)
                is_followup = FollowupRouter.is_followup(text)

                if last_domain and is_followup:
                    domain = last_domain
                else:
                    if language == "hi" and script == "roman":
                        return {
                            "text": "Kripya koi vishay chune ya apna prashna puchhe.",
                            "keyboard": DOMAIN_MENU_ROM
                        }

                    if language == "hi":
                        return {
                            "text": "कृपया कोई विषय चुनें या अपना प्रश्न पूछें।",
                            "keyboard": DOMAIN_MENU_DEV
                        }

                    return {
                        "text": "Choose a topic or ask your question.",
                        "keyboard": DOMAIN_MENU_EN
                    }

            StateManager.update_session(user_id, last_domain=domain)

            chart = DialogEngine.load_chart(user_id, session)

            if not getattr(session, "theme_shown", False):
                opening = ConsultationEngine.build_opening(chart, language, script)
                StateManager.update_session(user_id, theme_shown=True)
            else:
                opening = None

            domain_data = chart.get("domain_scores", {}).get(domain, {})
            domain_data["timing_focus"] = bool(TimingRouter.is_timing_question(text))

            prompt = AstrologerPrompts.build_domain_prompt(
                domain,
                domain_data,
                language,
                script,
                user_id,
                text
            )

            try:
                ai_output = ask_ai("", prompt)
            except Exception:
                if language == "hi" and script == "roman":
                    return "Server se connection issue aa raha hai. Kripya thodi der baad phir se puchhe."

                if language == "hi":
                    return "इस समय सर्वर से कनेक्शन में समस्या है। कृपया थोड़ी देर बाद फिर से पूछें।"

                return "I'm facing a temporary server connection issue. Please try again in a moment."

            formatted_reply = AstrologyResponseTemplate.build_response(
                domain=domain,
                domain_data=domain_data,
                ai_guidance=ai_output,
                language=language,
                script=script
            )

            # Apply localization after AI output and deterministic formatting.
            reply = PlanetTranslator.translate(
                formatted_reply,
                language,
                script
            )

            if opening:
                opening = PlanetTranslator.translate(opening, language, script)
                reply = f"{opening}\n\n{reply}"

            MemoryEngine.add_bot_message(user_id, reply)

            return reply

        return "Type /start to begin."
