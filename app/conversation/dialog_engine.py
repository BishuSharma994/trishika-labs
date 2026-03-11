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


class DialogEngine:

    # ------------------------------------------------------------------

    @staticmethod
    def load_chart(user_id, session):

        dob = session.dob
        tob = session.tob
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

        language = session.language or "en"
        script = getattr(session, "script", None) or "latin"

        # --------------------------------------------------------------
        # START
        # --------------------------------------------------------------

        if text == "/start":

            StateManager.update_session(
                user_id,
                step="language",
                language=None,
                script=None,
                language_mode=None,
                language_confirmed=False,
                last_domain=None,
                conversation_phase=ConsultationEngine.DOMAIN_ENTRY,
                language_state_blob=None,
                consultation_state_blob=None,
                chart_data=None,
            )

            MemoryEngine.clear(user_id)

            return {
                "text": "Please select your language\n\nकृपया अपनी भाषा चुनें",
                "keyboard": {
                    "keyboard": [["English"], ["हिंदी"], ["Hindi (Roman)"]],
                    "resize_keyboard": True,
                },
            }

        # --------------------------------------------------------------
        # LANGUAGE CHECK
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

            if update:
                StateManager.update_session(user_id, **update)

                for k, v in update.items():
                    setattr(session, k, v)

            if language_result.get("response"):

                reply = language_result["response"]

                MemoryEngine.add_bot_message(user_id, reply)

                return reply

        # --------------------------------------------------------------
        # PROFILE FLOW
        # --------------------------------------------------------------

        if session.step == "birthdata":

            parsed = BirthDataParser.parse_birth_data(text)

            dob = parsed.get("date")
            tob = parsed.get("time")
            place = parsed.get("place")

            if not dob or not tob or not place:
                return "Please send date, time and place."

            age = calculate_age(dob)

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

            return "What area would you like to explore?"

        # --------------------------------------------------------------
        # MAIN CONSULTATION
        # --------------------------------------------------------------

        if session.step == "question":

            last_domain = getattr(session, "last_domain", None)

            # domain detection
            domain = DomainRouter.detect(text, current_domain=last_domain)

            if not domain and not last_domain:
                return "Please choose a topic like career, marriage, finance or health."

            if not domain:
                domain = last_domain

            current_stage = (
                getattr(session, "conversation_phase", None)
                or ConsultationEngine.DOMAIN_ENTRY
            )

            chart = DialogEngine.load_chart(user_id, session)

            score_domain = ConsultationEngine.score_domain(domain) or domain

            domain_data = dict(chart.get("domain_scores", {}).get(score_domain, {}))

            domain_data["timing_focus"] = bool(
                TimingRouter.is_timing_question(text)
            )

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

            reply = PlanetTranslator.translate(reply, language, script)

            reply = LanguageEngine.enforce_response_language(session, reply)

            next_stage = ConsultationController.next_stage(current_stage)

            StateManager.update_session(
                user_id,
                last_domain=domain,
                conversation_phase=next_stage,
                consultation_state_blob=consultation.get("state_blob"),
            )

            MemoryEngine.add_bot_message(user_id, reply)

            return reply

        return "Type /start to begin."