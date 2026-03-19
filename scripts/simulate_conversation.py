import sys
import types
from types import SimpleNamespace
from uuid import uuid4
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _install_runtime_stubs():
    sessions = {}

    class StubStateManager:
        @staticmethod
        def get_session(user_id):
            data = sessions.get(user_id)
            if not data:
                return None
            return SimpleNamespace(**data)

        @staticmethod
        def reload_session(user_id):
            return StubStateManager.get_session(user_id)

        @staticmethod
        def get_or_create_session(user_id):
            if user_id not in sessions:
                sessions[user_id] = {
                    "user_id": user_id,
                    "step": "start",
                    "dob": None,
                    "tob": None,
                    "place": None,
                    "gender": None,
                    "language": None,
                    "script": "latin",
                    "language_mode": None,
                    "language_confirmed": False,
                    "language_state_blob": None,
                    "consultation_state_blob": None,
                    "last_domain": None,
                    "conversation_phase": None,
                    "last_followup_question": None,
                    "persona_introduced": False,
                    "age": None,
                    "life_stage": None,
                    "user_goal": None,
                    "plan_tier": "free",
                    "profiles": None,
                    "pending_profile_name": None,
                    "active_profile_name": None,
                    "chart_data": None,
                    "theme_shown": False,
                }
            return SimpleNamespace(**sessions[user_id])

        @staticmethod
        def update_session(user_id, **fields):
            session = vars(StubStateManager.get_or_create_session(user_id)).copy()
            session.update(fields)
            sessions[user_id] = session
            return session

    class StubMemoryEngine:
        @staticmethod
        def clear(user_id):
            return None

        @staticmethod
        def add_user_message(user_id, text):
            return None

        @staticmethod
        def add_bot_message(user_id, text):
            return None

    class StubParashariEngine:
        @staticmethod
        def generate_chart(dob, tob, lat, lon):
            return {}

    state_manager_module = types.ModuleType("app.conversation.state_manager")
    state_manager_module.StateManager = StubStateManager

    memory_engine_module = types.ModuleType("app.conversation.memory_engine")
    memory_engine_module.MemoryEngine = StubMemoryEngine

    astro_engine_module = types.ModuleType("app.astro_engine")
    astro_engine_module.ParashariEngine = StubParashariEngine

    sys.modules["app.conversation.state_manager"] = state_manager_module
    sys.modules["app.conversation.memory_engine"] = memory_engine_module
    sys.modules["app.astro_engine"] = astro_engine_module

    return sessions


_SESSIONS = _install_runtime_stubs()

from app.conversation.dialog_engine import DialogEngine


def _mock_chart():
    return {
        "domain_scores": {
            "marriage": {
                "primary_driver": "Venus",
                "risk_factor": "Moon",
                "score": 54,
                "projection_next_year": 57,
            },
            "career": {
                "primary_driver": "Saturn",
                "risk_factor": "Mercury",
                "score": 61,
                "projection_next_year": 66,
            },
            "finance": {
                "primary_driver": "Jupiter",
                "risk_factor": "Mars",
                "score": 56,
                "projection_next_year": 59,
            },
            "health": {
                "primary_driver": "Moon",
                "risk_factor": "Saturn",
                "score": 53,
                "projection_next_year": 56,
            },
        },
        "current_dasha": {},
        "transit": {},
    }


DialogEngine.load_chart = staticmethod(lambda *_args, **_kwargs: _mock_chart())


