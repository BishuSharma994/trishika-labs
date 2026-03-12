PLANET_BEHAVIOR_MAP = {
    "Moon": [
        "sleep rhythm",
        "emotional regulation",
        "hydration",
        "digestive rhythm",
    ],
    "Jupiter": [
        "daily routine",
        "learning habits",
        "morning structure",
        "mentor support",
    ],
    "Saturn": [
        "consistency",
        "long-term discipline",
        "physical endurance",
        "boundary setting",
    ],
    "Mars": [
        "exercise",
        "energy release",
        "anger management",
        "assertive communication",
    ],
    "Venus": [
        "relationship harmony",
        "financial balance",
        "self-care rhythm",
        "value-based decisions",
    ],
    "Mercury": [
        "communication hygiene",
        "planning",
        "decision journaling",
        "skill practice",
    ],
    "Sun": [
        "confidence",
        "leadership habits",
        "identity alignment",
        "goal clarity",
    ],
    "Rahu": [
        "impulse control",
        "digital boundaries",
        "risk filtering",
        "focus recovery",
    ],
    "Ketu": [
        "detachment balance",
        "reflection",
        "minimalism",
        "recovery time",
    ],
}

TOPIC_ROUTINE_MAP = {
    "career": "Start the day with a 15-minute task-priority plan before checking messages.",
    "finance": "Track all expenses once daily at a fixed evening time.",
    "marriage": "Schedule a daily 15-minute calm communication window.",
    "health": "Keep fixed sleep and wake times every day.",
}

SUBTOPIC_ROUTINE_MAP = {
    ("career", "job_switch"): "Do one skill-building block of 30 minutes daily and send one targeted application each weekday.",
    ("career", "promotion"): "Write three measurable wins at end of each workday and review them weekly.",
    ("career", "business_direction"): "Block 45 minutes daily for revenue-critical work before meetings.",
    ("finance", "savings"): "Auto-transfer a fixed savings amount on salary day and avoid same-day spending.",
    ("finance", "investment"): "Review allocation once per week; avoid ad-hoc buy/sell decisions during market spikes.",
    ("finance", "debt_management"): "Pay highest-interest debt first and freeze new discretionary borrowing for this cycle.",
    ("marriage", "single_path"): "Use a weekly relationship-intention checklist before starting new commitments.",
    ("marriage", "relationship_stability"): "Use a no-interruption 15-minute listening ritual daily.",
    ("marriage", "married_life"): "Set one weekly logistics-review conversation and one emotional check-in.",
    ("health", "stress"): "Practice 4-7-8 breathing twice daily and reduce stimulant intake after sunset.",
    ("health", "lifestyle_balance"): "Lock meal timing within a fixed two-hour band each day.",
    ("health", "specific_condition"): "Maintain symptom, sleep, and food journal with daily 3-line notes.",
}

SUBTOPIC_BEHAVIOR_MAP = {
    ("career", "job_switch"): "Avoid doom-scrolling job boards; use focused 2x20-minute search windows.",
    ("career", "promotion"): "Ask for one concrete feedback point weekly and execute it within 72 hours.",
    ("career", "business_direction"): "Say no to low-impact tasks that do not move revenue or delivery.",
    ("finance", "savings"): "Use a 24-hour pause before non-essential purchases.",
    ("finance", "investment"): "Follow a written investment rule; no decision without checklist confirmation.",
    ("finance", "debt_management"): "Use weekly debt tracker review; no emotional repayment changes.",
    ("marriage", "single_path"): "Prioritize value alignment over speed in relationship decisions.",
    ("marriage", "relationship_stability"): "Use calm tone reset before discussing sensitive topics.",
    ("marriage", "married_life"): "Separate problem-discussion from blame; focus on one issue at a time.",
    ("health", "stress"): "Do a 20-minute walk or light yoga daily for nervous-system release.",
    ("health", "lifestyle_balance"): "Stop heavy meals at least 2 hours before sleep.",
    ("health", "specific_condition"): "Escalate recurring symptoms early instead of delaying consultation.",
}

