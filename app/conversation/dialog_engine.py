import json
import re
from datetime import datetime

# Assuming these exist in your project
from app.astro_engine import ParashariEngine
from app.conversation.consultation_engine import ConsultationEngine
from app.conversation.intent_router import IntentRouter
from app.conversation.language_engine import LanguageEngine
from app.conversation.memory_engine import MemoryEngine
from app.conversation.persona_layer import PersonaLayer
from app.conversation.state_manager import StateManager
from app.utils.geo_resolver import resolve_coordinates

LANGUAGE_KEYBOARD = [["English", "Roman Hindi"]]
TOPIC_KEYBOARD = [["Career", "Finance"], ["Health", "Marriage"]]
GENDER_KEYBOARD = [["Male", "Female", "Other"]]
CONFIRM_KEYBOARDS = {
    LanguageEngine.ENGLISH: [["Yes", "No"]],
    LanguageEngine.HINDI_ROMAN: [["Haan", "Nahi"]],
}
STEP_ALIASES = {
    "initial_topic": "topic",
    "tob": "time",
    "question": "consult",
}
VALID_STEPS = {"start", "language", "topic", "dob", "time", "place", "gender", "name", "confirm", "consult"}
CONSULT_SUGGESTIONS = {
    "career": {
        LanguageEngine.ENGLISH: [["How long until career improves?"], ["What should I do for work growth?"]],
        LanguageEngine.HINDI_ROMAN: [["Career kab improve hoga?"], ["Work growth ke liye kya karu?"]],
    },
    "finance": {
        LanguageEngine.ENGLISH: [["How long until savings improve?"], ["What should I do with spending?"]],
        LanguageEngine.HINDI_ROMAN: [["Savings kab improve hongi?"], ["Spending ke liye kya karu?"]],
    },
    "health": {
        LanguageEngine.ENGLISH: [["How long until health improves?"], ["What should I do for better health?"]],
        LanguageEngine.HINDI_ROMAN: [["Health kab improve hogi?"], ["Better health ke liye kya karu?"]],
    },
    "marriage": {
        LanguageEngine.ENGLISH: [["How long until marriage improves?"], ["What should I do for marriage clarity?"]],
        LanguageEngine.HINDI_ROMAN: [["Shaadi kab improve hogi?"], ["Shaadi clarity ke liye kya karu?"]],
    },
}


