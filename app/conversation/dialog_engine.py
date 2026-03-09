import json
from datetime import datetime

from app.ai import ask_ai
from app.astro_engine import ParashariEngine
from app.conversation.astrologer_persona import AstrologerPersona
from app.conversation.astrology_response_template import AstrologyResponseTemplate
from app.conversation.consultation_engine import ConsultationEngine
from app.conversation.followup_router import FollowupRouter
from app.conversation.intent_router import IntentRouter
from app.conversation.life_stage_detector import LifeStageDetector
from app.conversation.memory_engine import MemoryEngine
from app.conversation.planet_translator import PlanetTranslator
from app.conversation.profile_manager import ProfileManager
from app.conversation.prompt_builder import AstrologerPrompts
from app.conversation.state_manager import StateManager
from app.conversation.timing_router import TimingRouter
from app.utils.age_calculator import AgeCalculator
from app.utils.birth_data_parser import BirthDataParser
from app.utils.geo_resolver import GeoResolver


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


PROFILE_SCOPE_MENU_EN = {
    "keyboard": [
        ["My Chart"],
        ["Family Member"]
    ],
    "resize_keyboard": True
}

PROFILE_SCOPE_MENU_DEV = {
    "keyboard": [
        ["मेरी कुंडली"],
        ["परिवार सदस्य"]
    ],
    "resize_keyboard": True
}

