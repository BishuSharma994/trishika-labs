import json
import re
from typing import Any



class LanguageEngine:

    ENGLISH           = "english"
    HINDI_ROMAN       = "hindi_roman"
    HINDI_DEVANAGARI  = "hindi_devanagari"

    MODE_ORDER = [ENGLISH, HINDI_ROMAN]

    HINDI_ROMAN_MARKERS = {
        "shaadi", "kya", "kyu", "kaise", "kab", "hai", "hain", "nahi", "aap",
        "mera", "meri", "kar", "ho", "hogi", "hoga", "raha", "rha", "chuki",
        "haan", "janm", "janam", "tareekh", "samay", "sthan", "ka", "ki", "ke",
        "mein", "me", "se", "tak", "agle", "mahina", "mahine", "kyunki"
    }

    NON_SWITCH_WORDS = {
        "1", "2", "3", "4",
        "single", "relationship", "married", "already married",
        "yes", "no", "haan", "ok", "okay"
    }

    ENGLISH_MARKERS = {
        "what", "when", "how", "why", "which", "where",
        "please", "can", "could", "would", "should",
        "tell", "explain", "meaning", "guide", "help",
        "career", "job", "finance", "marriage", "health",
        "opportunity", "opportunities", "time", "timing",
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

    @staticmethod
    def looks_like_english(text: Any):
        t = str(text or "").strip()
        if not t:
            return False
        if any("\u0900" <= c <= "\u097F" for c in t):
            return False

        tokens = re.findall(r"[a-z']+", t.lower())
        if not tokens:
            return False

        if set(tokens) & LanguageEngine.HINDI_ROMAN_MARKERS:
            return False

        if set(tokens) & LanguageEngine.ENGLISH_MARKERS:
            return True

        # If it's longer text with no Hindi markers, treat as English.
        return len(tokens) >= 4

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
    def _detect_explicit_switch_request(text):
        t = str(text or "").strip().lower()
        t_norm = re.sub(r"[^a-z0-9\u0900-\u097f\s]", " ", t)
        t_norm = re.sub(r"\s+", " ", t_norm).strip()
        tokens = set(t_norm.split())

        english_phrases = {
            "english",
            "in english",
            "reply in english",
            "speak english",
            "talk in english",
            "english please",
            "english me",
            "english mein",
            "switch to english",
            "can you tell me in english",
            "tell me in english",
        }
        hindi_rom_phrases = {
            "hindi",
            "हिंदी",
            "in hindi",
            "hindi me",
            "hindi mein",
            "switch to hindi",
            "hindi roman",
            "hindi (roman)",
            "roman hindi",
            "hinglish",
            "in hindi roman",
            "hindi roman me",
            "hindi roman mein",
            "switch to hindi roman",
        }
        english_tokens = {"english", "englis", "englsh", "inglish"}
        hindi_tokens = {"hindi", "हिंदी"}
        roman_tokens = {"roman", "hinglish"}

        if (
            t_norm in english_phrases
            or (tokens & english_tokens and (len(tokens) <= 3 or {"reply", "speak", "talk", "switch", "tell", "please"} & tokens))
            or re.search(r"(reply|speak|talk|switch|tell).*(english|englis|inglish|englsh)", t_norm)
        ):
            return LanguageEngine.ENGLISH
        if (
            t_norm in hindi_rom_phrases
            or ("hindi" in tokens and (tokens & roman_tokens or len(tokens) <= 3))
            or re.search(r"(switch|reply|talk|speak|tell).*(hindi|hinglish|roman)", t_norm)
        ):
            return LanguageEngine.HINDI_ROMAN
        return None

    # -----------------------------------------------------------------
    @staticmethod
    def handle_language(session, user_message):
        text      = str(user_message or "").strip()
        state     = LanguageEngine.load_state(getattr(session, "language_state_blob", None))
        mode      = getattr(session, "language_mode", None)
        confirmed = getattr(session, "language_confirmed", False)

        # If language already confirmed, only react to explicit re-selection
        if confirmed:
            requested_mode = LanguageEngine._detect_explicit_switch_request(text)
            if not requested_mode:
                return None
            if requested_mode == mode:
                same_mode_text = {
                    LanguageEngine.ENGLISH: "Already responding in English.",
                    LanguageEngine.HINDI_ROMAN: "Main Hindi mein hi jawab de raha hoon.",
                }
                return {
                    "response": {
                        "text": same_mode_text.get(mode, "Language already set."),
                        "keyboard": {"remove_keyboard": True},
                    },
                    "language_mode": mode,
                    "language_confirmed": True,
                    "state_blob": LanguageEngine.dump_state({"awaiting": False, "pending": None}),
                }

            if mode == LanguageEngine.HINDI_ROMAN:
                return {
                    "response": {
                        "text": "Aapne Hindi language choose kiya hai, toh aap Hindi mein baat kijiye.",
                        "keyboard": {"remove_keyboard": True},
                    },
                    "language_mode": mode,
                    "language_confirmed": True,
                    "state_blob": LanguageEngine.dump_state({"awaiting": False, "pending": None}),
                }

            script = "roman" if requested_mode == LanguageEngine.HINDI_ROMAN else "latin"
            switch_text = {
                LanguageEngine.ENGLISH: "Switched to English.",
                LanguageEngine.HINDI_ROMAN: "Hindi par switch kar diya gaya hai.",
            }
            return {
                "response": {
                    "text": switch_text.get(requested_mode, "Language switched."),
                    "keyboard": {"remove_keyboard": True},
                },
                "language_mode": requested_mode,
                "language_confirmed": True,
                "script": script,
                "step": "question",
                "state_blob": LanguageEngine.dump_state({"awaiting": False, "pending": None}),
            }

        # Button text to language mode map
        lang_button_map = {
            "english": LanguageEngine.ENGLISH,
            "hindi": LanguageEngine.HINDI_ROMAN,
            "\u0939\u093f\u0902\u0926\u0940": LanguageEngine.HINDI_ROMAN,
        }

        opening_prompts = {
            LanguageEngine.ENGLISH: "What would you like to ask today?",
            LanguageEngine.HINDI_ROMAN: "Aaj aap kya puchna chahenge?",
        }

        # Step A: User pressed a language button from /start keyboard
        chosen = lang_button_map.get(text.lower()) or lang_button_map.get(text)
        if chosen:
            script = "roman" if chosen == LanguageEngine.HINDI_ROMAN else "latin"
            return {
                "response": {
                    "text": opening_prompts[chosen],
                    "keyboard": {"remove_keyboard": True},
                },
                "language_mode": chosen,
                "language_confirmed": True,
                "script": script,
                "step": "question",
                "state_blob": LanguageEngine.dump_state({"awaiting": False, "pending": None}),
            }

        return None

    # -----------------------------------------------------------------
    @staticmethod
    def enforce_response_language(session, text):
        mode     = getattr(session, "language_mode", None)
        detected = LanguageEngine.detect_language(text)

        if mode == LanguageEngine.HINDI_ROMAN:
            return text  # trust LLM output for Roman Hindi
        if mode == LanguageEngine.ENGLISH and detected != LanguageEngine.ENGLISH:
            return "Let's continue in English.\n\n" + text
        return text
