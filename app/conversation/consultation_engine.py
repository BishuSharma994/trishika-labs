import hashlib
import json
import re
from difflib import SequenceMatcher

from app.conversation.astrology_response_template import AstrologyResponseTemplate
from app.conversation.intent_router import IntentRouter
from app.conversation.life_translation_engine import translate_to_life_guidance
from app.conversation.persona_layer import PersonaLayer


class ConsultationEngine:

    START = "START"
    COLLECT_BIRTHDATA = "COLLECT_BIRTHDATA"
    TOPIC_SELECTION = "TOPIC_SELECTION"
    SUBTOPIC_SELECTION = "SUBTOPIC_SELECTION"
    ANALYSIS = "ANALYSIS"
    TIMING = "TIMING"
    GUIDANCE = "GUIDANCE"
    REMEDY = "REMEDY"

    # Legacy aliases kept for compatibility with existing callers.
    DOMAIN_ENTRY = TOPIC_SELECTION
    STATUS_CAPTURE = SUBTOPIC_SELECTION
    DIAGNOSTIC = ANALYSIS
    INTERPRETATION = ANALYSIS
    ACTION_PLAN = REMEDY

    DEPTH_MIN = 1
    DEPTH_MAX = 5

    VALID_STATES = {
        START,
        COLLECT_BIRTHDATA,
        TOPIC_SELECTION,
        SUBTOPIC_SELECTION,
        ANALYSIS,
        TIMING,
        GUIDANCE,
        REMEDY,
    }

    SUBTOPIC_KEYWORDS = {
        "career": {
            "job_switch": {
                "job switch", "switch job", "change job", "new job", "naukri badalna",
                "switch", "job", "interview",
            },
            "promotion": {
                "promotion", "growth", "raise", "increment", "salary growth",
                "padonnati", "raise in salary",
            },
            "business_direction": {
                "business direction", "business", "startup", "entrepreneur", "vyapar",
                "biz direction", "company direction",
            },
        },
        "finance": {
            "savings": {
                "savings", "saving", "save", "bachat", "fund", "cash reserve",
            },
            "investment": {
                "investment", "invest", "sip", "stocks", "mutual fund", "nivesh",
            },
            "debt_management": {
                "debt", "loan", "emi", "karz", "karja", "debt management",
                "karz prabandhan", "repayment",
            },
        },
        "marriage": {
            "single_path": {
                "single", "new relationship", "naya rishta", "new partner",
            },
            "relationship_stability": {
                "relationship", "stability", "existing relationship", "rishta",
                "jhagda", "jagda", "conflict", "clarity",
            },
            "married_life": {
                "married", "marriage", "spouse", "husband", "wife", "vivahit",
                "shaadi",
            },
        },
        "health": {
            "stress": {
                "stress", "anxiety", "tanav", "mental", "worry",
            },
            "lifestyle_balance": {
                "lifestyle", "routine", "sleep", "diet", "jeevanshaili", "santulan",
            },
            "specific_condition": {
                "disease", "illness", "medical", "diagnosis", "hospital", "pain",
                "specific issue", "vishesh",
            },
        },
    }

    DEFAULT_SUBTOPIC = {
        "career": "job_switch",
        "finance": "savings",
        "marriage": "relationship_stability",
        "health": "stress",
    }

    TOPIC_FALLBACK_ORDER = ("career", "marriage", "finance", "health")
    TOPIC_HOUSE_MAP = {
        "career": 10,
        "finance": 2,
        "marriage": 7,
        "health": 6,
    }

    @staticmethod
    def _default_state(language="english"):
        return {
            "state": ConsultationEngine.START,
            "topic": None,
            "subtopic": None,
            "depth": 1,
            "last_response_hash": None,
            "language": language or "english",
            "last_user_key": None,
            "last_state": None,
        }

    @staticmethod
    def hash_response(text):
        value = str(text or "")
        return hashlib.md5(value.encode("utf-8")).hexdigest()

    @staticmethod
    def _clamp_depth(depth):
        try:
            value = int(depth)
        except Exception:
            value = ConsultationEngine.DEPTH_MIN
        if value < ConsultationEngine.DEPTH_MIN:
            return ConsultationEngine.DEPTH_MIN
        if value > ConsultationEngine.DEPTH_MAX:
            return ConsultationEngine.DEPTH_MAX
        return value

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

        # Migration path for legacy blob shapes.
        state = dict(base)
        state["state"] = parsed.get("state") if parsed.get("state") in ConsultationEngine.VALID_STATES else base["state"]
        state["topic"] = parsed.get("topic")
        state["subtopic"] = parsed.get("subtopic")
        state["depth"] = ConsultationEngine._clamp_depth(parsed.get("depth"))
        state["last_response_hash"] = parsed.get("last_response_hash")
        state["language"] = parsed.get("language") or base["language"]
        state["last_user_key"] = parsed.get("last_user_key")
        state["last_state"] = parsed.get("last_state")
        return state

    @staticmethod
    def dump_state(state):
        return json.dumps(state, ensure_ascii=False)

    @staticmethod
    def bootstrap_state(language, flow_state):
        state = ConsultationEngine._default_state(language=language)
        if flow_state in ConsultationEngine.VALID_STATES:
            state["state"] = flow_state
        return ConsultationEngine.dump_state(state)

    @staticmethod
    def move_state(blob, flow_state, language=None, topic=None, subtopic=None, reset_depth=False):
        state = ConsultationEngine.load_state(blob)
        if flow_state in ConsultationEngine.VALID_STATES:
            state["state"] = flow_state
        if language:
            state["language"] = language
        if topic is not None:
            state["topic"] = topic
        if subtopic is not None:
            state["subtopic"] = subtopic
        if reset_depth:
            state["depth"] = 1
            state["last_response_hash"] = None
        return ConsultationEngine.dump_state(state)

    @staticmethod
    def reset_language(blob, language):
        state = ConsultationEngine.load_state(blob)
        previous = state.get("language")
        if language and language != previous:
            state["language"] = language
            state["depth"] = 1
            state["last_response_hash"] = None
            state["last_user_key"] = None
            state["last_state"] = None
        elif language:
            state["language"] = language
        return ConsultationEngine.dump_state(state)

    @staticmethod
    def _normalized_text(text):
        value = str(text or "").strip().lower()
        value = re.sub(r"[^a-z0-9\u0900-\u097f\s]", " ", value)
        return re.sub(r"\s+", " ", value).strip()

    @staticmethod
    def _state_for_depth(depth):
        depth = ConsultationEngine._clamp_depth(depth)
        if depth <= 2:
            return ConsultationEngine.ANALYSIS
        if depth == 3:
            return ConsultationEngine.GUIDANCE
        return ConsultationEngine.REMEDY

    @staticmethod
    def _escalation_level(state_name, depth):
        depth = ConsultationEngine._clamp_depth(depth)
        if state_name == ConsultationEngine.REMEDY or depth >= 4:
            return 4
        if state_name == ConsultationEngine.GUIDANCE or depth == 3:
            return 3
        if state_name == ConsultationEngine.TIMING or depth == 2:
            return 2
        return 1

    @staticmethod
    def _best_similarity_match(tokens, keywords):
        best_score = 0.0
        for token in tokens:
            if len(token) < 3:
                continue
            for keyword in keywords:
                if len(keyword) < 3:
                    continue
                score = SequenceMatcher(None, token, keyword).ratio()
                if score > best_score:
                    best_score = score
        return best_score

    @staticmethod
    def _detect_subtopic(topic, text, existing_subtopic=None):
        if not topic:
            return None

        mapping = ConsultationEngine.SUBTOPIC_KEYWORDS.get(topic, {})
        normalized = ConsultationEngine._normalized_text(text)
        if not normalized:
            return existing_subtopic

        for subtopic, keywords in mapping.items():
            for keyword in keywords:
                pattern = rf"\b{re.escape(keyword.lower())}\b"
                if re.search(pattern, normalized):
                    return subtopic

        tokens = normalized.split()
        best_subtopic = None
        best_score = 0.0
        for subtopic, keywords in mapping.items():
            score = ConsultationEngine._best_similarity_match(tokens, keywords)
            if score > best_score:
                best_score = score
                best_subtopic = subtopic

        if best_subtopic and best_score >= 0.84:
            return best_subtopic

        return existing_subtopic

    @staticmethod
    def _topic_from_input(user_text, current_topic=None):
        return IntentRouter.detect_domain(user_text, current_domain=current_topic)

    @staticmethod
    def _intent_value(normalized_intent, user_text):
        if isinstance(normalized_intent, dict):
            return normalized_intent.get("intent")
        if isinstance(normalized_intent, str):
            return normalized_intent
        return IntentRouter.normalize_intent(user_text).get("intent")

    @staticmethod
    def _apply_intent_transition(state, intent, user_text):
        depth = ConsultationEngine._clamp_depth(state.get("depth"))
        current_state = state.get("state")

        if intent == "timing":
            depth = max(depth, 2)
            return ConsultationEngine.TIMING, depth
        if intent == "guidance":
            depth = max(depth, 3)
            return ConsultationEngine.GUIDANCE, depth
        if intent == "remedy":
            depth = max(depth, 4)
            return ConsultationEngine.REMEDY, depth
        if intent in {"detail", "explanation", "affirm"}:
            depth = min(ConsultationEngine.DEPTH_MAX, depth + 1)
            return ConsultationEngine._state_for_depth(depth), depth

        # Unknown follow-up still escalates one rung to avoid repeating the same block.
        normalized = ConsultationEngine._normalized_text(user_text)
        if normalized and current_state in {
            ConsultationEngine.ANALYSIS,
            ConsultationEngine.TIMING,
            ConsultationEngine.GUIDANCE,
            ConsultationEngine.REMEDY,
        }:
            depth = min(ConsultationEngine.DEPTH_MAX, depth + 1)
            return ConsultationEngine._state_for_depth(depth), depth

        return current_state, depth

    @staticmethod
    def _build_analysis_payload(state, domain_data):
        data = domain_data or {}
        topic = state.get("topic")
        score = data.get("score", 50)
        try:
            numeric_score = int(score)
        except Exception:
            numeric_score = 50

        if numeric_score >= 70:
            strength = "strong"
        elif numeric_score >= 50:
            strength = "moderate"
        else:
            strength = "weak"

        return {
            "planet": data.get("primary_driver") or "Moon",
            "house": ConsultationEngine.TOPIC_HOUSE_MAP.get(topic, 1),
            "strength": strength,
            "risk_planet": data.get("risk_factor") or "Mars",
            "supporting_planet": data.get("primary_driver") or "Jupiter",
            "score": numeric_score,
            "momentum": data.get("momentum"),
        }

    @staticmethod
    def _render_consultation_response(state, domain_data, language, script):
        level = ConsultationEngine._escalation_level(state.get("state"), state.get("depth"))
        analysis_payload = ConsultationEngine._build_analysis_payload(state, domain_data)
        life_guidance = translate_to_life_guidance(
            analysis=analysis_payload,
            topic=state.get("topic"),
            subtopic=state.get("subtopic"),
            depth=level,
        )
        return PersonaLayer.format_guidance(
            guidance=life_guidance,
            language=language,
            script=script,
        )

    @staticmethod
    def _render_with_repetition_guard(state, domain_data, language, script):
        for _ in range(3):
            text = ConsultationEngine._render_consultation_response(
                state=state,
                domain_data=domain_data,
                language=language,
                script=script,
            )
            digest = ConsultationEngine.hash_response(text)
            if digest != state.get("last_response_hash"):
                state["last_response_hash"] = digest
                return text

            if state.get("depth", 1) < ConsultationEngine.DEPTH_MAX:
                state["depth"] = ConsultationEngine._clamp_depth(state.get("depth", 1) + 1)
                state["state"] = ConsultationEngine._state_for_depth(state["depth"])
                continue

            tail = AstrologyResponseTemplate._localized(
                language,
                script,
                "Ask for another subtopic if you want a fresh angle.",
                "Naya angle ke liye doosra subtopic puchiye.",
                "नया दृष्टिकोण चाहिए तो दूसरा उप-विषय पूछें।",
            )
            varied_text = f"{text}\n\n{tail}"
            state["last_response_hash"] = ConsultationEngine.hash_response(varied_text)
            return varied_text

        fallback = AstrologyResponseTemplate._localized(
            language,
            script,
            "Please continue with your next question.",
            "Kripya apna agla sawal batayiye.",
            "कृपया अपना अगला सवाल बताइए।",
        )
        state["last_response_hash"] = ConsultationEngine.hash_response(fallback)
        return fallback

    @staticmethod
    def detect_domain(text, current_domain=None):
        return ConsultationEngine._topic_from_input(text, current_topic=current_domain)

    @staticmethod
    def score_domain(domain):
        return domain

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
        incoming_language = language or state.get("language") or "english"
        if state.get("language") != incoming_language:
            state["language"] = incoming_language
            state["depth"] = 1
            state["last_response_hash"] = None
            state["last_user_key"] = None
            state["last_state"] = None
        else:
            state["language"] = incoming_language

        if state.get("state") == ConsultationEngine.START and stage in ConsultationEngine.VALID_STATES:
            state["state"] = stage

        if domain_switched and domain:
            state["topic"] = domain
            state["subtopic"] = None
            state["depth"] = 1
            state["last_response_hash"] = None
            state["state"] = ConsultationEngine.SUBTOPIC_SELECTION

        current_state = state.get("state") or ConsultationEngine.START
        user_key = ConsultationEngine._normalized_text(user_text)

        if current_state == ConsultationEngine.START:
            state["state"] = ConsultationEngine.TOPIC_SELECTION
            text = AstrologyResponseTemplate.topic_prompt(language, script)
            state["last_response_hash"] = ConsultationEngine.hash_response(text)
            state["last_user_key"] = user_key
            state["last_state"] = state["state"]
            return {
                "text": text,
                "next_stage": state["state"],
                "state_blob": ConsultationEngine.dump_state(state),
            }

        if current_state == ConsultationEngine.COLLECT_BIRTHDATA:
            text = AstrologyResponseTemplate._localized(
                language,
                script,
                "Please share date, time, and place of birth first.",
                "Pehle janm ki tareekh, samay, aur jagah bhejiye.",
                "पहले जन्म की तारीख, समय और जगह भेजें।",
            )
            state["last_response_hash"] = ConsultationEngine.hash_response(text)
            state["last_user_key"] = user_key
            state["last_state"] = current_state
            return {
                "text": text,
                "next_stage": state["state"],
                "state_blob": ConsultationEngine.dump_state(state),
            }

        if current_state == ConsultationEngine.TOPIC_SELECTION:
            selected_topic = domain or ConsultationEngine._topic_from_input(user_text, current_topic=state.get("topic"))
            if not selected_topic:
                text = AstrologyResponseTemplate.topic_prompt(language, script)
                state["last_response_hash"] = ConsultationEngine.hash_response(text)
                state["last_user_key"] = user_key
                state["last_state"] = current_state
                return {
                    "text": text,
                    "next_stage": state["state"],
                    "state_blob": ConsultationEngine.dump_state(state),
                }

            state["topic"] = selected_topic
            state["depth"] = 1
            state["last_response_hash"] = None
            state["state"] = ConsultationEngine.SUBTOPIC_SELECTION

            selected_subtopic = ConsultationEngine._detect_subtopic(selected_topic, user_text)
            if selected_subtopic:
                state["subtopic"] = selected_subtopic
                state["state"] = ConsultationEngine.ANALYSIS
                text = ConsultationEngine._render_with_repetition_guard(state, domain_data, language, script)
            else:
                text = AstrologyResponseTemplate.subtopic_prompt(selected_topic, language, script)
                state["last_response_hash"] = ConsultationEngine.hash_response(text)

            state["last_user_key"] = user_key
            state["last_state"] = state["state"]
            return {
                "text": text,
                "next_stage": state["state"],
                "state_blob": ConsultationEngine.dump_state(state),
            }

        if current_state == ConsultationEngine.SUBTOPIC_SELECTION:
            selected_topic = state.get("topic") or domain or ConsultationEngine._topic_from_input(user_text)
            if not selected_topic:
                state["state"] = ConsultationEngine.TOPIC_SELECTION
                text = AstrologyResponseTemplate.topic_prompt(language, script)
                state["last_response_hash"] = ConsultationEngine.hash_response(text)
                state["last_user_key"] = user_key
                state["last_state"] = state["state"]
                return {
                    "text": text,
                    "next_stage": state["state"],
                    "state_blob": ConsultationEngine.dump_state(state),
                }

            state["topic"] = selected_topic
            selected_subtopic = ConsultationEngine._detect_subtopic(
                selected_topic,
                user_text,
                existing_subtopic=state.get("subtopic"),
            )
            if not selected_subtopic:
                text = AstrologyResponseTemplate.subtopic_prompt(selected_topic, language, script)
                state["last_response_hash"] = ConsultationEngine.hash_response(text)
                state["last_user_key"] = user_key
                state["last_state"] = state["state"]
                return {
                    "text": text,
                    "next_stage": state["state"],
                    "state_blob": ConsultationEngine.dump_state(state),
                }

            state["subtopic"] = selected_subtopic
            state["depth"] = 1
            state["state"] = ConsultationEngine.ANALYSIS
            text = ConsultationEngine._render_with_repetition_guard(state, domain_data, language, script)
            state["last_user_key"] = user_key
            state["last_state"] = state["state"]
            return {
                "text": text,
                "next_stage": state["state"],
                "state_blob": ConsultationEngine.dump_state(state),
            }

        # Active consultation states.
        selected_topic = state.get("topic")
        detected_topic = domain or ConsultationEngine._topic_from_input(user_text, current_topic=selected_topic)
        if detected_topic and detected_topic != selected_topic:
            state["topic"] = detected_topic
            state["subtopic"] = ConsultationEngine._detect_subtopic(detected_topic, user_text)
            state["depth"] = 1
            state["last_response_hash"] = None
            if state["subtopic"]:
                state["state"] = ConsultationEngine.ANALYSIS
                text = ConsultationEngine._render_with_repetition_guard(state, domain_data, language, script)
            else:
                state["state"] = ConsultationEngine.SUBTOPIC_SELECTION
                text = AstrologyResponseTemplate.subtopic_prompt(detected_topic, language, script)
                state["last_response_hash"] = ConsultationEngine.hash_response(text)
            state["last_user_key"] = user_key
            state["last_state"] = state["state"]
            return {
                "text": text,
                "next_stage": state["state"],
                "state_blob": ConsultationEngine.dump_state(state),
            }

        if not state.get("topic"):
            state["state"] = ConsultationEngine.TOPIC_SELECTION
            text = AstrologyResponseTemplate.topic_prompt(language, script)
            state["last_response_hash"] = ConsultationEngine.hash_response(text)
            state["last_user_key"] = user_key
            state["last_state"] = state["state"]
            return {
                "text": text,
                "next_stage": state["state"],
                "state_blob": ConsultationEngine.dump_state(state),
            }

        if not state.get("subtopic"):
            state["state"] = ConsultationEngine.SUBTOPIC_SELECTION
            text = AstrologyResponseTemplate.subtopic_prompt(state["topic"], language, script)
            state["last_response_hash"] = ConsultationEngine.hash_response(text)
            state["last_user_key"] = user_key
            state["last_state"] = state["state"]
            return {
                "text": text,
                "next_stage": state["state"],
                "state_blob": ConsultationEngine.dump_state(state),
            }

        # Same-state repeated input escalation.
        if user_key and user_key == state.get("last_user_key") and state.get("last_state") == state.get("state"):
            state["depth"] = ConsultationEngine._clamp_depth(state.get("depth", 1) + 1)
            state["state"] = ConsultationEngine._state_for_depth(state["depth"])
        else:
            intent = ConsultationEngine._intent_value(normalized_intent, user_text)
            next_state, next_depth = ConsultationEngine._apply_intent_transition(state, intent, user_text)
            state["state"] = next_state
            state["depth"] = ConsultationEngine._clamp_depth(next_depth)

        # Guarantee subtopic remains attached to every deeper response.
        if not state.get("subtopic"):
            state["subtopic"] = ConsultationEngine.DEFAULT_SUBTOPIC.get(state["topic"])

        text = ConsultationEngine._render_with_repetition_guard(state, domain_data, language, script)
        state["last_user_key"] = user_key
        state["last_state"] = state["state"]

        return {
            "text": text,
            "next_stage": state["state"],
            "state_blob": ConsultationEngine.dump_state(state),
        }
