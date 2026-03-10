import json
from datetime import datetime

from app.astro_engine import ParashariEngine
from app.conversation.consultation_engine import ConsultationEngine
from app.conversation.intent_router import IntentRouter
from app.conversation.memory_engine import MemoryEngine
from app.conversation.planet_translator import PlanetTranslator
from app.conversation.profile_manager import ProfileManager
from app.conversation.state_manager import StateManager
from app.conversation.timing_router import TimingRouter
from app.conversation.life_stage_detector import detect as detect_life_stage
from app.utils.age_calculator import calculate_age
from app.utils.birth_data_parser import BirthDataParser
from app.utils.geo_resolver import resolve_coordinates


LANGUAGE_MENU = {
    "keyboard": [["English"], ["हिंदी"], ["Hindi (Roman)"]],
    "resize_keyboard": True,
}

MAIN_MENU_EN = {
    "keyboard": [["🔮 Quick Astrology Question"], ["📜 Full Birth Chart Reading"]],
    "resize_keyboard": True,
}

MAIN_MENU_DEV = {
    "keyboard": [["🔮 त्वरित ज्योतिष प्रश्न"], ["📜 पूर्ण कुंडली विश्लेषण"]],
    "resize_keyboard": True,
}

MAIN_MENU_ROM = {
    "keyboard": [["🔮 Turant Jyotish Prashna"], ["📜 Poori Kundli Vishleshan"]],
    "resize_keyboard": True,
}

PROFILE_SCOPE_EN = {
    "keyboard": [["My Chart"], ["Family Member"]],
    "resize_keyboard": True,
}

PROFILE_SCOPE_DEV = {
    "keyboard": [["मेरी कुंडली"], ["Family Member"]],
    "resize_keyboard": True,
}

PROFILE_SCOPE_ROM = {
    "keyboard": [["Meri Kundli"], ["Family Member"]],
    "resize_keyboard": True,
}

DOMAIN_MENU_EN = {
    "keyboard": [["Career", "Finance"], ["Marriage", "Health"]],
    "resize_keyboard": True,
}

DOMAIN_MENU_DEV = {
    "keyboard": [["करियर", "धन"], ["विवाह", "स्वास्थ्य"]],
    "resize_keyboard": True,
}

DOMAIN_MENU_ROM = {
    "keyboard": [["Career", "Paisa"], ["Shaadi", "Health"]],
    "resize_keyboard": True,
}


