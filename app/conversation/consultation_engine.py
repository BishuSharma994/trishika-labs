import hashlib
import json

from app.conversation.intent_router import IntentRouter
from app.conversation.life_translation_engine import translate_to_life_guidance
from app.conversation.persona_layer import PersonaLayer


class ConsultationEngine:

    CONSULT_STAGES = {
        1: "observation",
        2: "explanation",
        3: "timing",
        4: "action",
        5: "remedy",
    }

    INTENT_STAGE_MAP = {
        "detail": 2,
        "timing": 3,
        "instruction": 4,
        "remedy": 5,
    }

    START = "START"
    COLLECT_BIRTHDATA = "COLLECT_BIRTHDATA"
    TOPIC_SELECTION = "TOPIC_SELECTION"
    SUBTOPIC_SELECTION = "SUBTOPIC_SELECTION"
    ANALYSIS = CONSULT_STAGES[1]
    EXPLANATION = CONSULT_STAGES[2]
    TIMING = CONSULT_STAGES[3]
    GUIDANCE = CONSULT_STAGES[4]
    REMEDY = CONSULT_STAGES[5]

    DOMAIN_ENTRY = TOPIC_SELECTION
    STATUS_CAPTURE = SUBTOPIC_SELECTION
    DIAGNOSTIC = ANALYSIS
    ACTION_PLAN = REMEDY

    VALID_STATES = set(CONSULT_STAGES.values()) | {
        START,
        COLLECT_BIRTHDATA,
        TOPIC_SELECTION,
        SUBTOPIC_SELECTION,
    }

    KNOWN_PLANETS = {"Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"}

    @staticmethod
    def _default_state(language="english"):
        return {
            "step": "consult",
            "topic": None,
            "dob": None,
            "time": None,
            "place": None,
            "gender": None,
            "name": None,
            "consult_stage": 1,
            "last_response": "",
            "language": language or "english",
        }

    @staticmethod
    def hash_response(text):
        value = str(text or "")
        return hashlib.md5(value.encode("utf-8")).hexdigest()

    @staticmethod
    def _clamp_stage(stage):
        try:
            value = int(stage)
        except Exception:
            value = 1
        if value < 1:
            return 1
        if value > 5:
            return 5
        return value

    @staticmethod
    def _stage_from_legacy(parsed):
        if not isinstance(parsed, dict):
            return 1

        if parsed.get("consult_stage") is not None:
            return ConsultationEngine._clamp_stage(parsed.get("consult_stage"))

        if parsed.get("depth") is not None:
            return ConsultationEngine._clamp_stage(parsed.get("depth"))

        state_name = str(parsed.get("state") or "").strip().lower()
        for number, label in ConsultationEngine.CONSULT_STAGES.items():
            if state_name == label:
                return number

        legacy_map = {
            "analysis": 1,
            "diagnostic": 1,
            "timing": 3,
            "guidance": 4,
            "remedy": 5,
            "action_plan": 5,
        }
        return legacy_map.get(state_name, 1)

    @staticmethod
    def load_state(blob):
        base = ConsultationEngine._default_state()
        if not blob:
            return dict(base)

        try:
            parsed = json.loads(blob)
        except Exception:
            return dict(base)

        if not isinstance(parsed, dict):
            return dict(base)

        state = dict(base)
        state["step"] = parsed.get("step") or "consult"
        state["topic"] = parsed.get("topic") or parsed.get("domain")
        state["dob"] = parsed.get("dob")
        state["time"] = parsed.get("time") or parsed.get("tob")
        state["place"] = parsed.get("place")
        state["gender"] = parsed.get("gender")
        state["name"] = parsed.get("name") or parsed.get("active_profile_name")
        state["consult_stage"] = ConsultationEngine._stage_from_legacy(parsed)
        state["last_response"] = str(parsed.get("last_response") or "")
        state["language"] = parsed.get("language") or parsed.get("language_mode") or base["language"]
        return state

    @staticmethod
    def dump_state(state):
        payload = dict(ConsultationEngine._default_state(language=state.get("language")))
        payload.update(state or {})
        payload["consult_stage"] = ConsultationEngine._clamp_stage(payload.get("consult_stage"))
        return json.dumps(payload, ensure_ascii=False)

    @staticmethod
    def bootstrap_state(language, flow_state=None):
        state = ConsultationEngine._default_state(language=language)
        if flow_state in ConsultationEngine.CONSULT_STAGES.values():
            for number, label in ConsultationEngine.CONSULT_STAGES.items():
                if label == flow_state:
                    state["consult_stage"] = number
                    break
        return ConsultationEngine.dump_state(state)

    @staticmethod
    def move_state(blob, flow_state, language=None, topic=None, subtopic=None, reset_depth=False):
        state = ConsultationEngine.load_state(blob)
        if language:
            state["language"] = language
        if topic is not None:
            state["topic"] = topic
        if reset_depth:
            state["consult_stage"] = 1
            state["last_response"] = ""
        if flow_state in ConsultationEngine.CONSULT_STAGES.values():
            for number, label in ConsultationEngine.CONSULT_STAGES.items():
                if label == flow_state:
                    state["consult_stage"] = number
                    break
        return ConsultationEngine.dump_state(state)

    @staticmethod
    def reset_language(blob, language):
        state = ConsultationEngine.load_state(blob)
        if language:
            state["language"] = language
            state["consult_stage"] = 1
            state["last_response"] = ""
        return ConsultationEngine.dump_state(state)

    @staticmethod
    def prime_state(
        session_state_blob=None,
        language="english",
        topic=None,
        dob=None,
        time=None,
        place=None,
        gender=None,
        name=None,
    ):
        state = ConsultationEngine.load_state(session_state_blob)
        if language:
            state["language"] = language
        if topic is not None:
            state["topic"] = topic
        if dob is not None:
            state["dob"] = dob
        if time is not None:
            state["time"] = time
        if place is not None:
            state["place"] = place
        if gender is not None:
            state["gender"] = gender
        if name is not None:
            state["name"] = name
        return ConsultationEngine.dump_state(state)

    @staticmethod
    def _normalize_planet(planet, fallback):
        value = str(planet or "").strip().title()
        if value in ConsultationEngine.KNOWN_PLANETS:
            return value
        return str(fallback or "Moon").strip().title()

    @staticmethod
    def _safe_int(value, default):
        try:
            return int(value)
        except Exception:
            return default

    @staticmethod
    def _build_analysis_payload(domain, domain_data, current_dasha):
        targets = IntentRouter.get_astrology_targets(domain)
        target_planets = list(targets.get("target_planets") or ["Moon", "Saturn"])
        fallback_primary = target_planets[0]
        fallback_risk = target_planets[1] if len(target_planets) > 1 else fallback_primary

        data = domain_data or {}
        score = ConsultationEngine._safe_int(data.get("score"), 55)
        projection = ConsultationEngine._safe_int(data.get("projection_next_year"), score)

        return {
            "planet": ConsultationEngine._normalize_planet(data.get("primary_driver"), fallback_primary),
            "risk_planet": ConsultationEngine._normalize_planet(data.get("risk_factor"), fallback_risk),
            "score": score,
            "projection": projection,
            "current_dasha": current_dasha or data.get("current_dasha") or {},
        }

    @staticmethod
    def _intent_value(normalized_intent, user_text):
        if isinstance(normalized_intent, dict):
            return normalized_intent.get("intent") or "general"
        if isinstance(normalized_intent, str):
            return normalized_intent
        return IntentRouter.normalize_intent(user_text).get("intent") or "general"

    @staticmethod
    def _select_stage(state, intent):
        next_stage = ConsultationEngine._clamp_stage(state.get("consult_stage", 1))
        mapped_stage = ConsultationEngine.INTENT_STAGE_MAP.get(intent)
        if mapped_stage is None:
            return next_stage
        return ConsultationEngine._clamp_stage(max(next_stage, mapped_stage))

    @staticmethod
    def _render_response(state, analysis_payload, language, script, intent, stage, variant=0):
        guidance = translate_to_life_guidance(
            analysis=analysis_payload,
            topic=state.get("topic"),
            consult_stage=stage,
            language=language,
            intent=intent,
            variant=variant,
        )
        return PersonaLayer.format_guidance(
            guidance=guidance,
            language=language,
            script=script,
            intent=intent,
        )

    @staticmethod
    def _validated_response(state, analysis_payload, language, script, intent):
        base_stage = ConsultationEngine._select_stage(state, intent)
        last_response = str(state.get("last_response") or "").strip()

        for stage in range(base_stage, 6):
            for variant in (0, 1):
                text = ConsultationEngine._render_response(
                    state=state,
                    analysis_payload=analysis_payload,
                    language=language,
                    script=script,
                    intent=intent,
                    stage=stage,
                    variant=variant,
                )

                if not PersonaLayer.validate_response(text, topic=state.get("topic"), intent=intent):
                    continue

                if text == last_response and stage < 5 and variant == 0:
                    continue

                return text, stage

        fallback_stage = 5
        fallback_text = ConsultationEngine._render_response(
            state=state,
            analysis_payload=analysis_payload,
            language=language,
            script=script,
            intent=intent,
            stage=fallback_stage,
            variant=1,
        )
        return fallback_text, fallback_stage

    @staticmethod
    def detect_domain(text, current_domain=None):
        return IntentRouter.detect_domain(text, current_domain=current_domain)

    @staticmethod
    def score_domain(domain):
        return domain if domain in {"career", "finance", "health", "marriage"} else None

    @staticmethod
    def generate_response(
        domain,
        domain_data,
        language,
        script,
        stage,
        age,
        life_stage,
        user_goal,
        current_dasha,
        transits,
        persona_introduced=False,
        chart=None,
        theme_shown=False,
        user_text="",
        session_state_blob=None,
        domain_switched=False,
        normalized_intent=None,
    ):
        state = ConsultationEngine.load_state(session_state_blob)
        state["language"] = language or state.get("language") or "english"

        detected_domain = domain or IntentRouter.detect_domain(user_text, current_domain=state.get("topic"))
        if detected_domain and (domain_switched or detected_domain != state.get("topic")):
            state["topic"] = detected_domain
            state["consult_stage"] = 1
            state["last_response"] = ""
        elif detected_domain and not state.get("topic"):
            state["topic"] = detected_domain

        if not state.get("topic"):
            state["topic"] = "career"

        intent = ConsultationEngine._intent_value(normalized_intent, user_text)
        analysis_payload = ConsultationEngine._build_analysis_payload(
            domain=state.get("topic"),
            domain_data=domain_data,
            current_dasha=current_dasha,
        )

        text, used_stage = ConsultationEngine._validated_response(
            state=state,
            analysis_payload=analysis_payload,
            language=state["language"],
            script=script,
            intent=intent,
        )

        state["consult_stage"] = ConsultationEngine._clamp_stage(used_stage + 1)
        state["last_response"] = text

        return {
            "text": text,
            "next_stage": ConsultationEngine.CONSULT_STAGES[used_stage],
            "state_blob": ConsultationEngine.dump_state(state),
        }
