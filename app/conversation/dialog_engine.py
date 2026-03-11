import json
from datetime import datetime

from app.conversation.domain_router import DomainRouter
from app.conversation.consultation_controller import ConsultationController
from app.astro_engine import ParashariEngine
from app.conversation.consultation_engine import ConsultationEngine
from app.conversation.intent_router import IntentRouter
from app.conversation.language_engine import LanguageEngine
from app.conversation.memory_engine import MemoryEngine
from app.conversation.planet_translator import PlanetTranslator
from app.conversation.profile_manager import ProfileManager
from app.conversation.state_manager import StateManager
from app.conversation.timing_router import TimingRouter
from app.conversation.life_stage_detector import detect as detect_life_stage
from app.utils.age_calculator import calculate_age
from app.utils.birth_data_parser import BirthDataParser
from app.utils.geo_resolver import resolve_coordinates


# -----------------------------------------------------------------------------
# Keyboard / text helpers (language-aware)
# -----------------------------------------------------------------------------

TOPIC_TEXTS = {
    LanguageEngine.ENGLISH:          "Birth details received!\n\nWhat area would you like to explore?",
    LanguageEngine.HINDI_ROMAN:      "Janm details mil gayi!\n\nKis topic ke baare mein jaanna chahte hain?",
    LanguageEngine.HINDI_DEVANAGARI: "\u091c\u0928\u094d\u092e \u0935\u093f\u0935\u0930\u0923 \u092e\u093f\u0932 \u0917\u092f\u093e!\n\n\u0906\u092a \u0915\u093f\u0938 \u0935\u093f\u0937\u092f \u0915\u0947 \u092c\u093e\u0930\u0947 \u092e\u0947\u0902 \u091c\u093e\u0928\u0928\u093e \u091a\u093e\u0939\u0924\u0947 \u0939\u0948\u0902?",
}

TOPIC_KEYBOARDS = {
    LanguageEngine.ENGLISH:          [["Career", "Marriage"], ["Finance", "Health"]],
    LanguageEngine.HINDI_ROMAN:      [["Career", "Shaadi"],   ["Finance", "Health"]],
    LanguageEngine.HINDI_DEVANAGARI: [["\u0915\u0930\u093f\u092f\u0930", "\u0935\u093f\u0935\u093e\u0939"], ["\u0935\u093f\u0924\u094d\u0924", "\u0938\u094d\u0935\u093e\u0938\u094d\u0925\u094d\u092f"]],
}

TOPIC_RETRY_TEXTS = {
    LanguageEngine.ENGLISH:          "Please choose a topic: Career, Marriage, Finance or Health.",
    LanguageEngine.HINDI_ROMAN:      "Ek topic choose karein: Career, Shaadi, Finance ya Health.",
    LanguageEngine.HINDI_DEVANAGARI: "\u0915\u0943\u092a\u092f\u093e \u090f\u0915 \u0935\u093f\u0937\u092f \u091a\u0941\u0928\u0947\u0902: \u0915\u0930\u093f\u092f\u0930, \u0935\u093f\u0935\u093e\u0939, \u0935\u093f\u0924\u094d\u0924 \u092f\u093e \u0938\u094d\u0935\u093e\u0938\u094d\u0925\u094d\u092f\u0964",
}

BIRTHDATA_ERROR_TEXTS = {
    LanguageEngine.ENGLISH:          "Please send your date, time and place of birth.\nExample: 15-08-1990, 10:30 AM, Delhi",
    LanguageEngine.HINDI_ROMAN:      "Please date, time aur jagah bhejiye.\nExample: 15-08-1990, 10:30 AM, Delhi",
    LanguageEngine.HINDI_DEVANAGARI: "\u0915\u0943\u092a\u092f\u093e \u0924\u093e\u0930\u0940\u0916, \u0938\u092e\u092f \u0914\u0930 \u091c\u0917\u0939 \u092d\u0947\u091c\u0947\u0902\u0964\n\u0909\u0926\u093e\u0939\u0930\u0923: 15-08-1990, 10:30 AM, \u0926\u093f\u0932\u094d\u0932\u0940",
}


def _topic_keyboard_response(lang, text_map=None):
    """Return a dict with text + topic selection keyboard."""
    texts = text_map or TOPIC_TEXTS
    return {
        "text": texts.get(lang, texts[LanguageEngine.ENGLISH]),
        "keyboard": {
            "keyboard": TOPIC_KEYBOARDS.get(lang, TOPIC_KEYBOARDS[LanguageEngine.ENGLISH]),
            "resize_keyboard": True,
            "one_time_keyboard": True,
        },
    }


# -----------------------------------------------------------------------------

