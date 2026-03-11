import json
import re
from typing import Any


class ConsultationEngine:

    DOMAIN_ENTRY = "DOMAIN_ENTRY"
    STATUS_CAPTURE = "STATUS_CAPTURE"
    DIAGNOSTIC = "DIAGNOSTIC"
    INTERPRETATION = "INTERPRETATION"
    GUIDANCE = "GUIDANCE"
    ACTION_PLAN = "ACTION_PLAN"

    # --------------------------------------------------

    DOMAIN_ALIASES = {
        "career": ["career","job","naukri","profession","work"],
        "marriage": ["marriage","shaadi","vivah","wife","husband"],
        "finance": ["finance","money","paisa","income","wealth"],
        "health": ["health","fitness","disease","sehat"]
    }

    STATUS_MAP = {
        "marriage": {
            "single": ["1","single","not married"],
            "relationship": ["2","relationship","dating"],
            "married": ["3","married","already married","spouse"]
        }
    }

    # --------------------------------------------------

    @staticmethod
    def detect_domain(text, current_domain=None):

        t = str(text or "").lower()

        for domain, aliases in ConsultationEngine.DOMAIN_ALIASES.items():
            for alias in aliases:
                if re.search(rf"\b{alias}\b", t):
                    return domain

        return None

    # --------------------------------------------------

    @staticmethod
    def score_domain(domain):

        return domain

    # --------------------------------------------------

    @staticmethod
    def load_state(blob):

        if not blob:
            return {"domain_memory": {}}

        try:
            return json.loads(blob)
        except Exception:
            return {"domain_memory": {}}

    @staticmethod
    def dump_state(state):

        return json.dumps(state, ensure_ascii=False)

    # --------------------------------------------------

    @staticmethod
    def parse_status(domain, text):

        mapping = ConsultationEngine.STATUS_MAP.get(domain, {})

        t = str(text or "").lower()

        for status, words in mapping.items():
            for w in words:
                if re.search(rf"\b{w}\b", t):
                    return status

        return None

    # --------------------------------------------------

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
    ):

        state = ConsultationEngine.load_state(session_state_blob)

        memory = state["domain_memory"].setdefault(domain, {})

        # ------------------------------------------
        # DOMAIN ENTRY
        # ------------------------------------------

        if stage == ConsultationEngine.DOMAIN_ENTRY:

            question = (
                "Shaadi ke baare mein sahi guidance dene ke liye pehle current situation samajhna zaroori hai.\n\n"
                "Aapki current situation kya hai?\n"
                "1. Single\n"
                "2. Relationship mein\n"
                "3. Already married"
            )

            return {
                "text": question,
                "next_stage": ConsultationEngine.STATUS_CAPTURE,
                "state_blob": ConsultationEngine.dump_state(state),
            }

        # ------------------------------------------
        # STATUS CAPTURE
        # ------------------------------------------

        if stage == ConsultationEngine.STATUS_CAPTURE:

            status = ConsultationEngine.parse_status(domain, user_text)

            if not status:

                return {
                    "text": "Please choose one option.\n1 Single\n2 Relationship\n3 Married",
                    "next_stage": ConsultationEngine.STATUS_CAPTURE,
                    "state_blob": ConsultationEngine.dump_state(state),
                }

            memory["status"] = status

            question = "Is current harmony stable, mixed, or under stress?"

            return {
                "text": f"Noted. Current status: {status}.\n\n{question}",
                "next_stage": ConsultationEngine.DIAGNOSTIC,
                "state_blob": ConsultationEngine.dump_state(state),
            }

        # ------------------------------------------
        # DIAGNOSTIC
        # ------------------------------------------

        if stage == ConsultationEngine.DIAGNOSTIC:

            memory["diagnostic"] = user_text

            text = (
                "Based on your chart signals and what you shared, "
                "the situation looks workable but requires patience."
            )

            return {
                "text": text,
                "next_stage": ConsultationEngine.INTERPRETATION,
                "state_blob": ConsultationEngine.dump_state(state),
            }

        # ------------------------------------------
        # INTERPRETATION
        # ------------------------------------------

        if stage == ConsultationEngine.INTERPRETATION:

            text = (
                "Planetary combinations suggest that decisions in this phase "
                "should be slow and well-structured."
            )

            return {
                "text": text,
                "next_stage": ConsultationEngine.GUIDANCE,
                "state_blob": ConsultationEngine.dump_state(state),
            }

        # ------------------------------------------
        # GUIDANCE
        # ------------------------------------------

        if stage == ConsultationEngine.GUIDANCE:

            text = (
                "Focus on improving communication and avoid reacting impulsively."
            )

            return {
                "text": text,
                "next_stage": ConsultationEngine.ACTION_PLAN,
                "state_blob": ConsultationEngine.dump_state(state),
            }

        # ------------------------------------------

        return {
            "text": "Share your next question.",
            "next_stage": ConsultationEngine.ACTION_PLAN,
            "state_blob": ConsultationEngine.dump_state(state),
        }