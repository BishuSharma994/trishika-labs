import json

from app.astro_engine import ParashariEngine
from app.conversation.consultation_engine import ConsultationEngine
from app.conversation.intent_router import IntentRouter
from app.conversation.language_engine import LanguageEngine
from app.conversation.memory_engine import MemoryEngine
from app.conversation.planet_translator import PlanetTranslator
from app.conversation.state_manager import StateManager
from app.utils.geo_resolver import resolve_coordinates

# -----------------------------------------------------------------------------
# Keyboard / text helpers (language-aware)
# -----------------------------------------------------------------------------

TOPIC_KEYBOARDS = {
    LanguageEngine.ENGLISH: [["Career 💼", "Finance 💰"], ["Health 🏥", "Marriage 💍"], ["Other 🔮"]],
    LanguageEngine.HINDI_ROMAN: [["Career 💼", "Finance 💰"], ["Health 🏥", "Marriage 💍"], ["Other 🔮"]],
}

class DialogEngine:

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

    @staticmethod
    def process(user_id, text, session=None):
        MemoryEngine.add_user_message(user_id, text)
        session = StateManager.get_or_create_session(user_id)

        lang = getattr(session, "language_mode", LanguageEngine.ENGLISH) or LanguageEngine.ENGLISH
        script = getattr(session, "script", None) or "latin"

        # --------------------------------------------------------------
        # 1. /start - Boot sequence
        # --------------------------------------------------------------
        if text == "/start":
            StateManager.update_session(
                user_id,
                step="language",
                language_mode=None,
                chart_data=None,
                dob=None,
                tob=None,
                place=None
            )
            MemoryEngine.clear(user_id)
            return {
                "text": "Hi! ✋ I'm Trishivara, your personal AI astrologer. To continue in English, tap English. Hindi ke liye Hindi tap karein.",
                "keyboard": {
                    "keyboard": [["English", "Hindi"]],
                    "resize_keyboard": True,
                    "one_time_keyboard": True,
                },
            }

        # --------------------------------------------------------------
        # 2. LANGUAGE SELECTION
        # --------------------------------------------------------------
        if session.step == "language":
            if text.lower() == "hindi":
                lang_mode = LanguageEngine.HINDI_ROMAN
                reply_text = "Namaste! 🙏 Main Trishivara, aapka AI Astrologer. Sahi kundali banane ke liye, kripya apni birth details share karein.\n\nApna Gender chunein👇"
            else:
                lang_mode = LanguageEngine.ENGLISH
                reply_text = "Hello! 🙏 I am Trishivara, your AI Astrologer. To create an accurate Kundali, please share your birth details.\n\nSelect your Gender👇"

            StateManager.update_session(user_id, step="gender", language_mode=lang_mode)
            return {
                "text": reply_text,
                "keyboard": {
                    "keyboard": [["Male 👨", "Female 👩", "Other 🏳️‍⚧️"]],
                    "resize_keyboard": True,
                    "one_time_keyboard": True,
                }
            }

        # --------------------------------------------------------------
        # 3. GENDER SELECTION
        # --------------------------------------------------------------
        if session.step == "gender":
            StateManager.update_session(user_id, step="dob")
            
            if lang == LanguageEngine.HINDI_ROMAN:
                reply_text = "Apni Date of Birth bataiye (Format: DD/MM/YYYY) 👇"
            else:
                reply_text = "Please enter your Date of Birth (Format: DD/MM/YYYY) 👇"
                
            return {
                "text": reply_text,
                "keyboard": {"remove_keyboard": True}
            }

        # --------------------------------------------------------------
        # 4. DOB COLLECTION
        # --------------------------------------------------------------
        if session.step == "dob":
            StateManager.update_session(user_id, step="tob", dob=text)
            
            if lang == LanguageEngine.HINDI_ROMAN:
                reply_text = "Apna Time of Birth bataiye (Format: HH:MM AM/PM) 👇"
            else:
                reply_text = "Please enter your Time of Birth (Format: HH:MM AM/PM) 👇"
                
            return {"text": reply_text}

        # --------------------------------------------------------------
        # 5. TOB COLLECTION
        # --------------------------------------------------------------
        if session.step == "tob":
            StateManager.update_session(user_id, step="place", tob=text)
            
            if lang == LanguageEngine.HINDI_ROMAN:
                reply_text = "Apna Place of Birth bataiye (City, State) 👇"
            else:
                reply_text = "Please enter your Place of Birth (City, State) 👇"
                
            return {"text": reply_text}

        # --------------------------------------------------------------
        # 6. PLACE COLLECTION & CHART GENERATION
        # --------------------------------------------------------------
        if session.step == "place":
            StateManager.update_session(user_id, step="question", place=text)
            session.place = text 
            session.dob = getattr(session, "dob", "01/01/2000") # Failsafe
            session.tob = getattr(session, "tob", "12:00 PM")   # Failsafe
            
            try:
                chart = DialogEngine.load_chart(user_id, session)
            except Exception as e:
                pass 
                
            if lang == LanguageEngine.HINDI_ROMAN:
                reply_text = "Kundali ban rahi hai... ⏳\n\nAapki Kundali ban gayi hai! 🎉 Aaj aap kis vishay par baat karna chahenge?"
            else:
                reply_text = "Generating Kundali... ⏳\n\nYour Kundali is ready! 🎉 What topic would you like to discuss today?"
                
            return {
                "text": reply_text,
                "keyboard": {
                    "keyboard": TOPIC_KEYBOARDS.get(lang, TOPIC_KEYBOARDS[LanguageEngine.ENGLISH]),
                    "resize_keyboard": True,
                    "one_time_keyboard": True,
                }
            }

        # --------------------------------------------------------------
        # 7. MAIN CONSULTATION (Premium LLM Pipeline + Graha Translator)
        # --------------------------------------------------------------
        if session.step == "question":
            from app.ai import ask_ai
            from app.conversation.prompt_builder import AstrologerPrompts
            from app.conversation.planet_translator import PlanetTranslator
            
            consultation_state = ConsultationEngine.load_state(
                getattr(session, "consultation_state_blob", None)
            )
            active_topic = consultation_state.get("topic") or getattr(session, "last_domain", None)
            domain = IntentRouter.detect_domain(text, current_domain=active_topic)
            
            chart = DialogEngine.load_chart(user_id, session)
            score_domain = ConsultationEngine.score_domain(domain or active_topic)
            
            domain_data = {}
            if score_domain:
                domain_data = dict(chart.get("domain_scores", {}).get(score_domain, {}))
            
            if "current_dasha" in chart:
                domain_data["current_dasha"] = chart["current_dasha"]

            messages = AstrologerPrompts.build_system_messages(domain_data, lang, script)

            history = MemoryEngine.get_history(user_id)
            for msg in history:
                messages.append(msg)

            ai_reply = ask_ai(messages)
            ai_reply = PlanetTranslator.translate(ai_reply, lang, script)

            StateManager.update_session(user_id, last_domain=(domain or active_topic))
            MemoryEngine.add_bot_message(user_id, ai_reply)

            return {
                "text": ai_reply,
                "keyboard": {"remove_keyboard": True},
            }

        # --------------------------------------------------------------
        # FALLBACK
        # --------------------------------------------------------------
        return {
            "text": "Type /start to begin.",
            "keyboard": {"remove_keyboard": True},
        }