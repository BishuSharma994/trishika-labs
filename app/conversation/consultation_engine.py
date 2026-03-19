import hashlib
import json
import re

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
        "clarification": 2,
        "detail": 2,
        "context_update": 2,
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
    TIMEFRAME_HINTS = ("day", "days", "week", "weeks", "month", "months", "hafta", "hafte", "mahina", "mahine")
    TEMPLATE_LABELS = ("observation:", "cause:", "action:", "timeframe:")

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

    OUTCOME_LINES = {
        "career": {
            "en": [
                "This improves consistency at work, reduces avoidable mistakes, and makes progress easier to track.",
                "This brings clearer work priorities, steadier output, and better control over delays.",
            ],
            "hi": [
                "Isse kaam mein consistency badhegi, avoidable mistakes kam hongi, aur progress track karna aasaan hoga.",
                "Isse work priorities clear hongi, output steady hoga, aur delays par zyada control aayega.",
            ],
        },
        "finance": {
            "en": [
                "This improves spending control, protects savings, and reduces regret purchases.",
                "This brings steadier budgeting, better savings discipline, and fewer money leaks.",
            ],
            "hi": [
                "Isse spending control better hoga, savings protect hongi, aur regret purchases kam hongi.",
                "Isse budgeting steady hogi, savings discipline improve hogi, aur money leaks kam honge.",
            ],
        },
        "health": {
            "en": [
                "This improves routine stability, reduces stress spikes, and supports steadier recovery.",
                "This brings better sleep discipline, calmer daily rhythm, and fewer health setbacks.",
            ],
            "hi": [
                "Isse routine stability improve hogi, stress spikes kam honge, aur recovery zyada steady hogi.",
                "Isse sleep discipline better hogi, daily rhythm calmer hoga, aur health setbacks kam honge.",
            ],
        },
        "marriage": {
            "en": [
                "This improves communication, reduces quick conflicts, and brings more clarity in expectations.",
                "This brings calmer conversations, better emotional control, and more stability in the relationship.",
            ],
            "hi": [
                "Isse communication improve hogi, quick conflicts kam honge, aur expectations mein clarity aayegi.",
                "Isse conversations calmer hongi, emotional control better hoga, aur relationship mein stability badhegi.",
            ],
        },
    }

    CONTEXT_ADJUSTMENTS = {
        "career": {
            "en": [
                "Understood. I would adjust this toward stabilizing your current work pattern, not restarting your direction.",
                "Understood. The focus should shift to improving consistency in the role you already have.",
            ],
            "hi": [
                "Samajh gaya. Isse aapke current work pattern ko stable karne par focus hoga, direction restart karne par nahi.",
                "Samajh gaya. Focus ab us role mein consistency improve karne par hona chahiye jo aap already kar rahe hain.",
            ],
        },
        "finance": {
            "en": [
                "Understood. I would adjust this toward protecting what is already working and tightening spending control.",
                "Understood. The focus should shift to refining your current budget, not starting from zero.",
            ],
            "hi": [
                "Samajh gaya. Isse jo already sahi chal raha hai usko protect karne aur spending control tight karne par focus hoga.",
                "Samajh gaya. Focus ab current budget ko refine karne par hona chahiye, zero se shuru karne par nahi.",
            ],
        },
        "health": {
            "en": [
                "Understood. I would adjust this toward making your existing routine more consistent, not replacing it fully.",
                "Understood. The focus should shift to reducing setbacks inside your current health routine.",
            ],
            "hi": [
                "Samajh gaya. Isse aapki existing routine ko zyada consistent banane par focus hoga, usko poori tarah replace karne par nahi.",
                "Samajh gaya. Focus ab current health routine ke andar setbacks kam karne par hona chahiye.",
            ],
        },
        "marriage": {
            "en": [
                "Understood. I would adjust this toward improving the current relationship dynamic, not treating it like a fresh start.",
                "Understood. The focus should shift to communication and stability inside the relationship you already have.",
            ],
            "hi": [
                "Samajh gaya. Isse current relationship dynamic improve karne par focus hoga, ise fresh start ki tarah treat karne par nahi.",
                "Samajh gaya. Focus ab us relationship ke andar communication aur stability par hona chahiye jo aapke paas already hai.",
            ],
        },
    }

    EXISTING_MARRIAGE_ADJUSTMENTS = {
        "en": [
            "Understood, you are already married. The focus now is improving the current marriage, not marriage timing.",
            "Understood, this is about your existing marriage. The focus now is reducing friction and building better communication.",
        ],
        "hi": [
            "Samajh gaya, aap already married hain. Focus ab current marriage ko improve karne par hai, marriage timing par nahi.",
            "Samajh gaya, yeh aapki existing marriage ke baare mein hai. Focus ab friction kam karne aur better communication banane par hai.",
        ],
    }

    FOLLOWUP_TYPE_ORDER = {
        "definition": ["definition", "clarification", "instruction", "timing"],
        "instruction": ["instruction", "clarification", "timing"],
        "clarification": ["clarification", "instruction", "timing"],
        "context_update": ["context_update", "clarification", "instruction", "timing"],
        "timing": ["timing", "clarification", "instruction"],
        "detail": ["clarification", "instruction", "timing"],
        "general": ["clarification", "instruction", "timing"],
    }

    NEXT_STAGE_MAP = {
        MODE_ANALYSIS: ANALYSIS,
        "definition": EXPLANATION,
        "clarification": EXPLANATION,
        "context_update": EXPLANATION,
        "timing": TIMING,
        "instruction": GUIDANCE,
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
    def _topic_key(topic):
        value = str(topic or "").strip().lower()
        if value in {"career", "finance", "health", "marriage"}:
            return value
        return "career"

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
    def _normalized_intent_name(intent):
        if isinstance(intent, dict):
            intent = intent.get("intent")
        value = str(intent or "").strip().lower()
        if value == "detail":
            return "clarification"
        if value in {"definition", "instruction", "clarification", "context_update", "timing"}:
            return value
        return "general"

    @staticmethod
    def _intent_value(normalized_intent, user_text):
        if isinstance(normalized_intent, dict):
            return ConsultationEngine._normalized_intent_name(normalized_intent.get("intent"))
        if isinstance(normalized_intent, str):
            return ConsultationEngine._normalized_intent_name(normalized_intent)
        return ConsultationEngine._normalized_intent_name(IntentRouter.normalize_intent(user_text).get("intent"))

    @staticmethod
    def _guidance_payload(state, analysis_payload, language, consult_stage, intent="general", variant=0):
        return translate_to_life_guidance(
            analysis=analysis_payload,
            topic=state.get("topic"),
            consult_stage=consult_stage,
            language=language,
            intent=intent,
            variant=variant,
        )

    @staticmethod
    def _analysis_response(state, analysis_payload, language, script):
        for variant in (0, 1):
            guidance = ConsultationEngine._guidance_payload(
                state=state,
                analysis_payload=analysis_payload,
                language=language,
                consult_stage=1,
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

        for variant in (0, 1):
            guidance = ConsultationEngine._guidance_payload(
                state=state,
                analysis_payload=analysis_payload,
                language=language,
                consult_stage=2,
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

        guidance = ConsultationEngine._guidance_payload(
            state=state,
            analysis_payload=analysis_payload,
            language=language,
            consult_stage=1,
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
        guidance = ConsultationEngine._guidance_payload(
            state=state,
            analysis_payload=analysis_payload,
            language=language,
            consult_stage=consult_stage,
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
    def _clarification_response(state, analysis_payload, language, variant=0):
        topic = ConsultationEngine._topic_key(state.get("topic"))
        outcome = ConsultationEngine._localized(ConsultationEngine.OUTCOME_LINES.get(topic, {}), language, variant=variant)
        if variant == 0:
            return outcome

        window = ConsultationEngine._time_window(analysis_payload, language, variant=0)
        if ConsultationEngine._language_key(language) == "en":
            return f"{outcome}\nYou should notice this in {window}."
        return f"{outcome}\nIska farq {window} mein dikhna chahiye."

    @staticmethod
    def _context_update_kind(state, user_text):
        topic = ConsultationEngine._topic_key(state.get("topic"))
        normalized = IntentRouter._normalize_text(user_text)
        if topic == "marriage":
            special_phrases = (
                "already married",
                "married already",
                "ho chuka",
                "ho chuki",
                "shaadi ho chuki",
                "shaadi ho chuka",
            )
            if any(phrase in normalized for phrase in special_phrases):
                return "existing_marriage"
        return "general"

    @staticmethod
    def _context_update_response(state, user_text, analysis_payload, language, variant=0):
        topic = ConsultationEngine._topic_key(state.get("topic"))
        if ConsultationEngine._context_update_kind(state, user_text) == "existing_marriage":
            base = ConsultationEngine._localized(ConsultationEngine.EXISTING_MARRIAGE_ADJUSTMENTS, language, variant=variant)
        else:
            base = ConsultationEngine._localized(ConsultationEngine.CONTEXT_ADJUSTMENTS.get(topic, {}), language, variant=variant)

        if variant == 0:
            return base

        outcome = ConsultationEngine._localized(ConsultationEngine.OUTCOME_LINES.get(topic, {}), language, variant=0)
        window = ConsultationEngine._time_window(analysis_payload, language, variant=0)
        if ConsultationEngine._language_key(language) == "en":
            return f"{base}\nThe adjusted result should feel clearer in {window}."
        return f"{base}\nAdjusted result {window} mein zyada clear dikhna chahiye."

    @staticmethod
    def _timing_response(analysis_payload, language, variant=0):
        return ConsultationEngine._time_window(analysis_payload, language, variant=variant)

    @staticmethod
    def _render_followup(response_type, state, user_text, analysis_payload, language, variant=0):
        if response_type == "definition":
            return ConsultationEngine._definition_response(user_text, analysis_payload, language, variant=variant)
        if response_type == "instruction":
            return ConsultationEngine._instruction_response(state, analysis_payload, language, variant=variant)
        if response_type == "clarification":
            return ConsultationEngine._clarification_response(state, analysis_payload, language, variant=variant)
        if response_type == "context_update":
            return ConsultationEngine._context_update_response(state, user_text, analysis_payload, language, variant=variant)
        if response_type == "timing":
            return ConsultationEngine._timing_response(analysis_payload, language, variant=variant)
        return ConsultationEngine._clarification_response(state, analysis_payload, language, variant=variant)

    @staticmethod
    def _followup_type_order(intent):
        normalized_intent = ConsultationEngine._normalized_intent_name(intent)
        return ConsultationEngine.FOLLOWUP_TYPE_ORDER.get(normalized_intent, ConsultationEngine.FOLLOWUP_TYPE_ORDER["general"])

    @staticmethod
    def _contains_planet_reference(text):
        lowered = str(text or "").lower()
        for planet in ConsultationEngine.KNOWN_PLANETS:
            if re.search(rf"\b{re.escape(planet.lower())}\b", lowered):
                return True
        return False

    @staticmethod
    def _contains_template_labels(text):
        lines = [line.strip().lower() for line in str(text or "").splitlines() if line.strip()]
        return any(any(line.startswith(label) for label in ConsultationEngine.TEMPLATE_LABELS) for line in lines)

    @staticmethod
    def _contains_blocked_words(text):
        lowered = str(text or "").lower()
        return any(word in lowered for word in PersonaLayer.BLOCKED_WORDS)

    @staticmethod
    def _has_timeframe_hint(text):
        lowered = str(text or "").lower()
        return any(hint in lowered for hint in ConsultationEngine.TIMEFRAME_HINTS)

    @staticmethod
    def _is_valid_followup(response_type, text):
        raw = str(text or "").strip()
        lines = [line.strip() for line in raw.splitlines() if line.strip()]

        if not raw:
            return False
        if ConsultationEngine._contains_template_labels(raw):
            return False
        if ConsultationEngine._contains_blocked_words(raw):
            return False

        if response_type == "definition":
            return len(lines) <= 2

        if response_type == "instruction":
            if len(lines) < 2 or len(lines) > 3:
                return False
            if ConsultationEngine._contains_planet_reference(raw):
                return False
            return all(re.match(r"^\d+\.\s+\S+", line) for line in lines)

        if response_type == "timing":
            if len(lines) != 1:
                return False
            if ConsultationEngine._contains_planet_reference(raw):
                return False
            return ConsultationEngine._has_timeframe_hint(raw)

        if response_type in {"clarification", "context_update"}:
            if len(lines) > 2:
                return False
            if ConsultationEngine._contains_planet_reference(raw):
                return False
            return True

        return False

    @staticmethod
    def _followup_response(state, user_text, analysis_payload, language, intent):
        last_response = str(state.get("last_response") or "").strip()
        ordered_types = ConsultationEngine._followup_type_order(intent)
        primary_type = ordered_types[0]

        primary_text = ConsultationEngine._render_followup(
            response_type=primary_type,
            state=state,
            user_text=user_text,
            analysis_payload=analysis_payload,
            language=language,
            variant=0,
        )
        if ConsultationEngine._is_valid_followup(primary_type, primary_text) and primary_text != last_response:
            return primary_text, primary_type

        for response_type in ordered_types[1:]:
            text = ConsultationEngine._render_followup(
                response_type=response_type,
                state=state,
                user_text=user_text,
                analysis_payload=analysis_payload,
                language=language,
                variant=0,
            )
            if not ConsultationEngine._is_valid_followup(response_type, text):
                continue
            if text == last_response:
                continue
            return text, response_type

        for response_type in ordered_types:
            text = ConsultationEngine._render_followup(
                response_type=response_type,
                state=state,
                user_text=user_text,
                analysis_payload=analysis_payload,
                language=language,
                variant=1,
            )
            if not ConsultationEngine._is_valid_followup(response_type, text):
                continue
            if text == last_response:
                continue
            return text, response_type

        fallback_candidates = [
            ("clarification", ConsultationEngine._clarification_response(state, analysis_payload, language, variant=1)),
            ("context_update", ConsultationEngine._context_update_response(state, user_text, analysis_payload, language, variant=1)),
            ("instruction", ConsultationEngine._instruction_response(state, analysis_payload, language, variant=1)),
            ("timing", ConsultationEngine._timing_response(analysis_payload, language, variant=1)),
            ("definition", ConsultationEngine._definition_response(user_text, analysis_payload, language, variant=1)),
        ]
        for response_type, text in fallback_candidates:
            if not ConsultationEngine._is_valid_followup(response_type, text):
                continue
            if text == last_response:
                continue
            return text, response_type

        return primary_text, primary_type

    @staticmethod
    def _next_consult_stage(current_stage, response_type):
        current_stage = ConsultationEngine._clamp_stage(current_stage)
        if response_type == ConsultationEngine.MODE_ANALYSIS:
            return 2
        if response_type in {"definition", "clarification", "context_update"}:
            return max(current_stage, 2)
        if response_type == "timing":
            return max(current_stage, 3)
        if response_type == "instruction":
            return max(current_stage, 4)
        if response_type == "remedy":
            return 5
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
