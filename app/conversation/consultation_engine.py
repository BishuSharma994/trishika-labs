import json
import re


class ConsultationEngine:
    STATE_DOMAIN_ENTRY = "STATE_DOMAIN_ENTRY"
    STAGE_CHART_READING = "STAGE_CHART_READING"
    STAGE_SITUATION_ANALYSIS = "STAGE_SITUATION_ANALYSIS"
    STAGE_STRATEGY_GUIDANCE = "STAGE_STRATEGY_GUIDANCE"
    STAGE_ACTION_PLAN = "STAGE_ACTION_PLAN"

    _STATE_VERSION = 1
    _STATE_MARKER = "consultation_state"
    _MAX_RESPONSE_WORDS = 160

    _DOMAIN_SIGNALS = {
        "marriage": {
            "houses": "7th house and Navamsa",
            "planets": "Venus and Jupiter",
            "timing_flag": "marriage_window_active",
        },
        "career": {
            "houses": "10th and 6th houses",
            "planets": "Saturn, Sun, and Mercury",
            "timing_flag": "career_window_active",
        },
        "finance": {
            "houses": "2nd, 11th, and 5th houses",
            "planets": "Jupiter, Venus, and Mercury",
            "timing_flag": None,
        },
        "health": {
            "houses": "1st, 6th, and 8th houses",
            "planets": "Sun, Moon, and Mars",
            "timing_flag": None,
        },
    }

    _DOMAIN_QUESTIONS = {
        "marriage": {
            "entry": {
                "key": "relationship_status",
                "en": (
                    "To guide your marriage question accurately, I first need your current situation.\n\n"
                    "What fits best?\n"
                    "1. Single\n"
                    "2. In a relationship\n"
                    "3. Already married"
                ),
                "dev": (
                    "Shaadi ke sawal par sahi guidance dene ke liye pehle aapki current situation samajhna zaroori hai.\n\n"
                    "Kaunsi condition fit hoti hai?\n"
                    "1. Single\n"
                    "2. Relationship mein\n"
                    "3. Already married"
                ),
                "rom": (
                    "Shaadi ke sawal par sahi guidance dene ke liye pehle aapki current situation samajhna zaroori hai.\n\n"
                    "Kaunsi condition fit hoti hai?\n"
                    "1. Single\n"
                    "2. Relationship mein\n"
                    "3. Already married"
                ),
                "choices": [
                    ("single", ["single", "unmarried", "not married", "अविवाहित"]),
                    ("relationship", ["relationship", "dating", "partner", "girlfriend", "boyfriend", "रिलेशन", "संबंध"]),
                    ("married", ["married", "already married", "wife", "husband", "विवाहित", "शादीशुदा", "shaadi ho"]),
                ],
            },
            "secondary": {
                "key": "proposal_flow",
                "en": (
                    "How are proposals or progress moving right now?\n"
                    "1. Active\n"
                    "2. Slow/occasional\n"
                    "3. Stuck"
                ),
                "dev": (
                    "Abhi proposals ya progress kis speed se chal rahi hai?\n"
                    "1. Active\n"
                    "2. Slow/occasional\n"
                    "3. Stuck"
                ),
                "rom": (
                    "Abhi proposals ya progress kis speed se chal rahi hai?\n"
                    "1. Active\n"
                    "2. Slow/occasional\n"
                    "3. Stuck"
                ),
                "choices": [
                    ("active", ["active", "yes", "regular", "aa rahe", "ho rahe"]),
                    ("slow", ["slow", "occasional", "few", "kabhi", "delay"]),
                    ("stuck", ["stuck", "none", "no", "blocked", "not", "nahi"]),
                ],
            },
        },
        "career": {
            "entry": {
                "key": "career_status",
                "en": (
                    "For career guidance, I need your present work context first.\n\n"
                    "Choose one:\n"
                    "1. Employed\n"
                    "2. Job search\n"
                    "3. Planning switch"
                ),
                "dev": (
                    "Career guidance ke liye pehle aapka current work context clear karna zaroori hai.\n\n"
                    "Ek option choose kariye:\n"
                    "1. Employed\n"
                    "2. Job search\n"
                    "3. Planning switch"
                ),
                "rom": (
                    "Career guidance ke liye pehle aapka current work context clear karna zaroori hai.\n\n"
                    "Ek option choose kariye:\n"
                    "1. Employed\n"
                    "2. Job search\n"
                    "3. Planning switch"
                ),
                "choices": [
                    ("employed", ["employed", "working", "job", "office", "currently working"]),
                    ("search", ["search", "looking", "unemployed", "job hunt"]),
                    ("switch", ["switch", "change", "new role", "new job"]),
                ],
            },
            "secondary": {
                "key": "growth_state",
                "en": (
                    "How do you feel your growth right now?\n"
                    "1. Good momentum\n"
                    "2. Stagnant\n"
                    "3. High pressure"
                ),
                "dev": (
                    "Abhi growth ka pattern kaisa lag raha hai?\n"
                    "1. Good momentum\n"
                    "2. Stagnant\n"
                    "3. High pressure"
                ),
                "rom": (
                    "Abhi growth ka pattern kaisa lag raha hai?\n"
                    "1. Good momentum\n"
                    "2. Stagnant\n"
                    "3. High pressure"
                ),
                "choices": [
                    ("good", ["good", "momentum", "growing", "positive"]),
                    ("stagnant", ["stagnant", "slow", "stuck", "flat"]),
                    ("pressure", ["pressure", "stress", "toxic", "overload"]),
                ],
            },
        },
        "finance": {
            "entry": {
                "key": "income_state",
                "en": (
                    "For finance guidance, I need one context point first.\n\n"
                    "Your current income flow is:\n"
                    "1. Stable\n"
                    "2. Fluctuating\n"
                    "3. Uncertain/new"
                ),
                "dev": (
                    "Finance guidance ke liye pehle ek context point chahiye.\n\n"
                    "Aapka current income flow kaisa hai?\n"
                    "1. Stable\n"
                    "2. Fluctuating\n"
                    "3. Uncertain/new"
                ),
                "rom": (
                    "Finance guidance ke liye pehle ek context point chahiye.\n\n"
                    "Aapka current income flow kaisa hai?\n"
                    "1. Stable\n"
                    "2. Fluctuating\n"
                    "3. Uncertain/new"
                ),
                "choices": [
                    ("stable", ["stable", "regular", "consistent"]),
                    ("fluctuating", ["fluctuating", "irregular", "up down", "variable"]),
                    ("uncertain", ["uncertain", "new", "not sure", "unstable"]),
                ],
            },
            "secondary": {
                "key": "expense_state",
                "en": (
                    "How are expenses behaving now?\n"
                    "1. Controlled\n"
                    "2. Random spikes\n"
                    "3. Debt pressure"
                ),
                "dev": (
                    "Abhi expenses ka pattern kaisa hai?\n"
                    "1. Controlled\n"
                    "2. Random spikes\n"
                    "3. Debt pressure"
                ),
                "rom": (
                    "Abhi expenses ka pattern kaisa hai?\n"
                    "1. Controlled\n"
                    "2. Random spikes\n"
                    "3. Debt pressure"
                ),
                "choices": [
                    ("controlled", ["controlled", "managed", "under control"]),
                    ("spikes", ["spike", "random", "unplanned", "high"]),
                    ("debt", ["debt", "loan", "emi", "liability"]),
                ],
            },
        },
        "health": {
            "entry": {
                "key": "health_focus",
                "en": (
                    "For health guidance, I first need your main concern area.\n\n"
                    "Pick one:\n"
                    "1. Stress/mental load\n"
                    "2. Lifestyle imbalance\n"
                    "3. Specific medical issue"
                ),
                "dev": (
                    "Health guidance ke liye pehle main concern area clear karna zaroori hai.\n\n"
                    "Ek option choose kariye:\n"
                    "1. Stress/mental load\n"
                    "2. Lifestyle imbalance\n"
                    "3. Specific medical issue"
                ),
                "rom": (
                    "Health guidance ke liye pehle main concern area clear karna zaroori hai.\n\n"
                    "Ek option choose kariye:\n"
                    "1. Stress/mental load\n"
                    "2. Lifestyle imbalance\n"
                    "3. Specific medical issue"
                ),
                "choices": [
                    ("stress", ["stress", "anxiety", "mental", "तनाव"]),
                    ("lifestyle", ["lifestyle", "sleep", "diet", "routine"]),
                    ("medical", ["medical", "issue", "disease", "illness", "diagnosis"]),
                ],
            },
            "secondary": {
                "key": "symptom_pattern",
                "en": (
                    "In the last 3 months, this pattern is:\n"
                    "1. Improving\n"
                    "2. Same\n"
                    "3. Worsening"
                ),
                "dev": (
                    "Last 3 months mein yeh pattern kaisa raha?\n"
                    "1. Improving\n"
                    "2. Same\n"
                    "3. Worsening"
                ),
                "rom": (
                    "Last 3 months mein yeh pattern kaisa raha?\n"
                    "1. Improving\n"
                    "2. Same\n"
                    "3. Worsening"
                ),
                "choices": [
                    ("improving", ["improving", "better", "recover", "improved"]),
                    ("same", ["same", "stable", "no change"]),
                    ("worse", ["worse", "worsening", "bad", "decline"]),
                ],
            },
        },
    }

    _DOMAIN_VALUE_LABELS = {
        "marriage": {
            "relationship_status": {
                "single": "currently single",
                "relationship": "currently in a relationship",
                "married": "already married",
            },
            "proposal_flow": {
                "active": "proposal flow is active",
                "slow": "proposal flow is slow",
                "stuck": "proposal flow is blocked",
            },
        },
        "career": {
            "career_status": {
                "employed": "currently employed",
                "search": "actively searching",
                "switch": "planning a switch",
            },
            "growth_state": {
                "good": "growth feels active",
                "stagnant": "growth feels stagnant",
                "pressure": "work pressure feels high",
            },
        },
        "finance": {
            "income_state": {
                "stable": "income is stable",
                "fluctuating": "income is fluctuating",
                "uncertain": "income flow feels uncertain",
            },
            "expense_state": {
                "controlled": "expenses are controlled",
                "spikes": "expenses spike unexpectedly",
                "debt": "debt pressure is present",
            },
        },
        "health": {
            "health_focus": {
                "stress": "stress is the main concern",
                "lifestyle": "lifestyle balance is the concern",
                "medical": "a specific medical issue is the concern",
            },
            "symptom_pattern": {
                "improving": "pattern is improving",
                "same": "pattern is stable",
                "worse": "pattern is worsening",
            },
        },
    }

    @staticmethod
    def _is_hi_dev(language, script):
        return language == "hi" and script == "devanagari"

    @staticmethod
    def _is_hi_rom(language, script):
        return language == "hi" and script == "roman"

    @staticmethod
    def _lang_key(language, script):
        if ConsultationEngine._is_hi_dev(language, script):
            return "dev"
        if ConsultationEngine._is_hi_rom(language, script):
            return "rom"
        return "en"

    @staticmethod
    def _new_state():
        return {
            ConsultationEngine._STATE_MARKER: True,
            "version": ConsultationEngine._STATE_VERSION,
            "domain_insights": {},
            "domain_memory": {},
            "active_domain": None,
            "last_question": {},
        }

    @staticmethod
    def _load_state(state_blob):
        if not state_blob:
            return ConsultationEngine._new_state()

        try:
            parsed = json.loads(str(state_blob))
        except Exception:
            return ConsultationEngine._new_state()

        if not isinstance(parsed, dict):
            return ConsultationEngine._new_state()

        if not parsed.get(ConsultationEngine._STATE_MARKER):
            return ConsultationEngine._new_state()

        parsed.setdefault("domain_insights", {})
        parsed.setdefault("domain_memory", {})
        parsed.setdefault("last_question", {})
        parsed.setdefault("active_domain", None)
        parsed.setdefault("version", ConsultationEngine._STATE_VERSION)
        return parsed

    @staticmethod
    def _dump_state(state):
        return json.dumps(state, ensure_ascii=False, separators=(",", ":"))

    @staticmethod
    def _ensure_domain_memory(state, domain):
        bucket = state["domain_memory"].get(domain)
        if not isinstance(bucket, dict):
            bucket = {}

        bucket.setdefault("answers", {})
        bucket.setdefault("pending_key", ConsultationEngine._DOMAIN_QUESTIONS[domain]["entry"]["key"])
        bucket.setdefault("last_user_input", "")
        state["domain_memory"][domain] = bucket
        return bucket

    @staticmethod
    def _limit_words(text, limit=None):
        max_words = limit or ConsultationEngine._MAX_RESPONSE_WORDS
        words = str(text or "").split()
        if len(words) <= max_words:
            return str(text or "").strip()
        return " ".join(words[:max_words]).strip()

    @staticmethod
    def _normalized(text):
        lowered = str(text or "").strip().lower()
        lowered = re.sub(r"\s+", " ", lowered)
        return lowered

    @staticmethod
    def _match_choice(text, choices):
        t = ConsultationEngine._normalized(text)
        if not t:
            return None

        number_map = {
            "1": 0,
            "2": 1,
            "3": 2,
            "one": 0,
            "two": 1,
            "three": 2,
        }

        if t in number_map and number_map[t] < len(choices):
            return choices[number_map[t]][0]

        if re.search(r"\b1\b", t) and len(choices) >= 1:
            return choices[0][0]
        if re.search(r"\b2\b", t) and len(choices) >= 2:
            return choices[1][0]
        if re.search(r"\b3\b", t) and len(choices) >= 3:
            return choices[2][0]

        for value, keywords in choices:
            for token in keywords:
                if token.lower() in t:
                    return value

        return None

    @staticmethod
    def _choice_label(domain, key, value):
        labels = ConsultationEngine._DOMAIN_VALUE_LABELS.get(domain, {}).get(key, {})
        return labels.get(value, str(value or "").strip())

    @staticmethod
    def _question_text(domain, question_type, language, script):
        q = ConsultationEngine._DOMAIN_QUESTIONS[domain][question_type]
        return q.get(ConsultationEngine._lang_key(language, script), q["en"])

    @staticmethod
    def _unknown_option_prompt(language, script):
        if ConsultationEngine._is_hi_dev(language, script):
            return "Mujhe precise reading ke liye aapka option clear chahiye."
        if ConsultationEngine._is_hi_rom(language, script):
            return "Mujhe precise reading ke liye aapka option clear chahiye."
        return "For a precise reading, I need that option clearly."

    @staticmethod
    def _strategy_question(language, script):
        if ConsultationEngine._is_hi_dev(language, script):
            return (
                "Aage aap kis style mein guidance chahte hain?\n"
                "1. Conservative\n"
                "2. Balanced\n"
                "3. Fast-track"
            )

        if ConsultationEngine._is_hi_rom(language, script):
            return (
                "Aage aap kis style mein guidance chahte hain?\n"
                "1. Conservative\n"
                "2. Balanced\n"
                "3. Fast-track"
            )

        return (
            "Which guidance style do you want next?\n"
            "1. Conservative\n"
            "2. Balanced\n"
            "3. Fast-track"
        )

    @staticmethod
    def _action_question(domain, language, script):
        if ConsultationEngine._is_hi_dev(language, script):
            return (
                f"{domain.title()} ke liye next step format choose karein:\n"
                "1. 30-day action plan\n"
                "2. 90-day strategy\n"
                "3. Timing checkpoints"
            )

        if ConsultationEngine._is_hi_rom(language, script):
            return (
                f"{domain.title()} ke liye next step format choose karein:\n"
                "1. 30-day action plan\n"
                "2. 90-day strategy\n"
                "3. Timing checkpoints"
            )

        return (
            f"For {domain}, choose the next-step format:\n"
            "1. 30-day action plan\n"
            "2. 90-day strategy\n"
            "3. Timing checkpoints"
        )

    @staticmethod
    def _parse_strategy_answer(text):
        choices = [
            ("conservative", ["conservative", "safe", "slow", "careful"]),
            ("balanced", ["balanced", "normal", "steady"]),
            ("fast", ["fast", "aggressive", "quick", "speed"]),
        ]
        return ConsultationEngine._match_choice(text, choices)

    @staticmethod
    def _parse_action_answer(text):
        choices = [
            ("30_day", ["30", "30-day", "monthly", "month"]),
            ("90_day", ["90", "90-day", "quarter", "quarterly"]),
            ("timing", ["timing", "checkpoint", "window"]),
        ]
        return ConsultationEngine._match_choice(text, choices)

    @staticmethod
    def _domain_momentum_line(domain, momentum, language, script):
        m = str(momentum or "Neutral").lower()

        if ConsultationEngine._is_hi_dev(language, script) or ConsultationEngine._is_hi_rom(language, script):
            if m == "positive":
                return f"{domain.title()} indicators supportive dikh rahe hain."
            if m == "challenging":
                return f"{domain.title()} indicators mein delay/pressure pattern dikh raha hai."
            return f"{domain.title()} indicators mixed but workable dikh rahe hain."

        if m == "positive":
            return f"{domain.title()} indicators look supportive right now."
        if m == "challenging":
            return f"{domain.title()} indicators show pressure and delay risk right now."
        return f"{domain.title()} indicators are mixed but workable right now."

    @staticmethod
    def _dasha_line(current_dasha, language, script):
        dasha = current_dasha or {}
        md = str(dasha.get("mahadasha") or "").strip()
        ad = str(dasha.get("antardasha") or "").strip()

        if not md and not ad:
            if ConsultationEngine._is_hi_dev(language, script) or ConsultationEngine._is_hi_rom(language, script):
                return "Dasha timing stable hai, isliye structured effort important rahega."
            return "Dasha timing is steady, so structured effort matters more than sudden moves."

        if md and ad:
            return f"Running dasha sequence {md}-{ad} is directly shaping this phase."

        return f"Running mahadasha {md} is influencing this phase."

    @staticmethod
    def _build_domain_insight(domain, domain_data, current_dasha, chart, language, script):
        signals = ConsultationEngine._DOMAIN_SIGNALS.get(domain, {})
        houses = signals.get("houses", "core domain houses")
        planets = signals.get("planets", "relevant planets")

        primary_driver = str(domain_data.get("primary_driver") or "").strip() or "Jupiter"
        risk_factor = str(domain_data.get("risk_factor") or "").strip() or "fluctuation"
        momentum = str(domain_data.get("momentum") or "Neutral")

        observation = ConsultationEngine._domain_momentum_line(domain, momentum, language, script)

        if ConsultationEngine._is_hi_dev(language, script) or ConsultationEngine._is_hi_rom(language, script):
            signal_line = (
                f"Main reading {houses} aur {planets} ke signal set se aa rahi hai, "
                f"jahan {primary_driver} driver role mein hai aur {risk_factor} caution area hai."
            )
        else:
            signal_line = (
                f"I am reading this through {houses} with {planets}, "
                f"where {primary_driver} is the lead driver and {risk_factor} is the caution zone."
            )

        timing_line = ConsultationEngine._dasha_line(current_dasha, language, script)
        timing_flag = signals.get("timing_flag")
        if timing_flag:
            flag_value = bool((chart or {}).get(timing_flag))
            if flag_value:
                timing_line = f"{timing_line} Current domain activation window is open."
            else:
                timing_line = f"{timing_line} Current domain activation window is not fully open yet."

        return {
            "observation": observation,
            "signal_line": signal_line,
            "timing_line": timing_line,
            "primary_driver": primary_driver,
            "risk_factor": risk_factor,
        }

    @staticmethod
    def _context_summary(domain, answers):
        labels = []
        for key, value in (answers or {}).items():
            if key.endswith("_raw"):
                continue
            if key in {"strategy_preference", "plan_preference"}:
                continue
            if not value:
                continue
            labels.append(ConsultationEngine._choice_label(domain, key, value))

        if not labels:
            return "context not yet complete"

        return "; ".join(labels)

    @staticmethod
    def _compose_domain_entry(domain, language, script):
        if ConsultationEngine._is_hi_dev(language, script) or ConsultationEngine._is_hi_rom(language, script):
            lead = f"{domain.title()} ke baare mein precise guidance dene se pehle ek diagnostic context lena zaroori hai."
        else:
            lead = f"Before I interpret {domain}, I need one diagnostic context point first."

        question = ConsultationEngine._question_text(domain, "entry", language, script)
        text = f"{lead}\n\n{question}"
        return ConsultationEngine._limit_words(text)

    @staticmethod
    def _compose_interpretation(domain, insight, context_summary, followup, language, script):
        if ConsultationEngine._is_hi_dev(language, script) or ConsultationEngine._is_hi_rom(language, script):
            lead = f"Aapne bataya: {context_summary}."
            body = (
                f"{insight['observation']} {insight['signal_line']} {insight['timing_line']} "
                "Isko aur precise karne ke liye ek aur point chahiye."
            )
        else:
            lead = f"You shared: {context_summary}."
            body = (
                f"{insight['observation']} {insight['signal_line']} {insight['timing_line']} "
                "To tighten interpretation accuracy, I need one more point."
            )

        text = f"{lead}\n\n{body}\n\n{followup}"
        return ConsultationEngine._limit_words(text)

    @staticmethod
    def _compose_guidance(domain, insight, context_summary, followup, language, script):
        if ConsultationEngine._is_hi_dev(language, script) or ConsultationEngine._is_hi_rom(language, script):
            text = (
                f"Same {domain} signal set ko use karte hue, aapka context ({context_summary}) "
                "batata hai ki immediate decision impulse se nahi, structured steps se lena better rahega. "
                f"{insight['primary_driver']} supportive tab hota hai jab execution disciplined ho, aur "
                f"{insight['risk_factor']} type moves avoid kiye jayein.\n\n"
                f"Agla step choose kariye:\n{followup}"
            )
        else:
            text = (
                f"Using the same {domain} signal set, your context ({context_summary}) suggests "
                "decisions should be structured, not rushed. "
                f"{insight['primary_driver']} supports progress when execution stays disciplined, while "
                f"{insight['risk_factor']}-style moves should be avoided.\n\n"
                f"Choose the next guidance style:\n{followup}"
            )

        return ConsultationEngine._limit_words(text)

    @staticmethod
    def _compose_practical_bridge(
        domain,
        insight,
        context_summary,
        strategy_pref,
        followup,
        language,
        script,
    ):
        if strategy_pref == "conservative":
            style_line = "risk low rakhkar steady progress mode mein chalna best rahega."
        elif strategy_pref == "fast":
            style_line = "fast-track mode possible hai, lekin guardrails strict rakhne honge."
        else:
            style_line = "balanced execution mode is domain ke liye strongest rahega."

        if ConsultationEngine._is_hi_dev(language, script) or ConsultationEngine._is_hi_rom(language, script):
            text = (
                f"Practical layer: aapke context ({context_summary}) ke liye {style_line} "
                "Is domain mein 3 clear rules rakhiye: "
                "(1) impulsive decisions avoid karein, "
                "(2) weekly measurable checkpoint rakhein, "
                f"(3) {insight['primary_driver']} supportive windows mein hi major step lein.\n\n"
                f"Ab execution format lock karte hain:\n{followup}"
            )
        else:
            text = (
                f"Practical layer: for your context ({context_summary}), {style_line} "
                "Keep three operating rules in this domain: "
                "(1) avoid impulsive decisions, "
                "(2) maintain one measurable weekly checkpoint, "
                f"(3) take major moves when {insight['primary_driver']} support is stronger.\n\n"
                f"Now lock the execution format:\n{followup}"
            )

        return ConsultationEngine._limit_words(text)

    @staticmethod
    def _compose_action(domain, insight, context_summary, plan_pref, followup, language, script):
        if plan_pref == "90_day":
            cadence = "90-day"
        elif plan_pref == "timing":
            cadence = "timing-checkpoint"
        else:
            cadence = "30-day"

        if ConsultationEngine._is_hi_dev(language, script) or ConsultationEngine._is_hi_rom(language, script):
            text = (
                f"Theek hai, is {domain} case mein {cadence} execution model rakhenge. "
                f"Aapke context ({context_summary}) aur same cached signal reading ke basis par: "
                "(1) clear measurable target set karein, "
                "(2) weekly review point fix karein, "
                "(3) emotional reaction ke bajaye pre-decided rule se action lein. "
                f"Yahi approach {insight['risk_factor']} risk ko control karti hai.\n\n"
                f"Agar chahein to next mein exact milestone format deta hoon. {followup}"
            )
        else:
            text = (
                f"Great, we will use a {cadence} execution model for this {domain} track. "
                f"From your context ({context_summary}) and the same cached signal reading: "
                "(1) set one measurable target, "
                "(2) lock a weekly review checkpoint, "
                "(3) take actions by rule, not emotion. "
                f"This is the safest way to reduce {insight['risk_factor']} risk.\n\n"
                f"If you want, I can map exact milestones next. {followup}"
            )

        return ConsultationEngine._limit_words(text)

    @staticmethod
    def next_stage(current_stage):
        if current_stage == ConsultationEngine.STATE_DOMAIN_ENTRY:
            return ConsultationEngine.STAGE_CHART_READING

        if current_stage == ConsultationEngine.STAGE_CHART_READING:
            return ConsultationEngine.STAGE_SITUATION_ANALYSIS

        if current_stage == ConsultationEngine.STAGE_SITUATION_ANALYSIS:
            return ConsultationEngine.STAGE_STRATEGY_GUIDANCE

        if current_stage == ConsultationEngine.STAGE_STRATEGY_GUIDANCE:
            return ConsultationEngine.STAGE_ACTION_PLAN

        return ConsultationEngine.STAGE_ACTION_PLAN

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
        del age, life_stage, user_goal, transits, persona_introduced, theme_shown

        if domain not in ConsultationEngine._DOMAIN_QUESTIONS:
            return {
                "text": "Please choose one domain: Career, Finance, Marriage, or Health.",
                "followup_question": "Which domain should we focus on?",
                "persona_added": False,
                "theme_used": False,
                "next_stage": ConsultationEngine.STATE_DOMAIN_ENTRY,
                "state_blob": session_state_blob,
            }

        state = ConsultationEngine._load_state(session_state_blob)
        state["active_domain"] = domain
        memory = ConsultationEngine._ensure_domain_memory(state, domain)
        answers = memory.get("answers", {})
        memory["last_user_input"] = str(user_text or "").strip()

        entry_cfg = ConsultationEngine._DOMAIN_QUESTIONS[domain]["entry"]
        secondary_cfg = ConsultationEngine._DOMAIN_QUESTIONS[domain]["secondary"]

        entry_key = entry_cfg["key"]
        secondary_key = secondary_cfg["key"]

        if domain_switched:
            memory["pending_key"] = entry_key

        response_text = ""
        followup_question = ""
        next_stage = ConsultationEngine.next_stage(stage)
        theme_used = False

        if stage == ConsultationEngine.STATE_DOMAIN_ENTRY:
            response_text = ConsultationEngine._compose_domain_entry(domain, language, script)
            followup_question = ConsultationEngine._question_text(domain, "entry", language, script)
            memory["pending_key"] = entry_key
            next_stage = ConsultationEngine.STAGE_CHART_READING

        elif stage == ConsultationEngine.STAGE_CHART_READING:
            if entry_key not in answers:
                parsed = ConsultationEngine._match_choice(user_text, entry_cfg["choices"])
                if not parsed:
                    response_text = (
                        f"{ConsultationEngine._unknown_option_prompt(language, script)}\n\n"
                        f"{ConsultationEngine._question_text(domain, 'entry', language, script)}"
                    )
                    followup_question = ConsultationEngine._question_text(domain, "entry", language, script)
                    memory["pending_key"] = entry_key
                    next_stage = ConsultationEngine.STAGE_CHART_READING
                else:
                    answers[entry_key] = parsed
                    answers[f"{entry_key}_raw"] = str(user_text or "").strip()

            if not response_text:
                insight_map = state.get("domain_insights", {})
                insight = insight_map.get(domain)
                if not isinstance(insight, dict):
                    insight = ConsultationEngine._build_domain_insight(
                        domain=domain,
                        domain_data=domain_data or {},
                        current_dasha=current_dasha,
                        chart=chart or {},
                        language=language,
                        script=script,
                    )
                    insight_map[domain] = insight
                    state["domain_insights"] = insight_map
                    theme_used = True

                followup_question = ConsultationEngine._question_text(domain, "secondary", language, script)
                response_text = ConsultationEngine._compose_interpretation(
                    domain=domain,
                    insight=insight,
                    context_summary=ConsultationEngine._context_summary(domain, answers),
                    followup=followup_question,
                    language=language,
                    script=script,
                )
                memory["pending_key"] = secondary_key
                next_stage = ConsultationEngine.STAGE_SITUATION_ANALYSIS

        elif stage == ConsultationEngine.STAGE_SITUATION_ANALYSIS:
            if secondary_key not in answers:
                parsed = ConsultationEngine._match_choice(user_text, secondary_cfg["choices"])
                if parsed:
                    answers[secondary_key] = parsed
                    answers[f"{secondary_key}_raw"] = str(user_text or "").strip()
                elif str(user_text or "").strip():
                    # Preserve free-form response if user does not use menu labels.
                    answers[secondary_key] = "freeform"
                    answers[f"{secondary_key}_raw"] = str(user_text or "").strip()

            insight = state.get("domain_insights", {}).get(domain)
            if not isinstance(insight, dict):
                insight = ConsultationEngine._build_domain_insight(
                    domain=domain,
                    domain_data=domain_data or {},
                    current_dasha=current_dasha,
                    chart=chart or {},
                    language=language,
                    script=script,
                )
                state["domain_insights"][domain] = insight
                theme_used = True

            followup_question = ConsultationEngine._strategy_question(language, script)
            response_text = ConsultationEngine._compose_guidance(
                domain=domain,
                insight=insight,
                context_summary=ConsultationEngine._context_summary(domain, answers),
                followup=followup_question,
                language=language,
                script=script,
            )
            memory["pending_key"] = "strategy_preference"
            next_stage = ConsultationEngine.STAGE_STRATEGY_GUIDANCE

        elif stage == ConsultationEngine.STAGE_STRATEGY_GUIDANCE:
            strategy_choice = ConsultationEngine._parse_strategy_answer(user_text)
            if strategy_choice:
                answers["strategy_preference"] = strategy_choice
                answers["strategy_preference_raw"] = str(user_text or "").strip()

            insight = state.get("domain_insights", {}).get(domain)
            if not isinstance(insight, dict):
                insight = ConsultationEngine._build_domain_insight(
                    domain=domain,
                    domain_data=domain_data or {},
                    current_dasha=current_dasha,
                    chart=chart or {},
                    language=language,
                    script=script,
                )
                state["domain_insights"][domain] = insight
                theme_used = True

            followup_question = ConsultationEngine._action_question(domain, language, script)
            response_text = ConsultationEngine._compose_practical_bridge(
                domain=domain,
                insight=insight,
                context_summary=ConsultationEngine._context_summary(domain, answers),
                strategy_pref=answers.get("strategy_preference", "balanced"),
                followup=followup_question,
                language=language,
                script=script,
            )
            memory["pending_key"] = "plan_preference"
            next_stage = ConsultationEngine.STAGE_ACTION_PLAN

        else:
            plan_choice = ConsultationEngine._parse_action_answer(user_text)
            if plan_choice:
                answers["plan_preference"] = plan_choice
                answers["plan_preference_raw"] = str(user_text or "").strip()

            insight = state.get("domain_insights", {}).get(domain)
            if not isinstance(insight, dict):
                insight = ConsultationEngine._build_domain_insight(
                    domain=domain,
                    domain_data=domain_data or {},
                    current_dasha=current_dasha,
                    chart=chart or {},
                    language=language,
                    script=script,
                )
                state["domain_insights"][domain] = insight
                theme_used = True

            followup_question = ConsultationEngine._action_question(domain, language, script)
            response_text = ConsultationEngine._compose_action(
                domain=domain,
                insight=insight,
                context_summary=ConsultationEngine._context_summary(domain, answers),
                plan_pref=answers.get("plan_preference", "30_day"),
                followup=followup_question,
                language=language,
                script=script,
            )
            memory["pending_key"] = "plan_preference"
            next_stage = ConsultationEngine.STAGE_ACTION_PLAN

        state["domain_memory"][domain] = memory
        state["last_question"][domain] = followup_question
        state_blob = ConsultationEngine._dump_state(state)

        return {
            "text": ConsultationEngine._limit_words(response_text),
            "followup_question": followup_question,
            "persona_added": False,
            "theme_used": theme_used,
            "next_stage": next_stage,
            "state_blob": state_blob,
        }
