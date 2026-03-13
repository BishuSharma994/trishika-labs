import json
import re
from typing import Any

from app.conversation.profile_manager import ProfileManager


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
        hindi_dev_phrases = {
            "hindi",
            "हिंदी",
            "in hindi",
            "hindi me",
            "hindi mein",
            "switch to hindi",
        }
        hindi_rom_phrases = {
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
            or ("hindi" in tokens and tokens & roman_tokens)
            or re.search(r"(switch|reply|talk|speak).*(hindi roman|roman hindi|hinglish)", t_norm)
        ):
            return LanguageEngine.HINDI_ROMAN
        if (
            t_norm in hindi_dev_phrases
            or (tokens & hindi_tokens and len(tokens) <= 3)
            or re.search(r"(reply|speak|talk|switch|tell).*(hindi)", t_norm)
        ):
            return LanguageEngine.HINDI_DEVANAGARI
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
                    LanguageEngine.HINDI_ROMAN: "Main pehle se Hindi Roman mein jawab de raha hoon.",
                    LanguageEngine.HINDI_DEVANAGARI: "मैं पहले से हिंदी में उत्तर दे रहा हूँ।",
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

            script = "devanagari" if requested_mode == LanguageEngine.HINDI_DEVANAGARI else ("roman" if requested_mode == LanguageEngine.HINDI_ROMAN else "latin")
            switch_text = {
                LanguageEngine.ENGLISH: "Switched to English.",
                LanguageEngine.HINDI_ROMAN: "Hindi Roman par switch kar diya gaya hai.",
                LanguageEngine.HINDI_DEVANAGARI: "हिंदी पर स्विच कर दिया गया है।",
            }
            return {
                "response": {
                    "text": switch_text[requested_mode],
                    "keyboard": {"remove_keyboard": True},
                },
                "language_mode": requested_mode,
                "language_confirmed": True,
                "script": script,
                "state_blob": LanguageEngine.dump_state({"awaiting": False, "pending": None}),
            }

        # Button text to language mode map
        lang_button_map = {
            "english":       LanguageEngine.ENGLISH,
            "\u0939\u093f\u0902\u0926\u0940": LanguageEngine.HINDI_DEVANAGARI,
            "hindi (roman)": LanguageEngine.HINDI_ROMAN,
        }

        # Confirm prompt text shown after user picks a language
        confirm_texts = {
            LanguageEngine.ENGLISH:          "We will continue in English.\n\nShall we proceed?",
            LanguageEngine.HINDI_ROMAN:      "Hum Hindi Roman mein baat karenge.\n\nAage badhein?",
            LanguageEngine.HINDI_DEVANAGARI: "\u0939\u092e \u0939\u093f\u0902\u0926\u0940 \u092e\u0947\u0902 \u092c\u093e\u0924 \u0915\u0930\u0947\u0902\u0917\u0947\u0964\n\n\u0906\u0917\u0947 \u092c\u0922\u093c\u0947\u0902?",
        }

        # Confirm keyboards language-aware
        confirm_keyboards = {
            LanguageEngine.ENGLISH:          [["1 Yes"],  ["2 Hindi Roman"], ["3 \u0939\u093f\u0902\u0926\u0940"]],
            LanguageEngine.HINDI_ROMAN:      [["1 Haan"], ["2 English"],     ["3 \u0939\u093f\u0902\u0926\u0940"]],
            LanguageEngine.HINDI_DEVANAGARI: [["1 \u0939\u093e\u0901"], ["2 English"], ["3 Hindi Roman"]],
        }

        # Step A: User pressed a language button from /start keyboard
        chosen = lang_button_map.get(text.lower()) or lang_button_map.get(text)
        if chosen:
            return {
                "response": {
                    "text": confirm_texts[chosen],
                    "keyboard": {
                        "keyboard": confirm_keyboards[chosen],
                        "resize_keyboard": True,
                        "one_time_keyboard": True,
                    },
                },
                "language_mode": chosen,
                "language_confirmed": False,
                "state_blob": LanguageEngine.dump_state({"awaiting": True, "pending": chosen}),
            }

        # Step B: User replied 1/2/3 to confirm or switch
        if state.get("awaiting") and not confirmed:
            pending = state.get("pending") or mode

            switch_map = {
                LanguageEngine.ENGLISH: {
                    "2": LanguageEngine.HINDI_ROMAN,
                    "3": LanguageEngine.HINDI_DEVANAGARI,
                },
                LanguageEngine.HINDI_ROMAN: {
                    "2": LanguageEngine.ENGLISH,
                    "3": LanguageEngine.HINDI_DEVANAGARI,
                },
                LanguageEngine.HINDI_DEVANAGARI: {
                    "2": LanguageEngine.ENGLISH,
                    "3": LanguageEngine.HINDI_ROMAN,
                },
            }

            t_lower = text.lower().strip()

            if t_lower in ("1 haan", "1 yes", "1 \u0939\u093e\u0901", "1 ha", "1", "haan", "yes", "\u0939\u093e\u0901", "ha"):
                final_lang = pending
            elif t_lower in ("2", "2 english", "2 hindi roman"):
                final_lang = switch_map.get(pending, {}).get("2", pending)
            elif t_lower in ("3", "3 \u0939\u093f\u0902\u0926\u0940", "3 hindi roman"):
                final_lang = switch_map.get(pending, {}).get("3", pending)
            else:
                return None  # Unrecognised reply, let main flow handle it

            if final_lang == LanguageEngine.HINDI_DEVANAGARI:
                script = "devanagari"
            elif final_lang == LanguageEngine.HINDI_ROMAN:
                script = "roman"
            else:
                script = "latin"

            confirmed_texts = {
                LanguageEngine.ENGLISH: (
                    "Alright, we'll continue in English."
                ),
                LanguageEngine.HINDI_ROMAN: (
                    "Theek hai, Hindi Roman mein hi baat karte hain."
                ),
                LanguageEngine.HINDI_DEVANAGARI: (
                    "\u0920\u0940\u0915 \u0939\u0948, \u0939\u092e \u0939\u093f\u0902\u0926\u0940 \u092e\u0947\u0902 \u0939\u0940 \u092c\u093e\u0924 \u0915\u0930\u0947\u0902\u0917\u0947\u0964"
                ),
            }
            pm_lang = (
                "hi"
                if final_lang in {LanguageEngine.HINDI_ROMAN, LanguageEngine.HINDI_DEVANAGARI}
                else "en"
            )
            pm_script = (
                "devanagari"
                if final_lang == LanguageEngine.HINDI_DEVANAGARI
                else "roman" if final_lang == LanguageEngine.HINDI_ROMAN else "latin"
            )
            declaration_prompt = ProfileManager.declaration_prompt(pm_lang, pm_script)
            declaration_keyboard = ProfileManager.declaration_keyboard(pm_lang, pm_script)

            return {
                "response": {
                    "text": f"{confirmed_texts[final_lang]}\n\n{declaration_prompt}",
                    "keyboard": {
                        "keyboard": declaration_keyboard,
                        "resize_keyboard": True,
                        "one_time_keyboard": True,
                    },
                },
                "language_mode": final_lang,
                "language_confirmed": True,
                "script": script,
                "step": "profile_scope",
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
        if mode == LanguageEngine.HINDI_DEVANAGARI and detected != LanguageEngine.HINDI_DEVANAGARI:
            return "\u091a\u0932\u093f\u090f \u0939\u093f\u0902\u0926\u0940 \u092e\u0947\u0902 \u092c\u093e\u0924 \u091c\u093e\u0930\u0940 \u0930\u0916\u0924\u0947 \u0939\u0948\u0902.\n\n" + text
        if mode == LanguageEngine.ENGLISH and detected != LanguageEngine.ENGLISH:
            return "Let's continue in English.\n\n" + text
        return text
