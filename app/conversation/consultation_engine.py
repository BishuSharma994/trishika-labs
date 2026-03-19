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
        "definition": 2,
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

    MODE_ANALYSIS = "analysis"
    MODE_FOLLOWUP = "followup"

    VALID_STATES = set(CONSULT_STAGES.values()) | {
        START,
        COLLECT_BIRTHDATA,
        TOPIC_SELECTION,
        SUBTOPIC_SELECTION,
    }

    KNOWN_PLANETS = {"Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"}

    PLANET_DEFINITIONS = {
        "Sun": {
            "en": [
                "Sun is the planet of authority and confidence.",
                "Sun also shows leadership, recognition, and self-direction.",
            ],
            "hi": [
                "Sun authority aur confidence ka grah hai.",
                "Sun leadership, recognition aur self-direction ko bhi dikhata hai.",
            ],
        },
        "Moon": {
            "en": [
                "Moon represents emotions and the mind.",
                "Moon also shows mood, comfort, and mental reactions.",
            ],
            "hi": [
                "Moon emotions aur mind ko represent karta hai.",
                "Moon mood, comfort aur mental reactions ko bhi dikhata hai.",
            ],
        },
        "Mars": {
            "en": [
                "Mars is the planet of action and decision making.",
                "Mars also shows drive, speed, and direct reactions.",
            ],
            "hi": [
                "Mars action aur decision making ka grah hai.",
                "Mars drive, speed aur direct reactions ko bhi dikhata hai.",
            ],
        },
        "Mercury": {
            "en": [
                "Mercury is the planet of communication and planning.",
                "Mercury also shows analysis, trade, and practical thinking.",
            ],
            "hi": [
                "Mercury communication aur planning ka grah hai.",
                "Mercury analysis, trade aur practical thinking ko bhi dikhata hai.",
            ],
        },
        "Jupiter": {
            "en": [
                "Jupiter is the planet of growth and opportunity.",
                "Jupiter also shows wisdom, expansion, and support.",
            ],
            "hi": [
                "Jupiter growth aur opportunity ka grah hai.",
                "Jupiter wisdom, expansion aur support ko bhi dikhata hai.",
            ],
        },
        "Venus": {
            "en": [
                "Venus is the planet of relationships and attraction.",
                "Venus also shows comfort, pleasure, and what you value.",
            ],
            "hi": [
                "Venus relationships aur attraction ko control karta hai.",
                "Venus comfort, pleasure aur values ko bhi dikhata hai.",
            ],
        },
        "Saturn": {
            "en": [
                "Saturn is the planet of discipline and delay.",
                "Saturn also shows pressure, responsibility, and long-term effort.",
            ],
            "hi": [
                "Saturn discipline aur delay ka grah hai.",
                "Saturn pressure, responsibility aur long-term effort ko bhi dikhata hai.",
            ],
        },
        "Rahu": {
            "en": [
                "Rahu shows obsession, ambition, and unusual focus.",
                "Rahu also shows urgency, confusion, and risk-taking.",
            ],
            "hi": [
                "Rahu obsession, ambition aur unusual focus ko dikhata hai.",
                "Rahu urgency, confusion aur risk-taking ko bhi dikhata hai.",
            ],
        },
        "Ketu": {
            "en": [
                "Ketu shows detachment and internal processing.",
                "Ketu also shows withdrawal, reflection, and separation.",
            ],
            "hi": [
                "Ketu detachment aur internal processing ko dikhata hai.",
                "Ketu withdrawal, reflection aur separation ko bhi dikhata hai.",
            ],
        },
    }

    DETAIL_LINES = {
        "career": {
            "en": [
                "In career, this affects work decisions, consistency, and progress.",
                "In career, this shows up through workload, discipline, and job direction.",
            ],
            "hi": [
                "Career mein yeh work decisions, consistency aur progress ko affect karta hai.",
                "Career mein yeh workload, discipline aur job direction par dikhta hai.",
            ],
        },
        "finance": {
            "en": [
                "In finance, this shows up through spending, savings, and budget control.",
                "In finance, this affects purchases, savings discipline, and money decisions.",
            ],
            "hi": [
                "Finance mein yeh spending, savings aur budget control par dikhta hai.",
                "Finance mein yeh purchases, savings discipline aur money decisions ko affect karta hai.",
            ],
        },
        "health": {
            "en": [
                "In health, this affects stress, routine, and recovery.",
                "In health, this shows up through sleep, stamina, and consistency.",
            ],
            "hi": [
                "Health mein yeh stress, routine aur recovery ko affect karta hai.",
                "Health mein yeh sleep, stamina aur consistency par dikhta hai.",
            ],
        },
        "marriage": {
            "en": [
                "In marriage, this affects reactions, expectations, and clarity.",
                "In marriage, this shows up through communication, commitment, and emotional response.",
            ],
            "hi": [
                "Shaadi mein yeh reactions, expectations aur clarity ko affect karta hai.",
                "Shaadi mein yeh communication, commitment aur emotional response par dikhta hai.",
            ],
        },
    }

    FOLLOWUP_TYPE_ORDER = {
        "definition": ["definition", "detail", "timing", "instruction"],
        "instruction": ["instruction", "detail", "definition", "timing"],
        "timing": ["timing", "detail", "definition", "instruction"],
        "detail": ["detail", "definition", "timing", "instruction"],
        "general": ["detail", "definition", "timing", "instruction"],
    }

    NEXT_STAGE_MAP = {
        MODE_ANALYSIS: ANALYSIS,
        "definition": EXPLANATION,
        "detail": EXPLANATION,
        "timing": TIMING,
        "instruction": GUIDANCE,
        "remedy": REMEDY,
    }

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
            "mode": ConsultationEngine.MODE_ANALYSIS,
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
    def _language_key(language):
        return "hi" if str(language or "").strip().lower() == "hindi_roman" else "en"

    @staticmethod
    def _localized(values, language, variant=0):
        key = ConsultationEngine._language_key(language)
        entries = list(values.get(key) or values.get("en") or [])
        if not entries:
            return ""
        index = 0 if variant <= 0 else min(variant, len(entries) - 1)
        return str(entries[index]).strip()

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
    def _mode_from_legacy(parsed):
        if not isinstance(parsed, dict):
            return ConsultationEngine.MODE_ANALYSIS

        mode = str(parsed.get("mode") or "").strip().lower()
        if mode in {ConsultationEngine.MODE_ANALYSIS, ConsultationEngine.MODE_FOLLOWUP}:
            return mode

        if parsed.get("last_response"):
            return ConsultationEngine.MODE_FOLLOWUP

        return ConsultationEngine.MODE_ANALYSIS

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
        state["mode"] = ConsultationEngine._mode_from_legacy(parsed)
        return state

    @staticmethod
    def dump_state(state):
        payload = dict(ConsultationEngine._default_state(language=state.get("language")))
        payload.update(state or {})
        payload["consult_stage"] = ConsultationEngine._clamp_stage(payload.get("consult_stage"))
        if payload.get("mode") not in {ConsultationEngine.MODE_ANALYSIS, ConsultationEngine.MODE_FOLLOWUP}:
            payload["mode"] = ConsultationEngine.MODE_ANALYSIS
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
            state["mode"] = ConsultationEngine.MODE_ANALYSIS
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
            state["mode"] = ConsultationEngine.MODE_ANALYSIS
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
    def _analysis_response(state, analysis_payload, language, script):
        for stage in (1, 2):
            for variant in (0, 1):
                guidance = translate_to_life_guidance(
                    analysis=analysis_payload,
                    topic=state.get("topic"),
                    consult_stage=stage,
                    language=language,
                    intent="general",
                    variant=variant,
                )
                text = PersonaLayer.format_guidance(
                    guidance=guidance,
                    language=language,
                    script=script,
                    intent="general",
                )
                if not PersonaLayer.validate_response(text, topic=state.get("topic"), intent="general"):
                    continue
                if text == state.get("last_response"):
                    continue
                return text

        guidance = translate_to_life_guidance(
            analysis=analysis_payload,
            topic=state.get("topic"),
            consult_stage=1,
            language=language,
            intent="general",
            variant=0,
        )
        return PersonaLayer.format_guidance(
            guidance=guidance,
            language=language,
            script=script,
            intent="general",
        )

    @staticmethod
    def _time_window(analysis_payload, language, variant=0):
        score = ConsultationEngine._safe_int(analysis_payload.get("score"), 55)
        projection = ConsultationEngine._safe_int(analysis_payload.get("projection"), score)
        planet = ConsultationEngine._normalize_planet(analysis_payload.get("planet"), "Moon")
        risk_planet = ConsultationEngine._normalize_planet(analysis_payload.get("risk_planet"), "Saturn")
        current_dasha = analysis_payload.get("current_dasha") or {}

        pace = score + max(-6, min(6, projection - score))
        dasha_values = {
            str(value or "").strip().title()
            for value in current_dasha.values()
            if str(value or "").strip()
        }
        if planet in dasha_values:
            pace += 5
        if risk_planet in dasha_values:
            pace -= 5

        if pace >= 72:
            window = "2-3 weeks" if ConsultationEngine._language_key(language) == "en" else "2-3 hafte"
        elif pace >= 60:
            window = "3-4 weeks" if ConsultationEngine._language_key(language) == "en" else "3-4 hafte"
        elif pace >= 48:
            window = "4-6 weeks" if ConsultationEngine._language_key(language) == "en" else "4-6 hafte"
        else:
            window = "6-8 weeks" if ConsultationEngine._language_key(language) == "en" else "6-8 hafte"

        if variant == 0:
            return window

        if ConsultationEngine._language_key(language) == "en":
            return f"Around {window}"
        return f"Lagbhag {window}"

    @staticmethod
    def _definition_response(user_text, analysis_payload, language, variant=0):
        planet = IntentRouter.detect_planet(user_text, fallback=analysis_payload.get("planet"))
        planet = ConsultationEngine._normalize_planet(planet, analysis_payload.get("planet"))
        definitions = ConsultationEngine.PLANET_DEFINITIONS.get(planet, ConsultationEngine.PLANET_DEFINITIONS["Moon"])
        return ConsultationEngine._localized(definitions, language, variant=variant)

    @staticmethod
    def _instruction_response(state, analysis_payload, language, variant=0):
        consult_stage = 4 if variant == 0 else 5
        guidance = translate_to_life_guidance(
            analysis=analysis_payload,
            topic=state.get("topic"),
            consult_stage=consult_stage,
            language=language,
            intent="instruction",
            variant=variant,
        )
        steps = []
        for index, action in enumerate(guidance.get("actions") or [], start=1):
            cleaned = str(action or "").strip()
            if cleaned:
                steps.append(f"{index}. {cleaned}")
        return "\n".join(steps[:3]).strip()

    @staticmethod
    def _detail_response(state, user_text, analysis_payload, language, variant=0):
        planet = IntentRouter.detect_planet(user_text, fallback=analysis_payload.get("planet"))
        planet = ConsultationEngine._normalize_planet(planet, analysis_payload.get("planet"))
        topic = str(state.get("topic") or "career").strip().lower()
        definition_line = ConsultationEngine._definition_response(user_text, analysis_payload, language, variant=variant)
        detail_payload = ConsultationEngine.DETAIL_LINES.get(topic, ConsultationEngine.DETAIL_LINES["career"])
        detail_line = ConsultationEngine._localized(detail_payload, language, variant=variant)

        if ConsultationEngine._language_key(language) == "en":
            if variant == 0:
                return f"{definition_line}\nRight now {planet} matters because {detail_line.lower()}"
            return f"{definition_line}\nThis is why {detail_line.lower()}"

        if variant == 0:
            return f"{definition_line}\nAbhi {planet} important hai kyunki {detail_line.lower()}"
        return f"{definition_line}\nIsi wajah se {detail_line.lower()}"

    @staticmethod
    def _timing_response(analysis_payload, language, variant=0):
        return ConsultationEngine._time_window(analysis_payload, language, variant=variant)

    @staticmethod
    def _render_followup(response_type, state, user_text, analysis_payload, language, variant=0):
        if response_type == "definition":
            return ConsultationEngine._definition_response(user_text, analysis_payload, language, variant=variant)
        if response_type == "instruction":
            return ConsultationEngine._instruction_response(state, analysis_payload, language, variant=variant)
        if response_type == "timing":
            return ConsultationEngine._timing_response(analysis_payload, language, variant=variant)
        return ConsultationEngine._detail_response(state, user_text, analysis_payload, language, variant=variant)

    @staticmethod
    def _followup_type_order(intent):
        normalized_intent = intent if intent in ConsultationEngine.FOLLOWUP_TYPE_ORDER else "general"
        return ConsultationEngine.FOLLOWUP_TYPE_ORDER[normalized_intent]

    @staticmethod
    def _followup_response(state, user_text, analysis_payload, language, intent):
        last_response = str(state.get("last_response") or "").strip()

        for response_type in ConsultationEngine._followup_type_order(intent):
            for variant in (0, 1):
                text = ConsultationEngine._render_followup(
                    response_type=response_type,
                    state=state,
                    user_text=user_text,
                    analysis_payload=analysis_payload,
                    language=language,
                    variant=variant,
                )
                if not text:
                    continue
                if text == last_response:
                    continue
                return text, response_type

        fallback_type = ConsultationEngine._followup_type_order(intent)[-1]
        fallback_text = ConsultationEngine._render_followup(
            response_type=fallback_type,
            state=state,
            user_text=user_text,
            analysis_payload=analysis_payload,
            language=language,
            variant=1,
        )
        return fallback_text, fallback_type

    @staticmethod
    def _next_consult_stage(current_stage, response_type):
        current_stage = ConsultationEngine._clamp_stage(current_stage)
        if response_type == ConsultationEngine.MODE_ANALYSIS:
            return 2
        if response_type == "definition":
            return max(current_stage, 2)
        if response_type == "detail":
            return ConsultationEngine._clamp_stage(max(current_stage, 2) + 1)
        if response_type == "timing":
            return max(current_stage, 3)
        if response_type == "instruction":
            return max(current_stage, 4)
        return current_stage

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
            state["mode"] = ConsultationEngine.MODE_ANALYSIS
        elif detected_domain and not state.get("topic"):
            state["topic"] = detected_domain

        if not state.get("topic"):
            state["topic"] = "career"

        analysis_payload = ConsultationEngine._build_analysis_payload(
            domain=state.get("topic"),
            domain_data=domain_data,
            current_dasha=current_dasha,
        )

        if state.get("mode") != ConsultationEngine.MODE_FOLLOWUP:
            text = ConsultationEngine._analysis_response(
                state=state,
                analysis_payload=analysis_payload,
                language=state["language"],
                script=script,
            )
            state["mode"] = ConsultationEngine.MODE_FOLLOWUP
            state["consult_stage"] = ConsultationEngine._next_consult_stage(
                state.get("consult_stage", 1),
                ConsultationEngine.MODE_ANALYSIS,
            )
            state["last_response"] = text
            return {
                "text": text,
                "next_stage": ConsultationEngine.NEXT_STAGE_MAP[ConsultationEngine.MODE_ANALYSIS],
                "state_blob": ConsultationEngine.dump_state(state),
            }

        intent = ConsultationEngine._intent_value(normalized_intent, user_text)
        if intent not in {"definition", "instruction", "timing", "detail"}:
            intent = "general"

        text, used_type = ConsultationEngine._followup_response(
            state=state,
            user_text=user_text,
            analysis_payload=analysis_payload,
            language=state["language"],
            intent=intent,
        )

        state["mode"] = ConsultationEngine.MODE_FOLLOWUP
        state["consult_stage"] = ConsultationEngine._next_consult_stage(
            state.get("consult_stage", 1),
            used_type,
        )
        state["last_response"] = text

        return {
            "text": text,
            "next_stage": ConsultationEngine.NEXT_STAGE_MAP.get(used_type, ConsultationEngine.EXPLANATION),
            "state_blob": ConsultationEngine.dump_state(state),
        }