class DialogEngine:

    # ------------------------------------------------------------------
    @staticmethod
    def load_chart(user_id, session):
        dob   = session.dob
        tob   = session.tob
        place = session.place

        if session.chart_data:
            try:
                return json.loads(session.chart_data)
            except Exception:
                pass

        lat, lon = resolve_coordinates(place)
        chart = ParashariEngine.generate_chart(dob, tob, lat, lon)
        StateManager.update_session(user_id, chart_data=json.dumps(chart))
        return chart

    # ------------------------------------------------------------------
    @staticmethod
    def process(user_id, text, session=None):
        MemoryEngine.add_user_message(user_id, text)
        session = StateManager.get_or_create_session(user_id)

        # Single source of truth for language
        lang   = getattr(session, "language_mode", LanguageEngine.ENGLISH) or LanguageEngine.ENGLISH
        script = getattr(session, "script", None) or "latin"

        # --------------------------------------------------------------
        # /start - reset everything
        # --------------------------------------------------------------
        if text == "/start":
            StateManager.update_session(
                user_id,
                step="language",
                language=None,
                script=None,
                language_mode=None,
                language_confirmed=False,
                language_state_blob=None,
                last_domain=None,
                conversation_phase=ConsultationEngine.DOMAIN_ENTRY,
                consultation_state_blob=None,
                chart_data=None,
            )
            MemoryEngine.clear(user_id)
            return {
                "text": "Please select your language\n\n\u0915\u0943\u092a\u092f\u093e \u0905\u092a\u0928\u0940 \u092d\u093e\u0937\u093e \u091a\u0941\u0928\u0947\u0902",
                "keyboard": {
                    "keyboard": [["English"], ["\u0939\u093f\u0902\u0926\u0940"], ["Hindi (Roman)"]],
                    "resize_keyboard": True,
                    "one_time_keyboard": True,
                },
            }

        # --------------------------------------------------------------
        # LANGUAGE FLOW
        # --------------------------------------------------------------
        language_result = LanguageEngine.handle_language(session, text)
        if language_result:
            update = {}
            if language_result.get("language_mode"):
                update["language_mode"] = language_result["language_mode"]
            if "language_confirmed" in language_result:
                update["language_confirmed"] = language_result["language_confirmed"]
            if language_result.get("state_blob"):
                update["language_state_blob"] = language_result["state_blob"]
            if language_result.get("script"):
                update["script"] = language_result["script"]
            if language_result.get("step"):
                update["step"] = language_result["step"]

            if update:
                StateManager.update_session(user_id, **update)
                for k, v in update.items():
                    setattr(session, k, v)

            if language_result.get("response"):
                reply = language_result["response"]
                bot_text = reply.get("text", "") if isinstance(reply, dict) else reply
                MemoryEngine.add_bot_message(user_id, bot_text)
                return reply

        # --------------------------------------------------------------
        # BIRTH DATA COLLECTION
        # --------------------------------------------------------------
        if session.step == "birthdata":
            parsed = BirthDataParser.parse_birth_data(text)
            dob    = parsed.get("date")
            tob    = parsed.get("time")
            place  = parsed.get("place")

            if not dob or not tob or not place:
                return {
                    "text": BIRTHDATA_ERROR_TEXTS.get(lang, BIRTHDATA_ERROR_TEXTS[LanguageEngine.ENGLISH]),
                    "keyboard": {"remove_keyboard": True},
                }

            age        = calculate_age(dob)
            life_stage = detect_life_stage(age)

            StateManager.update_session(
                user_id,
                dob=dob,
                tob=tob,
                place=place,
                age=age,
                life_stage=life_stage,
                step="question",
                language_confirmed=True,
                consultation_state_blob=None,
            )

            lang = getattr(session, "language_mode", LanguageEngine.ENGLISH) or LanguageEngine.ENGLISH
            response = _topic_keyboard_response(lang)
            MemoryEngine.add_bot_message(user_id, response["text"])
            return response

        # --------------------------------------------------------------
        # MAIN CONSULTATION
        # --------------------------------------------------------------
        if session.step == "question":
            last_domain = getattr(session, "last_domain", None)
            domain      = DomainRouter.detect(text, current_domain=last_domain)

            if not domain and not last_domain:
                response = _topic_keyboard_response(lang, text_map=TOPIC_RETRY_TEXTS)
                MemoryEngine.add_bot_message(user_id, response["text"])
                return response

            if not domain:
                domain = last_domain

            current_stage = (
                getattr(session, "conversation_phase", None)
                or ConsultationEngine.DOMAIN_ENTRY
            )

            chart        = DialogEngine.load_chart(user_id, session)
            score_domain = ConsultationEngine.score_domain(domain) or domain
            domain_data  = dict(chart.get("domain_scores", {}).get(score_domain, {}))
            domain_data["timing_focus"] = bool(TimingRouter.is_timing_question(text))

            current_dasha = chart.get("current_dasha", {})
            transits      = chart.get("transit", {})

            consultation = ConsultationEngine.generate_response(
                domain=domain,
                domain_data=domain_data,
                language=lang,
                script=script,
                stage=current_stage,
                age=getattr(session, "age", None),
                life_stage=getattr(session, "life_stage", None),
                user_goal=None,
                current_dasha=current_dasha,
                transits=transits,
                persona_introduced=False,
                chart=chart,
                theme_shown=False,
                user_text=text,
                session_state_blob=getattr(session, "consultation_state_blob", None),
                domain_switched=False,
            )

            reply = consultation.get("text", "")
            reply = PlanetTranslator.translate(reply, lang, script)
            reply = LanguageEngine.enforce_response_language(session, reply)

            next_stage = ConsultationController.next_stage(current_stage)

            StateManager.update_session(
                user_id,
                last_domain=domain,
                conversation_phase=next_stage,
                consultation_state_blob=consultation.get("state_blob"),
            )

            MemoryEngine.add_bot_message(user_id, reply)

            return {
                "text": reply,
                "keyboard": {"remove_keyboard": True},
            }

        # --------------------------------------------------------------
        # FALLBACK
        # --------------------------------------------------------------
        return {
            "text": "Type /start to begin.",
            "keyboard": {"remove_keyboard": True},
        }
