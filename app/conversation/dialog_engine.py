import json

from app.astro_engine import ParashariEngine
from app.conversation.consultation_engine import ConsultationEngine
from app.conversation.intent_router import IntentRouter
from app.conversation.language_engine import LanguageEngine
from app.conversation.memory_engine import MemoryEngine
from app.conversation.planet_translator import PlanetTranslator
from app.conversation.state_manager import StateManager
from app.utils.geo_resolver import resolve_coordinates

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
        script = getattr(session, "script", "latin")

        # --------------------------------------------------------------
        # 1. /start - The Secure Welcome Boot Sequence
        # --------------------------------------------------------------
        if text == "/start":
            StateManager.update_session(
                user_id, step="language", language_mode=None, chart_data=None, dob=None, tob=None, place=None, active_profile_name=None, last_domain=None
            )
            MemoryEngine.clear(user_id)
            return {
                "text": "Welcome to Trishivara! ✨\nYou can call & chat with our expert Astrologers, for accurate guidance, all your chat are completely secure and private.\n\nAap hamare expert Astrologers se call aur chat kar sakte ho, accurate guidance ke liye, aur aapki saari chats bilkul secure aur private hain.\n\nWhich language would you like to chat in?\nAap kis language mein chat karna chahenge?",
                "keyboard": {
                    "keyboard": [
                        ["English - I'd prefer to chat in English"],
                        ["Hindi - Mujhe Hindi mein baat karni hai"]
                    ],
                    "resize_keyboard": True,
                    "one_time_keyboard": True,
                },
            }

        # --------------------------------------------------------------
        # 2. LANGUAGE -> INTENT HOOK
        # --------------------------------------------------------------
        if session.step == "language":
            if text.lower().startswith("hindi"):
                lang_mode = LanguageEngine.HINDI_ROMAN
                reply_text = "Aap apne jeevan ke kis kshetra ke baare mein jaanna chahte hain? 👇"
            elif text.lower().startswith("english"):
                lang_mode = LanguageEngine.ENGLISH
                reply_text = "What area of your life would you like to know about? 👇"
            else:
                return {
                    "text": "Please tap a button below / Kripya neeche diye gaye button par tap karein 👇",
                    "keyboard": {
                        "keyboard": [["English - I'd prefer to chat in English"], ["Hindi - Mujhe Hindi mein baat karni hai"]],
                        "resize_keyboard": True
                    }
                }

            StateManager.update_session(user_id, step="initial_topic", language_mode=lang_mode)
            return {
                "text": reply_text,
                "keyboard": {
                    "keyboard": TOPIC_KEYBOARDS.get(lang_mode, TOPIC_KEYBOARDS[LanguageEngine.ENGLISH]),
                    "resize_keyboard": True,
                    "one_time_keyboard": True,
                }
            }

        # --------------------------------------------------------------
        # 3. INITIAL TOPIC -> NAME COLLECTION
        # --------------------------------------------------------------
        if session.step == "initial_topic":
            StateManager.update_session(user_id, step="name", last_domain=text)
            
            if lang == LanguageEngine.HINDI_ROMAN:
                reply_text = "Aap ko iski jankari denay k liye mujey app ka details chaiye.\n\nKripya apna Naam bataiye 👇"
            else:
                reply_text = "To give you accurate guidance about this, I need your birth details.\n\nPlease tell me your Name 👇"

            return {
                "text": reply_text,
                "keyboard": {"remove_keyboard": True}
            }

        # --------------------------------------------------------------
        # 4. NAME -> GENDER
        # --------------------------------------------------------------
        if session.step == "name":
            StateManager.update_session(user_id, step="gender", active_profile_name=text)
            reply_text = "Apna Gender chunein 👇" if lang == LanguageEngine.HINDI_ROMAN else "Select your Gender 👇"
            return {
                "text": reply_text,
                "keyboard": {
                    "keyboard": [["Male 👨", "Female 👩", "Other 🏳️‍⚧️"]],
                    "resize_keyboard": True,
                    "one_time_keyboard": True,
                }
            }

        # --------------------------------------------------------------
        # 5. GENDER -> DOB
        # --------------------------------------------------------------
        if session.step == "gender":
            StateManager.update_session(user_id, step="dob")
            reply_text = "Apni Date of Birth bataiye (Format: DD/MM/YYYY) 👇" if lang == LanguageEngine.HINDI_ROMAN else "Please enter your Date of Birth (Format: DD/MM/YYYY) 👇"
            return {"text": reply_text, "keyboard": {"remove_keyboard": True}}

        # --------------------------------------------------------------
        # 6. DOB -> TOB (With 12 PM hint)
        # --------------------------------------------------------------
        if session.step == "dob":
            StateManager.update_session(user_id, step="tob", dob=text)
            if lang == LanguageEngine.HINDI_ROMAN:
                reply_text = "Apna Time of Birth bataiye (Format: HH:MM AM/PM).\nAgar exact time nahi pata hai, toh aap 12:00 PM likh sakte hain 👇"
            else:
                reply_text = "Please enter your Time of Birth (Format: HH:MM AM/PM).\nIf you don't know the exact time, you can enter 12:00 PM 👇"
            return {"text": reply_text}

        # --------------------------------------------------------------
        # 7. TOB -> PLACE
        # --------------------------------------------------------------
        if session.step == "tob":
            StateManager.update_session(user_id, step="place", tob=text)
            reply_text = "Apna Place of Birth bataiye (City, State) 👇" if lang == LanguageEngine.HINDI_ROMAN else "Please enter your Place of Birth (City, State) 👇"
            return {"text": reply_text}

        # --------------------------------------------------------------
        # 8. PLACE -> CHART GENERATION & WELCOME SUMMARY
        # --------------------------------------------------------------
        if session.step == "place":
            StateManager.update_session(user_id, step="question", place=text)
            session.place = text 
            session.dob = getattr(session, "dob", "01/01/2000")
            session.tob = getattr(session, "tob", "12:00 PM")
            name = getattr(session, "active_profile_name", "User")
            
            try:
                chart = DialogEngine.load_chart(user_id, session)
            except Exception as e:
                pass 
                
            if lang == LanguageEngine.HINDI_ROMAN:
                reply_text = f"""Kundali ban rahi hai... ⏳

My Details:
Date of Birth: {session.dob}
Time of Birth: {session.tob}
Place of Birth: {session.place}

Namaste {name} ji main Hemant hoon aapka AI astrologer.

Aaj kaise hain aap?

Aaj kis bare mein baat karna chahenge?"""
                suggestions = [["Aagey opportunities kab milenge?"], ["Dhan prapti ke yog hain?"]]
            else:
                reply_text = f"""Generating Kundali... ⏳

My Details:
Date of Birth: {session.dob}
Time of Birth: {session.tob}
Place of Birth: {session.place}

Namaste {name} ji, I am Rohan, your AI astrologer.

How are you today?

What would you like to discuss today?"""
                suggestions = [["When will I get new opportunities?"], ["Are there chances of wealth gain?"]]
                
            return {
                "text": reply_text,
                "keyboard": {
                    "keyboard": suggestions,
                    "resize_keyboard": True,
                    "one_time_keyboard": True,
                }
            }

        # --------------------------------------------------------------
        # 9. MAIN CONSULTATION (With Strict Language Lock)
        # --------------------------------------------------------------
        if session.step == "question":
            
            # THE STRICT LANGUAGE LOCK INTERCEPTOR
            is_english = LanguageEngine.looks_like_english(text)
            detected_lang = LanguageEngine.detect_language(text)

            if lang == LanguageEngine.HINDI_ROMAN and is_english:
                return {
                    "text": "Aap ney hindi language choose kiya hai toh aap hindi mey baat kijiye.",
                    "keyboard": {"remove_keyboard": True}
                }
            elif lang == LanguageEngine.ENGLISH and detected_lang == LanguageEngine.HINDI_ROMAN:
                return {
                    "text": "You chose English as your language, please chat in English.",
                    "keyboard": {"remove_keyboard": True}
                }

            # If language check passes, proceed to LLM
            from app.ai import ask_ai
            from app.conversation.prompt_builder import AstrologerPrompts
            from app.conversation.planet_translator import PlanetTranslator
            
            consultation_state = ConsultationEngine.load_state(getattr(session, "consultation_state_blob", None))
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

        return {
            "text": "Type /start to begin.",
            "keyboard": {"remove_keyboard": True},
        }