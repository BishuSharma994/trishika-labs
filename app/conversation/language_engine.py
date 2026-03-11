import json
import re
from typing import Any


class LanguageEngine:

    ENGLISH           = "english"
    HINDI_ROMAN       = "hindi_roman"
    HINDI_DEVANAGARI  = "hindi_devanagari"

    MODE_ORDER = [ENGLISH, HINDI_ROMAN, HINDI_DEVANAGARI]

    HINDI_ROMAN_MARKERS = {
        "shaadi", "kya", "kyu", "kaise", "hai", "nahi", "aap",
        "mera", "meri", "kar", "ho", "chuki", "haan", "janm"
    }

    NON_SWITCH_WORDS = {
        "1", "2", "3", "4",
        "single", "relationship", "married", "already married",
        "yes", "no", "haan", "ok", "okay"
    }

    # -----------------------------------------------------------------
    @staticmethod
    def detect_language(text: Any):
        t = str(text or "").strip()
        if any("\u0900" <= c <= "\u097F" for c in t):
            return LanguageEngine.HINDI_DEVANAGARI
        tokens = set(re.findall(r"[a-z']+", t.lower()))
        if tokens & LanguageEngine.HINDI_ROMAN_MARKERS:
            return LanguageEngine.HINDI_ROMAN
        return LanguageEngine.ENGLISH

    # -----------------------------------------------------------------
    @staticmethod
    def load_state(blob):
        if not blob:
            return {"awaiting": False, "pending": None}
        try:
            return json.loads(blob)
        except Exception:
            return {"awaiting": False, "pending": None}

    @staticmethod
    def dump_state(state):
        return json.dumps(state, ensure_ascii=False)

    # -----------------------------------------------------------------
    @staticmethod
    def handle_language(session, user_message):
        text      = str(user_message or "").strip()
        state     = LanguageEngine.load_state(getattr(session, "language_state_blob", None))
        mode      = getattr(session, "language_mode", None)
        confirmed = getattr(session, "language_confirmed", False)

        