class DialogEngine:

    @staticmethod
    def _remove_keyboard():
        return {"remove_keyboard": True}

    @staticmethod
    def _keyboard(rows):
        return {
            "keyboard": rows,
            "resize_keyboard": True,
            "one_time_keyboard": True,
        }

    @staticmethod
    def _start_flow(user_id):
        StateManager.update_session(
            user_id,
            step="language",
            dob=None,
            tob=None,
            place=None,
            gender=None,
            language=None,
            script="latin",
            language_mode=None,
            language_confirmed=False,
            active_profile_name=None,
            last_domain=None,
            chart_data=None,
            consultation_state_blob=None,
            persona_introduced=False,
        )
        MemoryEngine.clear(user_id)
        return {
            "text": PersonaLayer.language_prompt(),
            "keyboard": DialogEngine._keyboard(LANGUAGE_KEYBOARD),
        }

    @staticmethod
    def _current_step(session):
        raw_step = str(getattr(session, "step", "start") or "start").strip().lower()
        return STEP_ALIASES.get(raw_step, raw_step)

    @staticmethod
    def _current_language(session):
        language = getattr(session, "language_mode", None) or LanguageEngine.ENGLISH
        script = getattr(session, "script", None) or ("roman" if language == LanguageEngine.HINDI_ROMAN else "latin")
        return language, script

    @staticmethod
    def _normalize_language_choice(text):
        value = re.sub(r"\s+", " ", str(text or "").strip().lower())
        if value.startswith("english") or value == "en":
            return LanguageEngine.ENGLISH
        if value in {"roman hindi", "hindi", "hindi roman", "roman", "hinglish"}:
            return LanguageEngine.HINDI_ROMAN
        return None

    @staticmethod
    def _normalize_gender(text):
        value = re.sub(r"\s+", " ", str(text or "").strip().lower())
        if value in {"male", "m"}:
            return "male"
        if value in {"female", "f"}:
            return "female"
        if value in {"other", "o"}:
            return "other"
        return None

    @staticmethod
    def _normalize_date(text):
        value = str(text or "").strip()
        for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"):
            try:
                parsed = datetime.strptime(value, fmt)
                return parsed.strftime("%d/%m/%Y")
            except Exception:
                continue
        return None

    @staticmethod
    def _normalize_time(text):
        value = str(text or "").strip().upper().replace(".", ":")
        value = re.sub(r"\s+", " ", value)
        value = re.sub(r"(?<=\d)(AM|PM)$", r" \1", value)

        for fmt in ("%I:%M %p", "%I %p", "%H:%M"):
            try:
                parsed = datetime.strptime(value, fmt)
                return parsed.strftime("%I:%M %p")
            except Exception:
                continue
        return None

    @staticmethod
    def _normalize_name(text):
        value = re.sub(r"\s+", " ", str(text or "").strip())
        if not value:
            return None
        if IntentRouter.contains_devanagari(value):
            return None
        if not re.fullmatch(r"[A-Za-z][A-Za-z .'-]{0,79}", value):
            return None
        return value

    @staticmethod
    def _affirmative(text):
        return str(text or "").strip().lower() in {"yes", "haan", "ha", "confirm"}

    @staticmethod
    def _negative(text):
        return str(text or "").strip().lower() in {"no", "nahi", "nahin"}

    @staticmethod
    def _topic_from_session(session):
        return IntentRouter.normalize_topic(getattr(session, "last_domain", None)) or getattr(session, "last_domain", None)

    @staticmethod
    def _consultation_blob(session, language):
        return ConsultationEngine.prime_state(
            session_state_blob=getattr(session, "consultation_state_blob", None),
            language=language,
            topic=DialogEngine._topic_from_session(session),
            dob=getattr(session, "dob", None),
            time=getattr(session, "tob", None),
            place=getattr(session, "place", None),
            gender=getattr(session, "gender", None),
            name=getattr(session, "active_profile_name", None),
        )

    @staticmethod
    def _consultation_keyboard(topic, language):
        rows = CONSULT_SUGGESTIONS.get(topic, {}).get(language)
        if not rows:
            rows = CONSULT_SUGGESTIONS["career"][LanguageEngine.ENGLISH]
        return DialogEngine._keyboard(rows)

    @staticmethod
    def load_chart(user_id, session):
        dob = getattr(session, "dob", "01/01/2000")
        tob = getattr(session, "tob", "12:00 PM")
        place = getattr(session, "place", "Delhi")

        if getattr(session, "chart_data", None):
            try:
                return json.loads(session.chart_data)
            except Exception:
                pass

        try:
            lat, lon = resolve_coordinates(place)
        except Exception:
            lat, lon = 28.6139, 77.2090

        try:
            chart = ParashariEngine.generate_chart(dob, tob, lat, lon)
            StateManager.update_session(user_id, chart_data=json.dumps(chart))
            return chart
        except Exception:
            return {}

    @staticmethod
    def _language_blocked(lang, text):
        if IntentRouter.contains_devanagari(text):
            return True
        if lang == LanguageEngine.ENGLISH:
            return LanguageEngine.detect_language(text) == LanguageEngine.HINDI_ROMAN
        return LanguageEngine.looks_like_english(text)

    @staticmethod
    def process(user_id, text, session=None):
        user_text = str(text or "").strip()
        MemoryEngine.add_user_message(user_id, user_text)

        if user_text == "/start":
            return DialogEngine._start_flow(user_id)

        session = StateManager.get_or_create_session(user_id)
        step = DialogEngine._current_step(session)

        if step not in VALID_STEPS or step == "start":
            return DialogEngine._start_flow(user_id)

        lang, script = DialogEngine._current_language(session)

        if step == "language":
            selected_language = DialogEngine._normalize_language_choice(user_text)
            if not selected_language:
                return {
                    "text": PersonaLayer.invalid_choice(LanguageEngine.ENGLISH),
                    "keyboard": DialogEngine._keyboard(LANGUAGE_KEYBOARD),
                }

            selected_script = "roman" if selected_language == LanguageEngine.HINDI_ROMAN else "latin"
            StateManager.update_session(
                user_id,
                step="topic",
                language=selected_language,
                script=selected_script,
                language_mode=selected_language,
                language_confirmed=True,
            )
            return {
                "text": PersonaLayer.topic_prompt(selected_language, selected_script),
                "keyboard": DialogEngine._keyboard(TOPIC_KEYBOARD),
            }

        if IntentRouter.contains_devanagari(user_text):
            return {
                "text": PersonaLayer.devanagari_block(lang, script),
                "keyboard": DialogEngine._remove_keyboard() if step != "topic" else DialogEngine._keyboard(TOPIC_KEYBOARD),
            }

        if step == "topic":
            topic = IntentRouter.normalize_topic(user_text)
            if not topic:
                return {
                    "text": PersonaLayer.topic_prompt(lang, script),
                    "keyboard": DialogEngine._keyboard(TOPIC_KEYBOARD),
                }

            StateManager.update_session(user_id, step="dob", last_domain=topic)
            return {
                "text": PersonaLayer.dob_prompt(lang, script),
                "keyboard": DialogEngine._remove_keyboard(),
            }

        if step == "dob":
            dob = DialogEngine._normalize_date(user_text)
            if not dob:
                return {
                    "text": PersonaLayer.dob_prompt(lang, script),
                    "keyboard": DialogEngine._remove_keyboard(),
                }

            StateManager.update_session(user_id, step="time", dob=dob)
            return {
                "text": PersonaLayer.time_prompt(lang, script),
                "keyboard": DialogEngine._remove_keyboard(),
            }

        if step == "time":
            birth_time = DialogEngine._normalize_time(user_text)
            if not birth_time:
                return {
                    "text": PersonaLayer.time_prompt(lang, script),
                    "keyboard": DialogEngine._remove_keyboard(),
                }

            StateManager.update_session(user_id, step="place", tob=birth_time)
            return {
                "text": PersonaLayer.place_prompt(lang, script),
                "keyboard": DialogEngine._remove_keyboard(),
            }

        if step == "place":
            place = re.sub(r"\s+", " ", user_text).strip()
            if not place:
                return {
                    "text": PersonaLayer.place_prompt(lang, script),
                    "keyboard": DialogEngine._remove_keyboard(),
                }

            StateManager.update_session(user_id, step="gender", place=place)
            return {
                "text": PersonaLayer.gender_prompt(lang, script),
                "keyboard": DialogEngine._keyboard(GENDER_KEYBOARD),
            }

        if step == "gender":
            gender = DialogEngine._normalize_gender(user_text)
            if not gender:
                return {
                    "text": PersonaLayer.gender_prompt(lang, script),
                    "keyboard": DialogEngine._keyboard(GENDER_KEYBOARD),
                }

            StateManager.update_session(user_id, step="name", gender=gender)
            return {
                "text": PersonaLayer.name_prompt(lang, script),
                "keyboard": DialogEngine._remove_keyboard(),
            }

        if step == "name":
            name = DialogEngine._normalize_name(user_text)
            if not name:
                return {
                    "text": PersonaLayer.name_prompt(lang, script),
                    "keyboard": DialogEngine._remove_keyboard(),
                }

            topic = DialogEngine._topic_from_session(session)
            dob = getattr(session, "dob", "")
            birth_time = getattr(session, "tob", "")
            place = getattr(session, "place", "")
            gender = getattr(session, "gender", "")

            StateManager.update_session(user_id, step="confirm", active_profile_name=name)

            return {
                "text": PersonaLayer.confirmation_prompt(
                    topic=topic,
                    dob=dob,
                    birth_time=birth_time,
                    place=place,
                    gender=gender,
                    name=name,
                    language=lang,
                    script=script,
                ),
                "keyboard": DialogEngine._keyboard(CONFIRM_KEYBOARDS.get(lang, CONFIRM_KEYBOARDS[LanguageEngine.ENGLISH])),
            }

        if step == "confirm":
            if DialogEngine._negative(user_text):
                StateManager.update_session(
                    user_id,
                    step="topic",
                    dob=None,
                    tob=None,
                    place=None,
                    gender=None,
                    active_profile_name=None,
                    chart_data=None,
                    consultation_state_blob=None,
                    persona_introduced=False,
                )
                return {
                    "text": PersonaLayer.topic_prompt(lang, script),
                    "keyboard": DialogEngine._keyboard(TOPIC_KEYBOARD),
                }

            if not DialogEngine._affirmative(user_text):
                return {
                    "text": PersonaLayer.invalid_choice(lang, script),
                    "keyboard": DialogEngine._keyboard(CONFIRM_KEYBOARDS.get(lang, CONFIRM_KEYBOARDS[LanguageEngine.ENGLISH])),
                }

            reloaded = StateManager.reload_session(user_id) or session
            consultation_blob = DialogEngine._consultation_blob(reloaded, lang)
            StateManager.update_session(
                user_id,
                step="consult",
                consultation_state_blob=consultation_blob,
                persona_introduced=True,
            )
            MemoryEngine.clear(user_id)

            consult_session = StateManager.reload_session(user_id) or reloaded
            DialogEngine.load_chart(user_id, consult_session)
            topic = DialogEngine._topic_from_session(consult_session) or "career"
            intro = PersonaLayer.astrologer_intro(lang, script)
            prompt = PersonaLayer.consult_prompt(topic, lang, script)
            response_text = f"{intro}\n\n{prompt}"
            MemoryEngine.add_bot_message(user_id, response_text)
            return {
                "text": response_text,
                "keyboard": DialogEngine._consultation_keyboard(topic, lang),
            }

        if step == "consult":
            if DialogEngine._language_blocked(lang, user_text):
                return {
                    "text": PersonaLayer.language_lock(lang, script),
                    "keyboard": DialogEngine._remove_keyboard(),
                }

            try:
                consultation_blob = DialogEngine._consultation_blob(session, lang)
                active_topic = DialogEngine._topic_from_session(session)
                domain = IntentRouter.detect_domain(user_text, current_domain=active_topic) or active_topic
                domain_switched = bool(domain and active_topic and domain != active_topic)

                chart = DialogEngine.load_chart(user_id, session) or {}
                score_domain = ConsultationEngine.score_domain(domain or active_topic)
                domain_data = {}
                if score_domain:
                    domain_data = dict(chart.get("domain_scores", {}).get(score_domain, {}))

                current_dasha = chart.get("current_dasha", {})
                if current_dasha:
                    domain_data["current_dasha"] = current_dasha

                response = ConsultationEngine.generate_response(
                    user_id=user_id,  # <--- CRITICAL FIX: Pass user_id for history lookup
                    domain=domain,
                    domain_data=domain_data,
                    language=lang,
                    script=script,
                    stage=None,
                    age=getattr(session, "age", None),
                    life_stage=getattr(session, "life_stage", None),
                    user_goal=getattr(session, "user_goal", None),
                    current_dasha=current_dasha,
                    transits=chart.get("transit"),
                    persona_introduced=getattr(session, "persona_introduced", False),
                    chart=chart,
                    theme_shown=getattr(session, "theme_shown", False),
                    user_text=user_text,
                    session_state_blob=consultation_blob,
                    domain_switched=domain_switched,
                    normalized_intent=IntentRouter.normalize_intent(user_text),
                )

                StateManager.update_session(
                    user_id,
                    step="consult",
                    last_domain=(domain or active_topic),
                    consultation_state_blob=response.get("state_blob"),
                )
                MemoryEngine.add_bot_message(user_id, response.get("text", ""))

                return {
                    "text": response.get("text", ""),
                    "keyboard": DialogEngine._remove_keyboard(),
                }
            except Exception as e:
                # Log error
                print(f"Error in consultation: {e}")
                return {
                    "text": PersonaLayer.technical_issue(lang, script),
                    "keyboard": DialogEngine._remove_keyboard(),
                }

        return DialogEngine._start_flow(user_id)
