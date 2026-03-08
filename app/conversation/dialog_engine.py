import json
from datetime import datetime

from app.ai import ask_ai
from app.astro_engine import ParashariEngine
from app.conversation.astrologer_persona import AstrologerPersona
from app.conversation.astrology_response_template import AstrologyResponseTemplate
from app.conversation.consultation_engine import ConsultationEngine
from app.conversation.followup_router import FollowupRouter
from app.conversation.intent_router import IntentRouter
from app.conversation.memory_engine import MemoryEngine
from app.conversation.planet_translator import PlanetTranslator
from app.conversation.prompt_builder import AstrologerPrompts
from app.conversation.state_manager import StateManager
from app.conversation.timing_router import TimingRouter
from app.utils.birth_data_parser import BirthDataParser


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

    PHASE_BIRTHDATA = "PHASE_BIRTHDATA"
    PHASE_DOMAIN_ANALYSIS = "PHASE_DOMAIN_ANALYSIS"
    PHASE_CONSULTATION = "PHASE_CONSULTATION"

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
                "कृपया अपनी जन्म जानकारी भेजें:\n"
                "जन्म तिथि\n"
                "जन्म समय\n"
                "जन्म स्थान"
            )

        if DialogEngine._is_hi_rom(language, script):
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
    def load_chart(user_id, session):
        lat = 28.6139
        lon = 77.2090

        if session.chart_data:
            try:
                return json.loads(session.chart_data)
            except Exception:
                pass

        dob, time = DialogEngine.normalize_birth_data(session)
        chart = ParashariEngine.generate_chart(dob, time, lat, lon)

        StateManager.update_session(
            user_id,
            chart_data=json.dumps(chart)
        )
        return chart

    @staticmethod
    def _build_domain_reply(user_id, text, session, language, script, chart, domain):
        domain_data = chart.get("domain_scores", {}).get(domain, {})
        if not domain_data:
            return DialogEngine._domain_not_detected(language, script)

        domain_data = dict(domain_data)
        domain_data["timing_focus"] = bool(TimingRouter.is_timing_question(text))

        prompt = AstrologerPrompts.build_domain_prompt(
            domain=domain,
            domain_data=domain_data,
            language=language,
            script=script,
            user_id=user_id,
            question=text
        )
        prompt = DialogEngine._to_structured_prompt(prompt, language, script)

        raw_output = ask_ai("", prompt)
        llm_fields = DialogEngine._parse_llm_fields(raw_output)

        followup_question = FollowupRouter.get_initial_followup_question(
            domain=domain,
            language=language,
            script=script
        )

        consultation_payload = ConsultationEngine.build_consultation_payload(
            domain=domain,
            domain_data=domain_data,
            llm_fields=llm_fields,
            language=language,
            script=script,
            followup_question=followup_question
        )

        consultation_payload = DialogEngine._translate_payload(
            consultation_payload,
            language,
            script
        )

        reply = AstrologyResponseTemplate.build_response(consultation_payload)

        reply, introduced_now = AstrologerPersona.apply_once(
            reply=reply,
            language=language,
            script=script,
            persona_introduced=bool(getattr(session, "persona_introduced", False))
        )

        StateManager.update_session(
            user_id,
            last_domain=domain,
            conversation_phase=DialogEngine.PHASE_CONSULTATION,
            last_followup_question=followup_question,
            persona_introduced=(bool(getattr(session, "persona_introduced", False)) or introduced_now)
        )

        return reply

    @staticmethod
    def _build_followup_reply(user_id, text, session, language, script, chart, domain):
        domain_data = chart.get("domain_scores", {}).get(domain, {})
        if not domain_data:
            return DialogEngine._domain_not_detected(language, script)

        domain_data = dict(domain_data)
        domain_data["timing_focus"] = bool(TimingRouter.is_timing_question(text))

        focus = FollowupRouter.detect_followup_focus(domain, text)

        prompt = FollowupRouter.build_deeper_prompt(
            domain=domain,
            domain_data=domain_data,
            language=language,
            script=script,
            user_id=user_id,
            user_text=text,
            focus=focus
        )
        prompt = DialogEngine._to_structured_prompt(prompt, language, script)

        raw_output = ask_ai("", prompt)
        llm_fields = DialogEngine._parse_llm_fields(raw_output)

        next_followup = FollowupRouter.get_next_followup_question(
            domain=domain,
            focus=focus,
            language=language,
            script=script,
            previous_question=getattr(session, "last_followup_question", None)
        )

        consultation_payload = ConsultationEngine.build_consultation_payload(
            domain=domain,
            domain_data=domain_data,
            llm_fields=llm_fields,
            language=language,
            script=script,
            followup_question=next_followup
        )

        consultation_payload = DialogEngine._translate_payload(
            consultation_payload,
            language,
            script
        )

        reply = AstrologyResponseTemplate.build_response(consultation_payload)

        reply, introduced_now = AstrologerPersona.apply_once(
            reply=reply,
            language=language,
            script=script,
            persona_introduced=bool(getattr(session, "persona_introduced", False))
        )

        StateManager.update_session(
            user_id,
            conversation_phase=DialogEngine.PHASE_CONSULTATION,
            last_followup_question=next_followup,
            last_domain=domain,
            persona_introduced=(bool(getattr(session, "persona_introduced", False)) or introduced_now)
        )

        return reply

    @staticmethod
    def process(user_id, text, session):
        MemoryEngine.add_user_message(user_id, text)

        session = StateManager.get_or_create_session(user_id)
        language, script = DialogEngine._language_values(session)
        step = getattr(session, "step", "start")
        phase = getattr(session, "conversation_phase", None) or DialogEngine.PHASE_BIRTHDATA

        if text == "/start":
            StateManager.update_session(
                user_id,
                step="language",
                language=None,
                script=None,
                last_domain=None,
                last_followup_question=None,
                conversation_phase=DialogEngine.PHASE_BIRTHDATA,
                persona_introduced=False
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
                    conversation_phase=DialogEngine.PHASE_BIRTHDATA
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
                    conversation_phase=DialogEngine.PHASE_BIRTHDATA
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
                    conversation_phase=DialogEngine.PHASE_BIRTHDATA
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
                    conversation_phase=DialogEngine.PHASE_BIRTHDATA
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
                    step="birthdata",
                    conversation_phase=DialogEngine.PHASE_BIRTHDATA,
                    last_domain=None,
                    last_followup_question=None
                )
                return DialogEngine._birth_details_prompt(language, script)

            return {
                "text": DialogEngine._menu_retry(language, script),
                "keyboard": DialogEngine._main_menu(language, script)
            }

        if step == "birthdata":
            parsed = BirthDataParser.parse_birth_data(text)

            dob = parsed.get("date")
            tob = parsed.get("time")
            place = parsed.get("place")

            if not dob or not tob or not place:
                return DialogEngine._birth_details_prompt(language, script)

            StateManager.update_session(
                user_id,
                dob=dob,
                tob=tob,
                place=place,
                step="question",
                conversation_phase=DialogEngine.PHASE_DOMAIN_ANALYSIS,
                last_domain=None,
                last_followup_question=None
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

                if (
                    phase == DialogEngine.PHASE_CONSULTATION
                    and last_domain
                    and FollowupRouter.is_followup_answer(text, last_followup, last_domain)
                ):
                    reply = DialogEngine._build_followup_reply(
                        user_id=user_id,
                        text=text,
                        session=session,
                        language=language,
                        script=script,
                        chart=chart,
                        domain=last_domain
                    )
                else:
                    domain = IntentRouter.detect_domain(text)

                    if not domain:
                        if phase == DialogEngine.PHASE_CONSULTATION and last_domain:
                            reply = DialogEngine._build_followup_reply(
                                user_id=user_id,
                                text=text,
                                session=session,
                                language=language,
                                script=script,
                                chart=chart,
                                domain=last_domain
                            )
                        else:
                            return {
                                "text": DialogEngine._domain_not_detected(language, script),
                                "keyboard": DialogEngine._domain_menu(language, script)
                            }
                    else:
                        reply = DialogEngine._build_domain_reply(
                            user_id=user_id,
                            text=text,
                            session=session,
                            language=language,
                            script=script,
                            chart=chart,
                            domain=domain
                        )
            except Exception:
                return DialogEngine._service_error(language, script)

            MemoryEngine.add_bot_message(user_id, reply)
            return reply

        return "Type /start to begin."