SCENARIOS = [
    {
        "name": "Marriage Follow-up Recovery",
        "messages": [
            "/start",
            "Roman Hindi",
            "Marriage",
            "01/01/1993",
            "10:30 AM",
            "Delhi",
            "Male",
            "Bishu",
            "Haan",
            "Meri shaadi mein abhi kya dikh raha hai?",
            "Shaadi clarity ke liye kya karu?",
            "Mera already sadhi ho chuka hai?",
            "ji",
            "kissey?",
            "aisa v hota hai kiya ?",
            "Thik hai mera carrer mey kiya hai ?",
        ],
        "checks": [
            {"user": "Shaadi clarity ke liye kya karu?", "must_start_with": "1."},
            {"user": "Mera already sadhi ho chuka hai?", "must_include": "shaadi pehle se ho chuki hai"},
            {"user": "ji", "must_include": "shaant baat-cheet"},
            {"user": "kissey?", "must_include": "se aata hai"},
            {"user": "aisa v hota hai kiya ?", "must_include": "Haan, aisa hota hai"},
            {"user": "Thik hai mera carrer mey kiya hai ?", "must_include": "Observation: Saturn"},
        ],
        "expected_final_domain": "career",
    },
    {
        "name": "Finance Action and Timing",
        "messages": [
            "/start",
            "Roman Hindi",
            "Finance",
            "01/01/1993",
            "10:30 AM",
            "Delhi",
            "Male",
            "Bishu",
            "Haan",
            "Mere paise mein abhi kya dikh raha hai?",
            "kya karu?",
            "kab sudhar hoga?",
            "ji",
        ],
        "checks": [
            {"user": "kya karu?", "must_start_with": "1."},
            {"user": "kab sudhar hoga?", "must_include": "hafte"},
            {"user": "ji", "must_include": "spending control"},
        ],
        "expected_final_domain": "finance",
    },
    {
        "name": "English Career Follow-up",
        "messages": [
            "/start",
            "English",
            "Career",
            "01/01/1993",
            "10:30 AM",
            "Delhi",
            "Male",
            "Alex",
            "Yes",
            "What is happening in my career right now?",
            "What should I do?",
            "already working there but progress is slow",
            "how exactly?",
            "how long?",
        ],
        "checks": [
            {"user": "What should I do?", "must_start_with": "1."},
            {"user": "already working there but progress is slow", "must_include": "Understood."},
            {"user": "how exactly?", "must_include": "improves consistency"},
            {"user": "how long?", "must_include": "weeks"},
        ],
        "expected_final_domain": "career",
    },
]


def _score_scenario(transcript, expected_final_domain):
    score = 10.0
    issues = []
    replies = [item["bot"] for item in transcript if item["user"]]

    for previous, current in zip(replies, replies[1:]):
        if previous.strip() == current.strip():
            score -= 1.5
            issues.append("exact_repeat_reply")

    final_domain = transcript[-1].get("domain")
    if expected_final_domain and final_domain != expected_final_domain:
        score -= 2.0
        issues.append(f"wrong_final_domain:{final_domain}")

    for item in transcript:
        bot = item["bot"].strip()
        user = item["user"].strip()
        if not bot:
            score -= 2.0
            issues.append(f"empty_reply:{user}")
        if "Observation:" in bot and user.lower() in {"ji", "ok", "haan"}:
            score -= 1.0
            issues.append(f"unnecessary_full_template:{user}")

    return max(0.0, round(score, 2)), issues


def _run_scenario(scenario):
    user_id = f"sim-{uuid4()}"
    transcript = []

    for message in scenario["messages"]:
        response = DialogEngine.process(user_id, message)
        bot_text = response.get("text", "") if isinstance(response, dict) else str(response)
        domain = _SESSIONS.get(user_id, {}).get("last_domain")
        transcript.append({"user": message, "bot": bot_text, "domain": domain})

    score, issues = _score_scenario(transcript, scenario.get("expected_final_domain"))

    check_failures = []
    for check in scenario["checks"]:
        row = next((item for item in transcript if item["user"] == check["user"]), None)
        if not row:
            score -= 1.0
            check_failures.append(f"missing_step:{check['user']}")
            continue

        reply = row["bot"]
        must_include = check.get("must_include")
        if must_include and must_include.lower() not in reply.lower():
            score -= 1.0
            check_failures.append(f"missing_text:{check['user']}->{must_include}")

        must_start_with = check.get("must_start_with")
        if must_start_with and not reply.strip().startswith(must_start_with):
            score -= 1.0
            check_failures.append(f"wrong_format:{check['user']}")

    final_score = max(0.0, round(score, 2))
    return transcript, final_score, issues + check_failures


def main():
    scenario_scores = []

    for scenario in SCENARIOS:
        transcript, score, issues = _run_scenario(scenario)
        scenario_scores.append(score)
        print(f"\n=== {scenario['name']} ===")
        for item in transcript:
            print(f"USER: {item['user']}")
            print(f"BOT : {item['bot']}")
            print(f"DOMAIN: {item['domain']}")
            print("-")
        print(f"SCORE: {score}/10")
        print(f"ISSUES: {issues if issues else 'none'}")

    average = round(sum(scenario_scores) / len(scenario_scores), 2) if scenario_scores else 0.0
    print(f"\nOVERALL CONVERSATION RATING: {average}/10")


if __name__ == "__main__":
    main()
