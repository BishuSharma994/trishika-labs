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
    def handle_language(session, user_message):
        text      = str(user_message or "").strip()
        state     = LanguageEngine.load_state(getattr(session, "language_state_blob", None))
        mode      = getattr(session, "language_mode", None)
        confirmed = getattr(session, "language_confirmed", False)

        # If language already confirmed, only react to explicit re-selection
        if confirmed:
            explicit_switches = {"english", "hindi", "\u0939\u093f\u0902\u0926\u0940", "hindi (roman)"}
            if text.lower() not in explicit_switches and text not in explicit_switches:
                return None

        # Button text to language mode map
        lang_button_map = {
            "english":       LanguageEngine.ENGLISH,
            "\u0939\u093f\u0902\u0926\u0940": LanguageEngine.HINDI_DEVANAGARI,
            "hindi (roman)": LanguageEngine.HINDI_ROMAN,
        }

        # Confirm prompt text shown after user picks a language
        confirm_texts = {
            LanguageEngine.ENGLISH:          "You are writing in English.\n\nContinue?",
            LanguageEngine.HINDI_ROMAN:      "Aap Hindi Roman mein baat kar rahe hain.\n\nJaari rakhein?",
            LanguageEngine.HINDI_DEVANAGARI: "\u0906\u092a \u0939\u093f\u0902\u0926\u0940 \u092e\u0947\u0902 \u0932\u093f\u0916 \u0930\u0939\u0947 \u0939\u0948\u0902\u0964\n\n\u091c\u093e\u0930\u0940 \u0930\u0916\u0947\u0902?",
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
                    "Great! Let's continue in English.\n\n"
                    "Tell me whose chart you want to read."
                ),
                LanguageEngine.HINDI_ROMAN: (
                    "Achha! Hindi Roman mein baat karte hain.\n\n"
                    "Batayiye aap kiski kundli dekhna chahte hain."
                ),
                LanguageEngine.HINDI_DEVANAGARI: (
                    "\u0920\u0940\u0915 \u0939\u0948! \u0939\u093f\u0902\u0926\u0940 \u092e\u0947\u0902 \u092c\u093e\u0924 \u0915\u0930\u0924\u0947 \u0939\u0948\u0902\u0964\n\n"
                    "\u092c\u0924\u093e\u0907\u090f \u0906\u092a \u0915\u093f\u0938\u0915\u0940 \u0915\u0941\u0902\u0921\u0932\u0940 \u0926\u0947\u0916\u0928\u093e \u091a\u093e\u0939\u0924\u0947 \u0939\u0948\u0902\u0964"
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