PLANET_REMEDY_MAP = {
    "Moon": "Maintain hydration discipline and avoid late-night meals for the full cycle.",
    "Jupiter": "Start mornings with learning, reflection, and one gratitude note.",
    "Saturn": "Follow strict time blocks and complete one pending task daily without fail.",
    "Mars": "Channel heat through exercise and avoid high-conflict conversations at peak stress.",
    "Venus": "Stabilize comfort-seeking impulses by planning spending and routines in advance.",
    "Mercury": "Write decisions before acting to reduce impulsive communication errors.",
    "Sun": "Start day with one confidence-building task and keep posture/energy intentional.",
    "Rahu": "Use digital boundaries and decision checklists to prevent reactive choices.",
    "Ketu": "Protect quiet reflection time and avoid abrupt withdrawal from responsibilities.",
}

STABILITY_BY_STRENGTH = {
    "strong": "stable",
    "moderate": "moderate",
    "weak": "sensitive",
}

TIMEFRAME_BY_STRENGTH = {
    "strong": "42 day consolidation cycle",
    "moderate": "28 day consistency cycle",
    "weak": "21 day stabilization cycle",
}


def _normalize_strength(strength, score):
    text = str(strength or "").strip().lower()
    if text in {"strong", "moderate", "weak"}:
        return text

    try:
        value = int(score)
    except Exception:
        value = 50

    if value >= 70:
        return "strong"
    if value >= 50:
        return "moderate"
    return "weak"


def _dedupe_keep_order(items):
    seen = set()
    ordered = []
    for item in items:
        token = str(item or "").strip().lower()
        if not token or token in seen:
            continue
        seen.add(token)
        ordered.append(str(item).strip())
    return ordered


def _level_from_depth(depth):
    try:
        value = int(depth)
    except Exception:
        value = 1
    if value <= 1:
        return 1
    if value == 2:
        return 2
    if value == 3:
        return 3
    return 4


def translate_to_life_guidance(analysis, topic, subtopic, depth=1):
    data = analysis or {}
    topic = str(topic or "general").strip().lower()
    subtopic = str(subtopic or "general").strip().lower()

    planet = str(data.get("planet") or "Moon").strip().title()
    house = data.get("house") or 0
    risk_planet = str(data.get("risk_planet") or data.get("risk_factor") or "Mars").strip().title()
    support_planet = str(data.get("supporting_planet") or planet).strip().title()
    score = data.get("score")
    strength = _normalize_strength(data.get("strength"), score)
    stability = STABILITY_BY_STRENGTH.get(strength, "moderate")
    timeframe = TIMEFRAME_BY_STRENGTH.get(strength, "28 day consistency cycle")
    level = _level_from_depth(depth)

    planet_focus = PLANET_BEHAVIOR_MAP.get(planet, PLANET_BEHAVIOR_MAP["Moon"])
    routine = SUBTOPIC_ROUTINE_MAP.get((topic, subtopic), TOPIC_ROUTINE_MAP.get(topic, "Keep one fixed routine block daily."))
    behavior = SUBTOPIC_BEHAVIOR_MAP.get((topic, subtopic), "Choose one behavior trigger and manage it with a written rule.")
    remedy = PLANET_REMEDY_MAP.get(planet, PLANET_REMEDY_MAP["Moon"])

    focus_areas = _dedupe_keep_order(
        [
            planet_focus[0] if len(planet_focus) > 0 else "",
            planet_focus[1] if len(planet_focus) > 1 else "",
            planet_focus[2] if len(planet_focus) > 2 else "",
            subtopic.replace("_", " "),
        ]
    )[:4]

    actions = [
        routine,
        behavior,
        f"Review progress every 7 days during the {timeframe}.",
    ]

    if level >= 3:
        actions.extend(
            [
                "Set a fixed daily check-in time and log completion in one line.",
                "When stress spikes, pause for 10 minutes before any major decision.",
            ]
        )

    if level >= 4:
        actions.append(remedy)

    return {
        "topic": topic,
        "subtopic": subtopic,
        "planet": planet,
        "house": house,
        "strength": strength,
        "stability": stability,
        "stress_source": f"{risk_planet} cycle",
        "supporting_influence": support_planet,
        "focus_areas": focus_areas,
        "actions": _dedupe_keep_order(actions),
        "routine": routine,
        "behavior": behavior,
        "timeframe": timeframe,
        "remedy": remedy,
        "level": level,
    }