PROFILE_SCOPE_MENU_ROM = {
    "keyboard": [
        ["Meri Kundli"],
        ["Family Member"]
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

    STAGE_BIRTHDATA = FollowupRouter.STAGE_BIRTHDATA
    STAGE_CHART_READING = FollowupRouter.STAGE_CHART_READING
    STAGE_SITUATION_ANALYSIS = FollowupRouter.STAGE_SITUATION_ANALYSIS
    STAGE_STRATEGY_GUIDANCE = FollowupRouter.STAGE_STRATEGY_GUIDANCE
    STAGE_ACTION_PLAN = FollowupRouter.STAGE_ACTION_PLAN

    GOAL_KEYWORDS = {
        "job_promotion": ["promotion", "increment", "raise", "salary hike", "प्रमोशन", "तरक्की"],
        "job_switch": ["job switch", "switch", "new job", "change job", "नौकरी बदल", "switch job"],
        "business_start": ["business", "startup", "start business", "venture", "व्यापार", "business start"],
        "business_growth": ["scale", "grow business", "revenue", "profit", "business growth", "विस्तार"],
        "marriage_timing": ["marriage", "shaadi", "wedding", "kab shaadi", "विवाह", "शादी"],
        "relationship_stability": ["relationship", "rishta", "compatibility", "partner", "संबंध", "रिश्ता"],
        "investment_growth": ["investment", "mutual fund", "stocks", "sip", "निवेश", "portfolio"],
        "debt_reduction": ["loan", "debt", "emi", "karz", "कर्ज", "debt free"],
        "health_recovery": ["health", "recovery", "illness", "disease", "स्वास्थ्य", "बीमारी"],
        "stress_control": ["stress", "anxiety", "mental", "तनाव", "चिंता"]
    }

    @staticmethod
    def normalize_birth_data(session):
        dob = datetime.strptime(session.dob, "%Y-%m-%d").strftime("%Y-%m-%d")
        return dob, session.tob

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
            return PROFILE_SCOPE_MENU_DEV
        if DialogEngine._is_hi_rom(language, script):
            return PROFILE_SCOPE_MENU_ROM
        return PROFILE_SCOPE_MENU_EN

    @staticmethod
    def _domain_menu(language, script):
        if DialogEngine._is_hi_dev(language, script):
            return DOMAIN_MENU_DEV
        if DialogEngine._is_hi_rom(language, script):
            return DOMAIN_MENU_ROM
        return DOMAIN_MENU_EN

    @staticmethod
    def _language_values(session):
        language = getattr(session, "language", None) or "en"
        script = getattr(session, "script", None)

        if language == "hi" and not script:
            script = "devanagari"
        if language == "en" and not script:
            script = "latin"

        return language, script

    @staticmethod
    def _birth_details_prompt(language, script):
        if DialogEngine._is_hi_dev(language, script):
            return (
                "कृपया जन्म जानकारी भेजें:\n"
                "जन्म तिथि\n"
                "जन्म समय\n"
                "जन्म स्थान"
            )

        if DialogEngine._is_hi_rom(language, script):
            return (
                "Kripya janm jaankari bheje:\n"
                "Janm tareekh\n"
                "Janm samay\n"
                "Janm sthan"
            )

        return (
            "Please send birth details:\n"
            "Date of birth\n"
            "Time of birth\n"
            "Birth place"
        )

    @staticmethod
    def _domain_prompt(language, script):
        if DialogEngine._is_hi_dev(language, script):
            return "आप किस विषय के बारे में जानना चाहते हैं?"
        if DialogEngine._is_hi_rom(language, script):
            return "Aap kis vishay ke baare mein jaana chahte hain?"
        return "What area would you like to explore?"

    @staticmethod
    def _domain_not_detected(language, script):
        if DialogEngine._is_hi_dev(language, script):
            return "कृपया कोई विषय चुनें या अपना प्रश्न पूछें।"
        if DialogEngine._is_hi_rom(language, script):
            return "Kripya koi vishay chune ya apna prashna pooche."
        return "Choose a topic or ask your question."

    @staticmethod
    def _menu_retry(language, script):
        if DialogEngine._is_hi_dev(language, script):
            return "कृपया मेनू से एक विकल्प चुनें।"
        if DialogEngine._is_hi_rom(language, script):
            return "Kripya menu se ek vikalp chune."
        return "Please choose an option from the menu."

    @staticmethod
    def _service_error(language, script):
        if DialogEngine._is_hi_dev(language, script):
            return "इस समय सर्वर से कनेक्शन में समस्या है। कृपया थोड़ी देर बाद फिर पूछें।"
        if DialogEngine._is_hi_rom(language, script):
            return "Is samay server connection issue aa raha hai. Kripya thodi der baad phir pooche."
        return "I'm facing a temporary server connection issue. Please try again shortly."

    @staticmethod
    def _to_structured_prompt(base_prompt, language, script):
        if DialogEngine._is_hi_dev(language, script):
            language_line = "All JSON values must be in Hindi Devanagari."
        elif DialogEngine._is_hi_rom(language, script):
            language_line = "All JSON values must be in Roman Hindi (Hinglish)."
        else:
            language_line = "All JSON values must be in English."

        return (
            f"{base_prompt}\n\n"
            "Return ONLY one valid JSON object with keys:\n"
            "observation, cause, timing, guidance, followup\n\n"
            "Rules:\n"
            "- Keep fields concise and conversational.\n"
            "- Do not mention scores, rankings, engines, or internal systems.\n"
            "- Do not output markdown, headings, bullet points, or text outside JSON.\n"
            f"- {language_line}\n"
        )

    @staticmethod
    def _parse_llm_fields(raw_text):
        keys = ["observation", "cause", "timing", "guidance", "followup"]
        parsed = {key: "" for key in keys}

        if not raw_text:
            return parsed

        content = raw_text.strip()

        if content.startswith("```"):
            lines = content.splitlines()
            if lines and lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            content = "\n".join(lines).strip()

        start = content.find("{")
        end = content.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return parsed

        content = content[start:end + 1]

        try:
            obj = json.loads(content)
            if not isinstance(obj, dict):
                return parsed
        except Exception:
            return parsed

        for key in keys:
            value = obj.get(key, "")
            if value is None:
                value = ""
            parsed[key] = str(value).strip()

        return parsed

    @staticmethod
    def _translate_payload(payload, language, script):
        translated = {}
        for key, value in (payload or {}).items():
            translated[key] = PlanetTranslator.translate(str(value), language, script)
        return translated

    @staticmethod
    def _detect_user_goal(text, domain, current_goal):
        message = (text or "").lower()

        for goal, tokens in DialogEngine.GOAL_KEYWORDS.items():
            for token in tokens:
                if token.lower() in message:
                    return goal

        if current_goal:
            return current_goal

        if domain:
            return f"{domain}_clarity"

        return None

    @staticmethod
    def load_chart(user_id, session):
        if session.chart_data:
            try:
                return json.loads(session.chart_data)
            except Exception:
                pass

        dob, time = DialogEngine.normalize_birth_data(session)
        lat, lon = GeoResolver.resolve(session.place)

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
    def _build_stage_prompt(user_id, text, domain, domain_data, language, script, stage, focus, user_goal):
        if stage == DialogEngine.STAGE_CHART_READING:
            base = AstrologerPrompts.build_domain_prompt(
                domain=domain,
                domain_data=domain_data,
                language=language,
                script=script,
                user_id=user_id,
                question=text
            )
        else:
            base = FollowupRouter.build_followup_prompt(
                domain=domain,
                domain_data=domain_data,
                language=language,
                script=script,
                user_id=user_id,
                user_text=text,
                stage=stage,
                focus=focus
            )

        if user_goal:
            base += (
                "\n\nUser stated goal:\n"
                f"{user_goal}\n"
                "Prioritize guidance and examples around this goal.\n"
            )

        return DialogEngine._to_structured_prompt(base, language, script)

    @staticmethod
    def _build_consultation_reply(
        user_id,
        text,
        session,
        language,
        script,
        chart,
        domain,
        stage,
        user_goal
    ):
        domain_data = chart.get("domain_scores", {}).get(domain, {})
        if not domain_data:
            return DialogEngine._domain_not_detected(language, script), stage, getattr(session, "last_followup_question", None), False

        domain_data = dict(domain_data)
        domain_data["timing_focus"] = bool(TimingRouter.is_timing_question(text))

        current_dasha = chart.get("current_dasha", {})
        transits = chart.get("transit", {})

        consultation_context = ConsultationEngine.prepare_consultation_context(
            domain_data=domain_data,
            age=getattr(session, "age", None),
            life_stage=getattr(session, "life_stage", None),
            current_dasha=current_dasha,
            transits=transits,
            user_goal=user_goal
        )

        focus = FollowupRouter.detect_followup_focus(domain, text)
        prompt = DialogEngine._build_stage_prompt(
            user_id=user_id,
            text=text,
            domain=domain,
            domain_data=consultation_context["prompt_domain_data"],
            language=language,
            script=script,
            stage=stage,
            focus=focus,
            user_goal=user_goal
        )

        llm_fields = DialogEngine._parse_llm_fields(ask_ai("", prompt))

        if stage == DialogEngine.STAGE_CHART_READING:
            followup_question = FollowupRouter.get_initial_followup_question(domain, language, script)
        elif stage == DialogEngine.STAGE_SITUATION_ANALYSIS:
            followup_question = FollowupRouter.next_followup_question(
                next_stage=DialogEngine.STAGE_STRATEGY_GUIDANCE,
                language=language,
                script=script,
                previous_question=getattr(session, "last_followup_question", None)
            )
        elif stage == DialogEngine.STAGE_STRATEGY_GUIDANCE:
            followup_question = FollowupRouter.next_followup_question(
                next_stage=DialogEngine.STAGE_ACTION_PLAN,
                language=language,
                script=script,
                previous_question=getattr(session, "last_followup_question", None)
            )
        else:
            followup_question = FollowupRouter.next_followup_question(
                next_stage=DialogEngine.STAGE_ACTION_PLAN,
                language=language,
                script=script,
                previous_question=getattr(session, "last_followup_question", None)
            )

        payload = ConsultationEngine.build_consultation_payload(
            domain=domain,
            domain_data=consultation_context["prompt_domain_data"],
            llm_fields=llm_fields,
            language=language,
            script=script,
            followup_question=followup_question,
            stage=stage,
            age=consultation_context["age"],
            life_stage=consultation_context["life_stage"],
            current_dasha=consultation_context["current_dasha"],
            transits=consultation_context["transits"],
            user_goal=consultation_context["user_goal"]
        )

        # Planet translation after consultation text generation and before final reply.
        payload = DialogEngine._translate_payload(payload, language, script)

        reply = AstrologyResponseTemplate.build_response(payload)

        reply, introduced_now = AstrologerPersona.apply_once(
            reply=reply,
            language=language,
            script=script,
            persona_introduced=bool(getattr(session, "persona_introduced", False))
        )

        return reply, stage, followup_question, introduced_now

    @staticmethod
    def process(user_id, text, session):
        MemoryEngine.add_user_message(user_id, text)

        session = StateManager.get_or_create_session(user_id)
        language, script = DialogEngine._language_values(session)
        step = getattr(session, "step", "start")
        stage = getattr(session, "conversation_phase", None) or DialogEngine.STAGE_BIRTHDATA

        if text == "/start":
            StateManager.update_session(
                user_id,
                step="language",
                language=None,
                script=None,
                last_domain=None,
                last_followup_question=None,
                conversation_phase=DialogEngine.STAGE_BIRTHDATA,
                persona_introduced=False,
                age=None,
                life_stage=None,
                user_goal=None,
                profiles=ProfileManager.serialize_profiles([]),
                pending_profile_name=None,
                active_profile_name=None,
                chart_data=None,
                plan_tier=getattr(session, "plan_tier", None) or "free"
            )
            return {
                "text": "Please select your language\n\nकृपया अपनी भाषा चुनें",
                "keyboard": LANGUAGE_MENU
            }

        if step == "language":
            t = text.lower()

            if "roman" in t or "hindi (roman)" in t:
                StateManager.update_session(
                    user_id,
                    language="hi",
                    script="roman",
                    step="menu",
                    conversation_phase=DialogEngine.STAGE_BIRTHDATA
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
                    step="menu",
                    conversation_phase=DialogEngine.STAGE_BIRTHDATA
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
                    step="menu",
                    conversation_phase=DialogEngine.STAGE_BIRTHDATA
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
                    step="menu",
                    conversation_phase=DialogEngine.STAGE_BIRTHDATA
                )
                return {
                    "text": "Namaste.\n\nAap kaise shuru karna chahenge?",
                    "keyboard": MAIN_MENU_ROM
                }

            return {
                "text": "Please choose a language / कृपया भाषा चुनें",
                "keyboard": LANGUAGE_MENU
            }

        if step == "menu":
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

            if quick_selected or full_selected:
                StateManager.update_session(
                    user_id,
                    step="profile_scope",
                    conversation_phase=DialogEngine.STAGE_BIRTHDATA,
                    last_domain=None,
                    last_followup_question=None,
                    pending_profile_name=None,
                    user_goal=None
                )
                return {
                    "text": ProfileManager.declaration_prompt(language, script),
                    "keyboard": DialogEngine._profile_scope_menu(language, script)
                }

            return {
                "text": DialogEngine._menu_retry(language, script),
                "keyboard": DialogEngine._main_menu(language, script)
            }

        if step == "profile_scope":
            scope = ProfileManager.detect_profile_scope(text)

            if scope == "self":
                StateManager.update_session(
                    user_id,
                    step="birthdata",
                    pending_profile_name=ProfileManager.default_profile_name(language, script)
                )
                return DialogEngine._birth_details_prompt(language, script)

            if scope == "family":
                StateManager.update_session(
                    user_id,
                    step="profile_name"
                )
                return ProfileManager.profile_name_prompt(language, script)

            return {
                "text": ProfileManager.declaration_prompt(language, script),
                "keyboard": DialogEngine._profile_scope_menu(language, script)
            }

        if step == "profile_name":
            profile_name = (text or "").strip()
            if len(profile_name) < 2:
                return ProfileManager.profile_name_prompt(language, script)

            StateManager.update_session(
                user_id,
                pending_profile_name=profile_name,
                step="birthdata"
            )
            return DialogEngine._birth_details_prompt(language, script)

        if step == "birthdata":
            parsed = BirthDataParser.parse_birth_data(text)

            dob = parsed.get("date")
            tob = parsed.get("time")
            place = parsed.get("place")

            if not dob or not tob or not place:
                return DialogEngine._birth_details_prompt(language, script)

            age = AgeCalculator.calculate_age(dob)
            life_stage = LifeStageDetector.detect(age)

            profiles = ProfileManager.parse_profiles(getattr(session, "profiles", None))
            profile_name = str(
                getattr(session, "pending_profile_name", None)
                or ProfileManager.default_profile_name(language, script)
            ).strip()

            max_profiles = ProfileManager.max_profiles(session)
            profile_payload = {
                "name": profile_name,
                "dob": dob,
                "tob": tob,
                "place": place
            }
            profiles, _, limit_exceeded = ProfileManager.upsert_profile(
                profiles=profiles,
                profile=profile_payload,
                limit=max_profiles
            )

            if limit_exceeded:
                return ProfileManager.limit_message(language, script)

            StateManager.update_session(
                user_id,
                dob=dob,
                tob=tob,
                place=place,
                age=age,
                life_stage=life_stage,
                user_goal=None,
                profiles=ProfileManager.serialize_profiles(profiles),
                active_profile_name=profile_name,
                pending_profile_name=None,
                step="question",
                conversation_phase=DialogEngine.STAGE_BIRTHDATA,
                last_domain=None,
                last_followup_question=None,
                chart_data=None
            )

            return {
                "text": DialogEngine._domain_prompt(language, script),
                "keyboard": DialogEngine._domain_menu(language, script)
            }

        if step == "question":
            try:
                chart = DialogEngine.load_chart(user_id, session)
            except Exception:
                return DialogEngine._service_error(language, script)

            try:
                last_domain = getattr(session, "last_domain", None)
                last_followup = getattr(session, "last_followup_question", None)
                domain_from_text = IntentRouter.detect_domain(text)

                target_domain = last_domain
                target_stage = stage

                # Domain switch explicitly restarts only for the new domain.
                if domain_from_text and last_domain and domain_from_text != last_domain:
                    target_domain = domain_from_text
                    target_stage = DialogEngine.STAGE_CHART_READING

                elif stage == DialogEngine.STAGE_BIRTHDATA:
                    if not domain_from_text:
                        return {
                            "text": DialogEngine._domain_not_detected(language, script),
                            "keyboard": DialogEngine._domain_menu(language, script)
                        }
                    target_domain = domain_from_text
                    target_stage = DialogEngine.STAGE_CHART_READING

                elif stage == DialogEngine.STAGE_CHART_READING:
                    target_domain = target_domain or domain_from_text
                    if not target_domain:
                        return {
                            "text": DialogEngine._domain_not_detected(language, script),
                            "keyboard": DialogEngine._domain_menu(language, script)
                        }

                    if FollowupRouter.is_followup_answer(text, last_followup, target_domain):
                        target_stage = DialogEngine.STAGE_SITUATION_ANALYSIS
                    else:
                        target_stage = DialogEngine.STAGE_CHART_READING

                elif stage == DialogEngine.STAGE_SITUATION_ANALYSIS:
                    if not target_domain:
                        target_domain = domain_from_text
                    if not target_domain:
                        return {
                            "text": DialogEngine._domain_not_detected(language, script),
                            "keyboard": DialogEngine._domain_menu(language, script)
                        }
                    target_stage = DialogEngine.STAGE_STRATEGY_GUIDANCE

                elif stage == DialogEngine.STAGE_STRATEGY_GUIDANCE:
                    if not target_domain:
                        target_domain = domain_from_text
                    if not target_domain:
                        return {
                            "text": DialogEngine._domain_not_detected(language, script),
                            "keyboard": DialogEngine._domain_menu(language, script)
                        }
                    target_stage = DialogEngine.STAGE_ACTION_PLAN

                else:
                    if not target_domain:
                        target_domain = domain_from_text
                    if not target_domain:
                        return {
                            "text": DialogEngine._domain_not_detected(language, script),
                            "keyboard": DialogEngine._domain_menu(language, script)
                        }
                    target_stage = DialogEngine.STAGE_ACTION_PLAN

                current_goal = getattr(session, "user_goal", None)
                target_goal = DialogEngine._detect_user_goal(
                    text=text,
                    domain=target_domain,
                    current_goal=current_goal
                )

                reply, new_stage, new_followup_question, introduced_now = DialogEngine._build_consultation_reply(
                    user_id=user_id,
                    text=text,
                    session=session,
                    language=language,
                    script=script,
                    chart=chart,
                    domain=target_domain,
                    stage=target_stage,
                    user_goal=target_goal
                )
            except Exception:
                return DialogEngine._service_error(language, script)

            StateManager.update_session(
                user_id,
                last_domain=target_domain,
                user_goal=target_goal,
                conversation_phase=new_stage,
                last_followup_question=new_followup_question,
                persona_introduced=(bool(getattr(session, "persona_introduced", False)) or introduced_now)
            )

            MemoryEngine.add_bot_message(user_id, reply)
            return reply

        return "Type /start to begin."
