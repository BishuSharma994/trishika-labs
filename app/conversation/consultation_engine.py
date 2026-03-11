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
    def _is_hi_dev(language, script):
        return (
            language in {"hindi_devanagari", "hi_dev"}
            or (language == "hi" and script == "devanagari")
        )

    @staticmethod
    def _is_hi_rom(language, script):
        return (
            language in {"hindi_roman", "hi_rom"}
            or (language == "hi" and script in {"roman", "latin"})
        )

    @staticmethod
    def _domain_entry_question(domain, language, script):
        if domain == "marriage":
            if ConsultationEngine._is_hi_dev(language, script):
                return (
                    "विवाह पर सही मार्गदर्शन देने के लिए पहले आपकी current situation समझना जरूरी है।\n\n"
                    "आपकी current situation क्या है?\n"
                    "1. Single\n"
                    "2. Relationship में\n"
                    "3. Already married"
                )
            if ConsultationEngine._is_hi_rom(language, script):
                return (
                    "Shaadi ke baare mein sahi guidance dene ke liye pehle current situation samajhna zaroori hai.\n\n"
                    "Aapki current situation kya hai?\n"
                    "1. Single\n"
                    "2. Relationship mein\n"
                    "3. Already married"
                )
            return (
                "To guide you accurately on marriage, I first need your current relationship status.\n\n"
                "What is your current situation?\n"
                "1. Single\n"
                "2. In a relationship\n"
                "3. Already married"
            )

        if ConsultationEngine._is_hi_dev(language, script):
            questions = {
                "career": "करियर में आपका अभी मुख्य फोकस किस पर है: job switch, promotion, या business direction?",
                "finance": "वित्त में आपका अभी मुख्य फोकस क्या है: बचत, निवेश, या कर्ज प्रबंधन?",
                "health": "स्वास्थ्य में आपकी मुख्य चिंता क्या है: stress, lifestyle balance, या कोई specific issue?",
            }
            return questions.get(domain, "कृपया इस विषय से जुड़ी अपनी वर्तमान स्थिति एक लाइन में बताएं।")

        if ConsultationEngine._is_hi_rom(language, script):
            questions = {
                "career": "Career mein aapka abhi main focus kis par hai: job switch, promotion, ya business direction?",
                "finance": "Finance mein aap abhi kis par focus kar rahe hain: savings, investment, ya debt management?",
                "health": "Health mein aapki main concern kya hai: stress, lifestyle balance, ya koi specific issue?",
            }
            return questions.get(domain, "Kripya is topic se judi apni current situation ek line mein batayein.")

        questions = {
            "career": "In career, what is your current focus: job switch, promotion, or business direction?",
            "finance": "In finance, what are you prioritizing right now: savings, investments, or debt management?",
            "health": "In health, is your concern mainly stress, lifestyle balance, or a specific issue?",
        }
        return questions.get(domain, "Please share your current situation in one line for this topic.")

    @staticmethod
    def _marriage_retry_prompt(language, script):
        if ConsultationEngine._is_hi_dev(language, script):
            return "कृपया एक विकल्प चुनें:\n1 Single\n2 Relationship\n3 Married"
        if ConsultationEngine._is_hi_rom(language, script):
            return "Please ek option choose karein:\n1 Single\n2 Relationship\n3 Married"
        return "Please choose one option.\n1 Single\n2 Relationship\n3 Married"

    @staticmethod
    def _marriage_diagnostic_prompt(language, script):
        if ConsultationEngine._is_hi_dev(language, script):
            return "वर्तमान relationship harmony stable है, mixed है, या stress में है?"
        if ConsultationEngine._is_hi_rom(language, script):
            return "Current relationship harmony stable hai, mixed hai, ya stress mein hai?"
        return "Is your current relationship harmony stable, mixed, or under stress?"

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
            question = ConsultationEngine._domain_entry_question(domain, language, script)
            next_stage = (
                ConsultationEngine.STATUS_CAPTURE
                if domain == "marriage"
                else ConsultationEngine.DIAGNOSTIC
            )

            return {
                "text": question,
                "next_stage": next_stage,
                "state_blob": ConsultationEngine.dump_state(state),
            }

        # ------------------------------------------
        # STATUS CAPTURE
        # ------------------------------------------

        if stage == ConsultationEngine.STATUS_CAPTURE:
            if domain != "marriage":
                memory["status"] = str(user_text or "").strip()
                if ConsultationEngine._is_hi_dev(language, script):
                    bridge_text = "ठीक है, यह मैंने नोट कर लिया। अब मैं इसे आपकी कुंडली संकेतों के साथ जोड़कर देखता हूँ।"
                elif ConsultationEngine._is_hi_rom(language, script):
                    bridge_text = "Theek hai, maine yeh note kar liya. Ab main ise aapke chart signals ke saath dekh raha hoon."
                else:
                    bridge_text = "Noted. I will now evaluate this with your chart signals."
                return {
                    "text": bridge_text,
                    "next_stage": ConsultationEngine.DIAGNOSTIC,
                    "state_blob": ConsultationEngine.dump_state(state),
                }

            status = ConsultationEngine.parse_status(domain, user_text)

            if not status:

                return {
                    "text": ConsultationEngine._marriage_retry_prompt(language, script),
                    "next_stage": ConsultationEngine.STATUS_CAPTURE,
                    "state_blob": ConsultationEngine.dump_state(state),
                }

            memory["status"] = status

            question = ConsultationEngine._marriage_diagnostic_prompt(language, script)

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
