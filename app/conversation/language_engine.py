import json
import re
from typing import Any


class LanguageEngine:
    ENGLISH = "english"
    HINDI_ROMAN = "hindi_roman"
    HINDI_DEVANAGARI = "hindi_devanagari"

    _STATE_KEY = "language_control"
    _MODE_ORDER = [ENGLISH, HINDI_ROMAN, HINDI_DEVANAGARI]

    _HINDI_ROMAN_HINTS = {
        "shaadi",
        "kya",
        "kyu",
        "kaise",
        "nahi",
        "hai",
        "aap",
        "mera",
        "meri",
        "kar",
        "ho",
        "chuki",
        "haan",
        "kripya",
        "janm",
        "sawal",
        "samajh",
        "bataiye",
        "kyunki",
        "isse",
        "abhi",
        "mein",
        "se",
        "ki",
        "ke",
    }

    _SHORT_NON_SWITCH_INPUTS = {
        "1",
        "2",
        "3",
        "4",
        "ok",
        "okay",
        "haan",
        "ha",
        "yes",
        "no",
        "nahi",
        "nah",
        "hmm",
        "h",
        "y",
        "n",
    }

    @staticmethod
    def check_devanagari(text: Any) -> bool:
        t = str(text or "")
        return any("\u0900" <= ch <= "\u097F" for ch in t)

    @staticmethod
    def check_hindi_roman(text: Any) -> bool:
        t = str(text or "").strip().lower()
        if not t:
            return False

        if LanguageEngine.check_devanagari(t):
            return False

        tokens = set(re.findall(r"[a-z']+", t))
        if not tokens:
            return False

        hint_hits = len(tokens & LanguageEngine._HINDI_ROMAN_HINTS)
        if hint_hits >= 1:
            return True

        bigram_hits = 0
        for phrase in ("ho chuki", "kar raha", "kar rahi", "kya hai", "kaise hai"):
            if phrase in t:
                bigram_hits += 1

        return bigram_hits > 0

    @staticmethod
    def detect_language(text: Any) -> str:
        if LanguageEngine.check_devanagari(text):
            return LanguageEngine.HINDI_DEVANAGARI

        if LanguageEngine.check_hindi_roman(text):
            return LanguageEngine.HINDI_ROMAN

        return LanguageEngine.ENGLISH

    @staticmethod
    def _base_state() -> dict[str, Any]:
        return {
            "consultation_state": True,
            "version": 2,
            "active_domain": None,
            "domain_memory": {},
            "domain_insights": {},
            "memory": {},
        }

    @staticmethod
    def _load_state(blob: Any) -> dict[str, Any]:
        if not blob:
            return LanguageEngine._base_state()

        try:
            parsed = json.loads(str(blob))
        except Exception:
            return LanguageEngine._base_state()

        if not isinstance(parsed, dict):
            return LanguageEngine._base_state()

        if not parsed.get("consultation_state"):
            return LanguageEngine._base_state()

        parsed.setdefault("version", 2)
        parsed.setdefault("active_domain", None)
        parsed.setdefault("domain_memory", {})
        parsed.setdefault("domain_insights", {})
        parsed.setdefault("memory", {})
        return parsed

    @staticmethod
    def _dump_state(state: dict[str, Any]) -> str:
        return json.dumps(state, ensure_ascii=False, separators=(",", ":"))

    @staticmethod
    def _ensure_language_state(state: dict[str, Any]) -> dict[str, Any]:
        bucket = state.get(LanguageEngine._STATE_KEY)
        if not isinstance(bucket, dict):
            bucket = {}

        bucket.setdefault("awaiting_confirmation", False)
        bucket.setdefault("pending_mode", None)
        bucket.setdefault("previous_mode", None)
        bucket.setdefault("prompt_type", None)
        state[LanguageEngine._STATE_KEY] = bucket
        return bucket

    @staticmethod
    def _mode_from_session(session: Any) -> str | None:
        mode = str(getattr(session, "language_mode", "") or "").strip().lower()
        if mode in LanguageEngine._MODE_ORDER:
            return mode

        language = str(getattr(session, "language", "") or "").strip().lower()
        script = str(getattr(session, "script", "") or "").strip().lower()

        if language == "hi" and script == "roman":
            return LanguageEngine.HINDI_ROMAN

        if language == "hi" and script == "devanagari":
            return LanguageEngine.HINDI_DEVANAGARI

        if language == "en":
            return LanguageEngine.ENGLISH

        return None

    @staticmethod
    def _mode_to_lang_script(mode: str | None) -> tuple[str | None, str | None]:
        if mode == LanguageEngine.HINDI_ROMAN:
            return "hi", "roman"

        if mode == LanguageEngine.HINDI_DEVANAGARI:
            return "hi", "devanagari"

        if mode == LanguageEngine.ENGLISH:
            return "en", "latin"

        return None, None

    @staticmethod
    def _mode_label(mode: str | None) -> str:
        mapping = {
            LanguageEngine.ENGLISH: "English",
            LanguageEngine.HINDI_ROMAN: "Hindi Roman",
            LanguageEngine.HINDI_DEVANAGARI: "हिंदी",
        }
        return mapping.get(mode, "language")

    @staticmethod
    def _ack_message(mode: str | None) -> str:
        if mode == LanguageEngine.HINDI_ROMAN:
            return "Theek hai. Hum Hindi Roman mein continue karenge."

        if mode == LanguageEngine.HINDI_DEVANAGARI:
            return "ठीक है। हम हिंदी में ही आगे बात करेंगे।"

        return "Great. We will continue in English."

    @staticmethod
    def _initial_confirmation_prompt(mode: str) -> str:
        if mode == LanguageEngine.HINDI_ROMAN:
            return (
                "Aap Hindi Roman mein baat kar rahe hain.\n\n"
                "Kya isi language mein consultation continue karein?\n"
                "1 Haan\n"
                "2 English\n"
                "3 हिंदी"
            )

        if mode == LanguageEngine.HINDI_DEVANAGARI:
            return (
                "आप हिंदी में लिख रहे हैं।\n\n"
                "क्या इसी भाषा में consultation जारी रखें?\n"
                "1 हाँ\n"
                "2 English\n"
                "3 Hindi Roman"
            )

        return (
            "You are writing in English.\n\n"
            "Do you want to continue in English?\n"
            "1 Yes\n"
            "2 Hindi Roman\n"
            "3 हिंदी"
        )

    @staticmethod
    def _drift_confirmation_prompt(previous_mode: str, pending_mode: str) -> str:
        return (
            f"You switched to {LanguageEngine._mode_label(pending_mode)}.\n\n"
            f"Do you want to continue in {LanguageEngine._mode_label(pending_mode)}?\n"
            "1 Yes\n"
            f"2 Continue in {LanguageEngine._mode_label(previous_mode)}"
        )

    @staticmethod
    def _explicit_mode_from_text(text: str) -> str | None:
        t = str(text or "").strip().lower()
        if not t:
            return None

        if LanguageEngine.check_devanagari(t):
            if "हिं" in t:
                return LanguageEngine.HINDI_DEVANAGARI

        if "english" in t:
            return LanguageEngine.ENGLISH

        if "hindi roman" in t or "roman" in t:
            return LanguageEngine.HINDI_ROMAN

        if "hindi" in t:
            return LanguageEngine.HINDI_DEVANAGARI

        return None

    @staticmethod
    def _resolve_initial_numeric_choice(pending_mode: str, text: str) -> str | None:
        t = str(text or "").strip().lower()
        if t not in {"1", "2", "3"}:
            return None

        if t == "1":
            return pending_mode

        if pending_mode == LanguageEngine.ENGLISH:
            return LanguageEngine.HINDI_ROMAN if t == "2" else LanguageEngine.HINDI_DEVANAGARI

        if pending_mode == LanguageEngine.HINDI_ROMAN:
            return LanguageEngine.ENGLISH if t == "2" else LanguageEngine.HINDI_DEVANAGARI

        return LanguageEngine.ENGLISH if t == "2" else LanguageEngine.HINDI_ROMAN

    @staticmethod
    def _resolve_drift_choice(previous_mode: str, pending_mode: str, text: str) -> str | None:
        t = str(text or "").strip().lower()

        if t in {"1", "yes", "haan", "ha", "y"}:
            return pending_mode

        if t in {"2", "no", "n", "nah", "nahi"}:
            return previous_mode

        explicit = LanguageEngine._explicit_mode_from_text(t)
        if explicit in LanguageEngine._MODE_ORDER:
            return explicit

        return None

    @staticmethod
    def _message_can_trigger_drift(text: str) -> bool:
        t = str(text or "").strip().lower()
        if not t:
            return False

        if t in LanguageEngine._SHORT_NON_SWITCH_INPUTS:
            return False

        if re.fullmatch(r"[0-9\s\-:/]+", t):
            return False

        return True

    @staticmethod
    def _result(
        response: str | None,
        consumed: bool,
        mode: str | None,
        confirmed: bool,
        state: dict[str, Any],
    ) -> dict[str, Any]:
        language, script = LanguageEngine._mode_to_lang_script(mode)
        return {
            "response": response,
            "consumed": consumed,
            "language_mode": mode,
            "language_confirmed": bool(confirmed),
            "language": language,
            "script": script,
            "state_blob": LanguageEngine._dump_state(state),
        }

    @staticmethod
    def handle_language(session: Any, user_message: Any) -> dict[str, Any]:
        text = str(user_message or "").strip()

        state = LanguageEngine._load_state(getattr(session, "last_followup_question", None))
        lang_state = LanguageEngine._ensure_language_state(state)

        mode = LanguageEngine._mode_from_session(session)
        confirmed = bool(getattr(session, "language_confirmed", False))

        if mode and str(getattr(session, "language_mode", "") or "").strip().lower() != mode:
            # Backfill missing persisted mode from old language/script fields.
            state.setdefault("memory", {})["language_mode_backfill"] = mode

        if text.startswith("/"):
            return LanguageEngine._result(
                response=None,
                consumed=False,
                mode=mode,
                confirmed=confirmed,
                state=state,
            )

        awaiting = bool(lang_state.get("awaiting_confirmation"))
        pending_mode = lang_state.get("pending_mode")
        previous_mode = lang_state.get("previous_mode") or mode
        prompt_type = lang_state.get("prompt_type")

        if awaiting and pending_mode in LanguageEngine._MODE_ORDER:
            selected_mode = None

            if prompt_type == "drift":
                selected_mode = LanguageEngine._resolve_drift_choice(previous_mode, pending_mode, text)
            else:
                selected_mode = LanguageEngine._resolve_initial_numeric_choice(pending_mode, text)
                if selected_mode is None:
                    explicit = LanguageEngine._explicit_mode_from_text(text)
                    if explicit in LanguageEngine._MODE_ORDER:
                        selected_mode = explicit

            if selected_mode in LanguageEngine._MODE_ORDER:
                mode = selected_mode
                confirmed = True
                lang_state["awaiting_confirmation"] = False
                lang_state["pending_mode"] = None
                lang_state["previous_mode"] = None
                lang_state["prompt_type"] = None
                return LanguageEngine._result(
                    response=LanguageEngine._ack_message(mode),
                    consumed=True,
                    mode=mode,
                    confirmed=confirmed,
                    state=state,
                )

            if prompt_type == "drift" and previous_mode in LanguageEngine._MODE_ORDER:
                prompt = LanguageEngine._drift_confirmation_prompt(previous_mode, pending_mode)
            else:
                prompt = LanguageEngine._initial_confirmation_prompt(pending_mode)

            return LanguageEngine._result(
                response=prompt,
                consumed=True,
                mode=mode,
                confirmed=confirmed,
                state=state,
            )

        detected_mode = LanguageEngine.detect_language(text)

        if not confirmed or mode not in LanguageEngine._MODE_ORDER:
            lang_state["awaiting_confirmation"] = True
            lang_state["pending_mode"] = detected_mode
            lang_state["previous_mode"] = mode
            lang_state["prompt_type"] = "initial"
            return LanguageEngine._result(
                response=LanguageEngine._initial_confirmation_prompt(detected_mode),
                consumed=True,
                mode=mode,
                confirmed=False,
                state=state,
            )

        if (
            detected_mode in LanguageEngine._MODE_ORDER
            and detected_mode != mode
            and LanguageEngine._message_can_trigger_drift(text)
        ):
            lang_state["awaiting_confirmation"] = True
            lang_state["pending_mode"] = detected_mode
            lang_state["previous_mode"] = mode
            lang_state["prompt_type"] = "drift"
            return LanguageEngine._result(
                response=LanguageEngine._drift_confirmation_prompt(mode, detected_mode),
                consumed=True,
                mode=mode,
                confirmed=True,
                state=state,
            )

        return LanguageEngine._result(
            response=None,
            consumed=False,
            mode=mode,
            confirmed=True,
            state=state,
        )

    @staticmethod
    def enforce_response_language(session: Any, text: Any) -> str:
        raw = str(text or "").strip()
        if not raw:
            return raw

        mode = LanguageEngine._mode_from_session(session)
        if mode not in LanguageEngine._MODE_ORDER:
            return raw

        detected = LanguageEngine.detect_language(raw)

        if mode == LanguageEngine.ENGLISH:
            if detected == LanguageEngine.ENGLISH:
                return raw
            return f"Let's continue in English.\n\n{raw}"

        if mode == LanguageEngine.HINDI_ROMAN:
            if detected == LanguageEngine.HINDI_ROMAN:
                return raw
            return f"Chaliye Hindi Roman mein continue karte hain.\n\n{raw}"

        if detected == LanguageEngine.HINDI_DEVANAGARI:
            return raw

        return f"चलिए हिंदी में ही आगे बात करते हैं।\n\n{raw}"
