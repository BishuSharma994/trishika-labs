import json
import re
from typing import Any


class LanguageEngine:

    ENGLISH = "english"
    HINDI_ROMAN = "hindi_roman"
    HINDI_DEVANAGARI = "hindi_devanagari"

    MODE_ORDER = [ENGLISH, HINDI_ROMAN, HINDI_DEVANAGARI]

    HINDI_ROMAN_MARKERS = {
        "shaadi","kya","kyu","kaise","hai","nahi","aap",
        "mera","meri","kar","ho","chuki","haan","janm"
    }

    NON_SWITCH_WORDS = {
        "1","2","3","4",
        "single","relationship","married","already married",
        "yes","no","haan","ok","okay"
    }

    # -----------------------------------------------------

    @staticmethod
    def detect_language(text: Any):

        t = str(text or "").strip()

        if any("\u0900" <= c <= "\u097F" for c in t):
            return LanguageEngine.HINDI_DEVANAGARI

        tokens = set(re.findall(r"[a-z']+", t.lower()))

        if tokens & LanguageEngine.HINDI_ROMAN_MARKERS:
            return LanguageEngine.HINDI_ROMAN

        return LanguageEngine.ENGLISH

    # -----------------------------------------------------

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

    # -----------------------------------------------------

    @staticmethod
    def handle_language(session, user_message):

        text = str(user_message or "").strip()

        state = LanguageEngine.load_state(
            getattr(session, "language_state_blob", None)
        )

        mode = getattr(session, "language_mode", None)
        confirmed = getattr(session, "language_confirmed", False)

        detected = LanguageEngine.detect_language(text)

        if text.lower() in LanguageEngine.NON_SWITCH_WORDS:
            return None

        if mode == LanguageEngine.HINDI_ROMAN and confirmed:
            return None

        if not confirmed:

            state["awaiting"] = True
            state["pending"] = detected

            prompts = {
                LanguageEngine.ENGLISH:
                    "You are writing in English.\n\nContinue?\n1 Yes\n2 Hindi Roman\n3 हिंदी",

                LanguageEngine.HINDI_ROMAN:
                    "Aap Hindi Roman mein baat kar rahe hain.\n\nContinue?\n1 Haan\n2 English\n3 हिंदी",

                LanguageEngine.HINDI_DEVANAGARI:
                    "आप हिंदी में लिख रहे हैं।\n\nजारी रखें?\n1 हाँ\n2 English\n3 Hindi Roman",
            }

            return {
                "response": prompts[detected],
                "language_mode": detected,
                "language_confirmed": False,
                "state_blob": LanguageEngine.dump_state(state),
            }

        return None

    # -----------------------------------------------------

    @staticmethod
    def enforce_response_language(session, text):

        mode = getattr(session, "language_mode", None)

        detected = LanguageEngine.detect_language(text)

        if mode == LanguageEngine.HINDI_ROMAN:
            return text

        if mode == LanguageEngine.HINDI_DEVANAGARI and detected != LanguageEngine.HINDI_DEVANAGARI:
            return "चलिए हिंदी में बात जारी रखते हैं.\n\n" + text

        if mode == LanguageEngine.ENGLISH and detected != LanguageEngine.ENGLISH:
            return "Let's continue in English.\n\n" + text

        return text