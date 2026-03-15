import re
import sys
import types

# Stub swisseph for simulation-only runs
if "swisseph" not in sys.modules:
    swe_stub = types.SimpleNamespace(
        SUN=0,
        MOON=1,
        MARS=2,
        MERCURY=3,
        JUPITER=4,
        VENUS=5,
        SATURN=6,
        MEAN_NODE=7,
        set_ephe_path=lambda *args, **kwargs: None,
        julday=lambda *args, **kwargs: 0.0,
        calc_ut=lambda *args, **kwargs: ([0.0, 0.0, 0.0], 0),
        houses=lambda *args, **kwargs: ([0.0] * 12, [0.0] * 10),
    )
    sys.modules["swisseph"] = swe_stub

from app.conversation.dialog_engine import DialogEngine
from app.conversation.state_manager import StateManager
from app.conversation.quality_guard import ConversationQualityGuard
from app.conversation.language_engine import LanguageEngine
import os
import app.ai as ai


def _mock_reply(user_text, is_hindi):
    t = str(user_text or "").strip().lower()
    if not t:
        return "Kripya apna sawal bhejiye." if is_hindi else "Please share your question."

    timing = any(token in t for token in ("kab", "when", "time", "timing", "how long"))
    action = any(token in t for token in ("kya karu", "what should i do", "what to do", "guide"))
    selection_only = t in {"career", "finance", "health", "marriage", "shaadi"}

    if selection_only:
        return (
            "Career ke kis part par clarity chahte hain - job switch, promotion, ya current situation?"
            if is_hindi
            else "Which part of career do you want clarity on most right now - job switch, promotion, or your current situation?"
        )

    if timing:
        return (
            "Agle 2-3 mahine mein dheere dheere movement dikhne lagega. Jaldbazi se pehle options clear rakhiye."
            if is_hindi
            else "You should see a shift over the next 2-3 months. Keep your options clear before taking a fast decision."
        )

    if action:
        return (
            "Pehla, apni priority do goals par set kijiye. Doosra, agle 4-6 hafton tak ek consistent routine rakhiye."
            if is_hindi
            else "First, set two clear priorities. Second, keep a consistent routine for the next 4-6 weeks."
        )

    return (
        "Samajh raha hoon. Is phase mein pressure timing aur recognition ka hai, isliye progress slow lag sakti hai."
        if is_hindi
        else "I understand. In this phase the pressure is around timing and recognition, so progress can feel slow."
    )


def mock_ask_ai(messages_array):
    # Decide language from system instruction or user text
    sys_blob = "\n".join(msg.get("content", "") for msg in messages_array if msg.get("role") == "system")
    is_hindi = "IMPORTANT: You MUST reply in natural Hinglish" in sys_blob
    last_user = ""
    for msg in reversed(messages_array):
        if msg.get("role") == "user":
            last_user = msg.get("content", "")
            break
    return _mock_reply(last_user, is_hindi)


USE_REAL_API = os.getenv("USE_REAL_API", "").strip().lower() in {"1", "true", "yes"}

if not USE_REAL_API:
    ai.ask_ai = mock_ask_ai


def _mock_chart():
    return {
        "lagna": "Aries",
        "moon_sign": "Taurus",
        "current_dasha": "Mercury",
        "domain_scores": {
            "career": {"score": 60, "components": {}},
            "finance": {"score": 55, "components": {}},
            "marriage": {"score": 58, "components": {}},
            "health": {"score": 62, "components": {}},
        },
    }


DialogEngine.load_chart = staticmethod(lambda *_args, **_kwargs: _mock_chart())


def run_flow(user_id, steps):
    print(f"\n--- Simulation for {user_id} ---")
    for user_text in steps:
        result = DialogEngine.process(user_id, user_text, None)
        reply = result.get("text") if isinstance(result, dict) else str(result)
        session = StateManager.get_session(user_id)
        lang = getattr(session, "language_mode", LanguageEngine.ENGLISH) if session else LanguageEngine.ENGLISH
        script = getattr(session, "script", "latin") if session else "latin"
        score, issues = ConversationQualityGuard.score_reply(user_text, reply, lang, script)
        print(f"USER: {user_text}")
        print(f"BOT : {reply}")
        print(f"SCORE: {score} | issues: {issues}")
        print("-")


if __name__ == "__main__":
    hindi_steps = [
        "/start",
        "Hindi",
        "Kab shaadi hogi?",
        "06/12/1994",
        "03:45 AM",
        "Birpara, West Bengal, India",
        "Male",
        "Bishu Sharma",
        "Shaadi kab hogi?",
    ]

    english_steps = [
        "/start",
        "English",
        "When will I get new opportunities?",
        "06/12/1994",
        "03:45 AM",
        "Birpara, West Bengal, India",
        "Male",
        "Alex",
        "When will opportunities improve?",
    ]

    run_flow("sim_user_hindi", hindi_steps)
    run_flow("sim_user_english", english_steps)
