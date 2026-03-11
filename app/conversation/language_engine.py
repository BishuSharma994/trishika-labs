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

    # ─────────────────────────────────────────────────────────────
    @staticmethod
    def detect_language(text: Any):
        t = str(text or "").strip()
        if any("\u0900" <= c <= "\u097F" for c in t):
            return LanguageEngine.HINDI_DEVANAGARI
        tokens = set(re.findall(r"[a-z']+", t.lower()))
        if tokens & LanguageEngine.HINDI_ROMAN_MARKERS:
            return LanguageEngine.HINDI_ROMAN
        return LanguageEngine.ENGLISH

    # ─────────────────────────────────────────────────────────────
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

    # ─────────────────────────────────────────────────────────────
    @staticmethod
    def handle_language(session, user_message):
        text      = str(user_message or "").strip()
        state     = LanguageEngine.load_state(getattr(session, "language_state_blob", None))
        mode      = getattr(session, "language_mode", None)
        confirmed = getattr(session, "language_confirmed", False)

        # ── If language is already confirmed, only react to explicit re-selection ──
        if confirmed:
            explicit_switches = {"english", "hindi", "हिंदी", "hindi (roman)"}
            if text.lower() not in explicit_switches and text not in explicit_switches:
                return None

        # ── Map from button text → language mode ──────────────────────────────────
        lang_button_map = {
            "english":      LanguageEngine.ENGLISH,
            "हिंदी":        LanguageEngine.HINDI_DEVANAGARI,
            "hindi (roman)":LanguageEngine.HINDI_ROMAN,
        }
        lang_confirm_prompts = {
            LanguageEngine.ENGLISH: (
                "You are writing in English.\n\nContinue?\n1 Yes\n2 Hindi Roman\n3 हिंदी"
            ),
            LanguageEngine.HINDI_ROMAN: (
                "Aap Hindi Roman mein baat kar rahe hain.\n\nContinue?\n1 Haan\n2 English\n3 हिंदी"
            ),
            LanguageEngine.HINDI_DEVANAGARI: (
                "आप हिंदी में लिख रहे हैं।\n\nजारी रखें?\n1 हाँ\n2 English\n3 Hindi Roman"
            ),
        }

        # ── Step A: User pressed a language button from /start keyboard ───────────
        chosen = lang_button_map.get(text.lower()) or lang_button_map.get(text)
        if chosen:
            return {
                "response":          lang_confirm_prompts[chosen],
                "language_mode":     chosen,
                "language_confirmed": False,
                "state_blob":        LanguageEngine.dump_state({"awaiting": True, "pending": chosen}),
            }

        # ── Step B: User replied 1/2/3 to confirm or switch language ─────────────
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

            if text in ("1", "haan", "yes", "हाँ", "ha"):
                final_lang = pending
            elif text in ("2", "3") and pending in switch_map:
                final_lang = switch_map[pending].get(text, pending)
            else:
                # Unrecognised reply — don't intercept, let main flow handle it
                return None

            script = "devanagari" if final_lang == LanguageEngine.HINDI_DEVANAGARI else "latin"

            confirmed_msgs = {
                LanguageEngine.ENGLISH: (
                    "Great! Let's continue in English.\n\n"
                    "Please share your birth details:\n"
                    "Example: 15-08-1990, 10:30 AM, Delhi"
                ),
                LanguageEngine.HINDI_ROMAN: (
                    "Achha! Hindi Roman mein baat karte hain.\n\n"
                    "Apni janm details bhejiye:\n"
                    "Example: 15-08-1990, 10:30 AM, Delhi"
                ),
                LanguageEngine.HINDI_DEVANAGARI: (
                    "ठीक है! हिंदी में बात करते हैं।\n\n"
                    "अपनी जन्म जानकारी भेजें:\n"
                    "उदाहरण: 15-08-1990, 10:30 AM, दिल्ली"
                ),
            }

            return {
                "response":           confirmed_msgs[final_lang],
                "language_mode":      final_lang,
                "language_confirmed": True,          # ← THE KEY FIX
                "script":             script,
                "step":               "birthdata",   # ← Advance the flow
                "state_blob":         LanguageEngine.dump_state({"awaiting": False, "pending": None}),
            }

        return None

    # ─────────────────────────────────────────────────────────────
    @staticmethod
    def enforce_response_language(session, text):
        mode     = getattr(session, "language_mode", None)
        detected = LanguageEngine.detect_language(text)

        if mode == LanguageEngine.HINDI_ROMAN:
            return text
        if mode == LanguageEngine.HINDI_DEVANAGARI and detected != LanguageEngine.HINDI_DEVANAGARI:
            return "चलिए हिंदी में बात जारी रखते हैं.\n\n" + text
        if mode == LanguageEngine.ENGLISH and detected != LanguageEngine.ENGLISH:
            return "Let's continue in English.\n\n" + text
        return text