class DialogEngine:
    GOAL_KEYWORDS = {
        "job_promotion": ["promotion", "increment", "salary hike", "प्रमोशन"],
        "business_start": ["business", "startup", "start business", "व्यापार", "बिजनेस"],
        "job_switch": ["job switch", "change job", "new job", "नौकरी बदल"],
        "relationship_growth": ["relationship", "marriage", "shaadi", "विवाह", "रिश्ता"],
        "health_recovery": ["health", "recovery", "fitness", "स्वास्थ्य"],
        "wealth_growth": ["wealth", "investment", "savings", "finance", "धन", "पैसा"],
    }

    @staticmethod
    def _is_hi_dev(language, script):
        return language == "hi" and script == "devanagari"

    @staticmethod
    def _is_hi_rom(language, script):
        return language == "hi" and script == "roman"

    @staticmethod
    def _main_menu(language, script):
        if DialogEngine._is_hi_dev(language, script):
            return MAIN_MENU_DEV

        if DialogEngine._is_hi_rom(language, script):
            return MAIN_MENU_ROM

        return MAIN_MENU_EN

    @staticmethod
    def _profile_scope_menu(language, script):
        if DialogEngine._is_hi_dev(language, script):
            return PROFILE_SCOPE_DEV

        if DialogEngine._is_hi_rom(language, script):
            return PROFILE_SCOPE_ROM

        return PROFILE_SCOPE_EN

    @staticmethod
    def _domain_menu(language, script):
        if DialogEngine._is_hi_dev(language, script):
            return DOMAIN_MENU_DEV

        if DialogEngine._is_hi_rom(language, script):
            return DOMAIN_MENU_ROM

        return DOMAIN_MENU_EN

    @staticmethod
    def _infer_script_from_text(text):
        if not text:
            return None

        if any("\u0900" <= ch <= "\u097F" for ch in text):
            return "devanagari"

        t = text.lower()
        roman_markers = [
            "turant",
            "jyotish",
            "prashna",
            "poori",
            "kundli",
            "vishleshan",
            "janm",
            "shaadi",
            "paisa",
            "hindi",
        ]

        if any(marker in t for marker in roman_markers):
            return "roman"

        return None

    @staticmethod
    def _coerce_language_script(session, text=""):
        language = getattr(session, "language", None)
        script = getattr(session, "script", None)

        if language == "hi" and not script:
            script = DialogEngine._infer_script_from_text(text) or "devanagari"

        return language, script

    @staticmethod
    def _birth_details_prompt(language, script, profile_name):
        target = profile_name or "this profile"

        if DialogEngine._is_hi_dev(language, script):
            return (
                f"{target} के लिए जन्म जानकारी भेजें।\n\n"
                "कृपया भेजें:\n"
                "जन्म तिथि (YYYY-MM-DD)\n"
                "जन्म समय (HH:MM)\n"
                "जन्म स्थान"
            )

        if DialogEngine._is_hi_rom(language, script):
            return (
                f"{target} ke liye janm jaankari bhejiye.\n\n"
                "Kripya bheje:\n"
                "Janm tareekh (YYYY-MM-DD)\n"
                "Janm samay (HH:MM)\n"
                "Janm sthan"
            )

        return (
            f"Please share birth details for {target}.\n\n"
            "Send:\n"
            "Date of birth (YYYY-MM-DD)\n"
            "Time of birth (HH:MM)\n"
            "Birth place"
        )

    @staticmethod
    def _birth_data_retry_prompt(language, script):
        if DialogEngine._is_hi_dev(language, script):
            return "कृपया पूरी जन्म जानकारी भेजें: जन्म तिथि, समय, और स्थान।"

        if DialogEngine._is_hi_rom(language, script):
            return "Kripya poori janm jaankari bheje: tareekh, samay, aur sthan."

        return "Please send complete birth details: date, time, and place."

    @staticmethod
    def _domain_prompt(language, script):
        if DialogEngine._is_hi_dev(language, script):
            return "अब आप किस विषय पर मार्गदर्शन चाहते हैं?"

        if DialogEngine._is_hi_rom(language, script):
            return "Ab aap kis topic par guidance chahte hain?"

        return "What area would you like to explore now?"

    @staticmethod
    def _domain_not_detected(language, script):
        if DialogEngine._is_hi_dev(language, script):
            return "कृपया Career, Finance, Marriage या Health में से विषय चुनें।"

        if DialogEngine._is_hi_rom(language, script):
            return "Kripya Career, Finance, Marriage ya Health mein se topic chuniye."

        return "Please choose a topic from Career, Finance, Marriage, or Health."

    @staticmethod
    def _normalize_birth_data(dob, tob):
        normalized_dob = datetime.strptime(dob, "%Y-%m-%d").strftime("%Y-%m-%d")
        normalized_tob = str(tob or "").strip()
        return normalized_dob, normalized_tob

    @staticmethod
    def _active_profile(session):
        profiles = ProfileManager.parse_profiles(getattr(session, "profiles", None))
        active_name = str(getattr(session, "active_profile_name", "") or "").strip().lower()

        if active_name:
            for profile in profiles:
                if str(profile.get("name", "")).strip().lower() == active_name:
                    return profile

        if profiles:
            return profiles[0]

        return {
            "name": getattr(session, "active_profile_name", None) or "",
            "dob": getattr(session, "dob", None) or "",
            "tob": getattr(session, "tob", None) or "",
            "place": getattr(session, "place", None) or "",
        }

    @staticmethod
    def _detect_goal(text):
        if not text:
            return None

        t = text.lower()

        for goal, markers in DialogEngine.GOAL_KEYWORDS.items():
            if any(marker in t for marker in markers):
                return goal

        return None

    @staticmethod
    def load_chart(user_id, session):
        active_profile = DialogEngine._active_profile(session)
        dob = str(active_profile.get("dob", "") or "").strip()
        tob = str(active_profile.get("tob", "") or "").strip()
        place = str(active_profile.get("place", "") or "").strip()

        if session.chart_data:
            try:
                return json.loads(session.chart_data)
            except Exception:
                pass

        if not dob or not tob or not place:
            raise ValueError("Missing birth details for active profile")

        dob, tob = DialogEngine._normalize_birth_data(dob, tob)
        lat, lon = resolve_coordinates(place)

        chart = ParashariEngine.generate_chart(dob, tob, lat, lon)
        StateManager.update_session(user_id, chart_data=json.dumps(chart))

        return chart

    @staticmethod
    def process(user_id, text, session=None):
        MemoryEngine.add_user_message(user_id, text)

        session = StateManager.get_or_create_session(user_id)
        language = session.language or "en"
        script = getattr(session, "script", None) or "latin"

        if text == "/start":
            StateManager.update_session(
                user_id,
                step="language",
                language=None,
                script=None,
                last_domain=None,
                conversation_phase=ConsultationEngine.DOMAIN_ENTRY,
                last_followup_question=None,
                theme_shown=False,
                persona_introduced=False,
                chart_data=None,
                pending_profile_name=None,
                active_profile_name=None,
            )
            MemoryEngine.clear(user_id)

            return {
                "text": "Please select your language\n\nकृपया अपनी भाषा चुनें",
                "keyboard": LANGUAGE_MENU,
            }

        if session.step in {"start", "language"}:
            t = text.lower()

            if "roman" in t:
                StateManager.update_session(
                    user_id,
                    language="hi",
                    script="roman",
                    step="menu",
                    last_domain=None,
                )
                return {
                    "text": "Namaste.\n\nAap kaise shuru karna chahenge?",
                    "keyboard": MAIN_MENU_ROM,
                }

            if "english" in t:
                StateManager.update_session(
                    user_id,
                    language="en",
                    script="latin",
                    step="menu",
                    last_domain=None,
                )
                return {
                    "text": "Welcome.\n\nHow would you like to begin?",
                    "keyboard": MAIN_MENU_EN,
                }

            if "हिंदी" in text:
                StateManager.update_session(
                    user_id,
                    language="hi",
                    script="devanagari",
                    step="menu",
                    last_domain=None,
                )
                return {
                    "text": "नमस्ते।\n\nआप कैसे शुरू करना चाहेंगे?",
                    "keyboard": MAIN_MENU_DEV,
                }

            if "hindi" in t:
                StateManager.update_session(
                    user_id,
                    language="hi",
                    script="roman",
                    step="menu",
                    last_domain=None,
                )
                return {
                    "text": "Namaste.\n\nAap kaise shuru karna chahenge?",
                    "keyboard": MAIN_MENU_ROM,
                }

            return {
                "text": "Please choose a language / कृपया भाषा चुनें",
                "keyboard": LANGUAGE_MENU,
            }

        if session.step == "menu":
            t = text.lower()
            language, script = DialogEngine._coerce_language_script(session, text)

            quick_selected = (
                "quick" in t
                or "turant" in t
                or "त्वरित" in text
                or "jyotish prashna" in t
            )
            full_selected = (
                "chart" in t
                or "kundli" in t
                or "कुंडली" in text
                or "vishleshan" in t
                or "poori" in t
            )

            if quick_selected or full_selected:
                StateManager.update_session(
                    user_id,
                    step="profile_scope",
                    pending_profile_name=None,
                    conversation_phase=ConsultationEngine.DOMAIN_ENTRY,
                    last_followup_question=None,
                    chart_data=None,
                )
                return {
                    "text": ProfileManager.declaration_prompt(language, script),
                    "keyboard": DialogEngine._profile_scope_menu(language, script),
                }

            if DialogEngine._is_hi_dev(language, script):
                return {"text": "कृपया मेनू से एक विकल्प चुनें।", "keyboard": MAIN_MENU_DEV}

            if DialogEngine._is_hi_rom(language, script):
                return {"text": "Kripya menu se ek vikalp chuniye.", "keyboard": MAIN_MENU_ROM}

            return {"text": "Please choose an option from the menu.", "keyboard": MAIN_MENU_EN}

        if session.step == "profile_scope":
            language, script = DialogEngine._coerce_language_script(session, text)
            scope = ProfileManager.detect_profile_scope(text)

            if scope == "self":
                profile_name = ProfileManager.default_profile_name(language, script)
                StateManager.update_session(
                    user_id,
                    step="birthdata",
                    pending_profile_name=profile_name,
                    active_profile_name=profile_name,
                )
                return DialogEngine._birth_details_prompt(language, script, profile_name)

            if scope == "family":
                StateManager.update_session(user_id, step="profile_name")
                return ProfileManager.profile_name_prompt(language, script)

            return {
                "text": ProfileManager.declaration_prompt(language, script),
                "keyboard": DialogEngine._profile_scope_menu(language, script),
            }

        if session.step == "profile_name":
            language, script = DialogEngine._coerce_language_script(session, text)
            profile_name = str(text or "").strip()

            if not profile_name or profile_name.startswith("/"):
                return ProfileManager.profile_name_prompt(language, script)

            StateManager.update_session(
                user_id,
                pending_profile_name=profile_name,
                active_profile_name=profile_name,
                step="birthdata",
            )
            return DialogEngine._birth_details_prompt(language, script, profile_name)

        if session.step == "birthdata":
            language, script = DialogEngine._coerce_language_script(session, text)
            parsed = BirthDataParser.parse_birth_data(text)

            dob = parsed.get("date")
            tob = parsed.get("time")
            place = parsed.get("place")

            if not dob or not tob or not place:
                return DialogEngine._birth_data_retry_prompt(language, script)

            profile_name = (
                getattr(session, "pending_profile_name", None)
                or getattr(session, "active_profile_name", None)
                or ProfileManager.default_profile_name(language, script)
            )

            profiles = ProfileManager.parse_profiles(getattr(session, "profiles", None))
            max_allowed = ProfileManager.max_profiles(session)
            profiles, saved, limit_hit = ProfileManager.upsert_profile(
                profiles,
                {
                    "name": profile_name,
                    "dob": dob,
                    "tob": tob,
                    "place": place,
                },
                max_allowed,
            )

            if limit_hit:
                return ProfileManager.limit_message(language, script)

            age = calculate_age(dob)
            life_stage = detect_life_stage(age)

            StateManager.update_session(
                user_id,
                dob=dob,
                tob=tob,
                place=place,
                age=age,
                life_stage=life_stage,
                profiles=ProfileManager.serialize_profiles(profiles),
                active_profile_name=profile_name,
                pending_profile_name=None,
                step="question",
                last_domain=None,
                conversation_phase=ConsultationEngine.DOMAIN_ENTRY,
                last_followup_question=None,
                theme_shown=False,
                chart_data=None,
            )

            return {
                "text": DialogEngine._domain_prompt(language, script),
                "keyboard": DialogEngine._domain_menu(language, script),
            }

        if session.step == "question":
            language, script = DialogEngine._coerce_language_script(session, text)
            last_domain = getattr(session, "last_domain", None)
            domain = (
                ConsultationEngine.detect_domain(text, current_domain=last_domain)
                or IntentRouter.detect_domain(text)
            )
            domain_switched = False
            current_stage = (
                getattr(session, "conversation_phase", None)
                or ConsultationEngine.DOMAIN_ENTRY
            )

            if domain:
                if last_domain != domain:
                    current_stage = ConsultationEngine.DOMAIN_ENTRY
                    domain_switched = True
            else:
                if not last_domain:
                    return {
                        "text": DialogEngine._domain_not_detected(language, script),
                        "keyboard": DialogEngine._domain_menu(language, script),
                    }
                domain = last_domain

            detected_goal = DialogEngine._detect_goal(text)
            effective_goal = detected_goal or getattr(session, "user_goal", None)

            if detected_goal:
                StateManager.update_session(user_id, user_goal=detected_goal)

            chart = DialogEngine.load_chart(user_id, session)
            score_domain = ConsultationEngine.score_domain(domain) or domain
            domain_data = dict(chart.get("domain_scores", {}).get(score_domain, {}))
            domain_data["timing_focus"] = bool(TimingRouter.is_timing_question(text))
            current_dasha = chart.get("current_dasha", {})
            transits = chart.get("transit", {})

            consultation = ConsultationEngine.generate_response(
                domain=domain,
                domain_data=domain_data,
                language=language,
                script=script,
                stage=current_stage,
                age=getattr(session, "age", None),
                life_stage=getattr(session, "life_stage", None),
                user_goal=effective_goal,
                current_dasha=current_dasha,
                transits=transits,
                persona_introduced=bool(getattr(session, "persona_introduced", False)),
                chart=chart,
                theme_shown=bool(getattr(session, "theme_shown", False)) and not domain_switched,
                user_text=text,
                session_state_blob=getattr(session, "last_followup_question", None),
                domain_switched=domain_switched,
            )

            reply = consultation.get("text", "")
            reply = PlanetTranslator.translate(reply, language, script)

            next_stage = consultation.get("next_stage") or ConsultationEngine.next_stage(current_stage)
            persisted_consultation_state = (
                consultation.get("state_blob")
                or consultation.get("followup_question")
            )
            StateManager.update_session(
                user_id,
                last_domain=domain,
                conversation_phase=next_stage,
                last_followup_question=persisted_consultation_state,
                theme_shown=bool(getattr(session, "theme_shown", False))
                or bool(consultation.get("theme_used")),
                persona_introduced=bool(getattr(session, "persona_introduced", False))
                or bool(consultation.get("persona_added")),
                user_goal=effective_goal,
            )

            MemoryEngine.add_bot_message(user_id, reply)
            return reply

        return "Type /start to begin."
