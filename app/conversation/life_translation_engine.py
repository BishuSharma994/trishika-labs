PLANET_MAP = {
    "Moon": {
        "meaning": "emotional reactions",
        "effects": ["stress", "sleep disruption"],
    },
    "Mars": {
        "meaning": "action",
        "effects": ["impulsive decisions"],
    },
    "Venus": {
        "meaning": "comfort",
        "effects": ["luxury spending"],
    },
    "Saturn": {
        "meaning": "discipline",
        "effects": ["slow progress"],
    },
    "Jupiter": {
        "meaning": "growth",
        "effects": ["opportunity"],
    },
    "Mercury": {
        "meaning": "planning",
        "effects": ["mixed decisions"],
    },
    "Sun": {
        "meaning": "authority",
        "effects": ["pressure"],
    },
}

FINANCE_MAP = {
    "Mars": {
        "en": "impulsive spending during quick decisions",
        "hi": "jaldi decisions mein impulsive spending",
    },
    "Venus": {
        "en": "luxury spending stretching your budget",
        "hi": "luxury spending aapka budget stretch kar rahi hai",
    },
    "Saturn": {
        "en": "slow but disciplined saving",
        "hi": "slow lekin disciplined saving",
    },
    "Jupiter": {
        "en": "income growth with better budgeting",
        "hi": "better budgeting ke saath income growth",
    },
    "Moon": {
        "en": "emotional spending affecting savings",
        "hi": "emotional spending savings ko affect kar rahi hai",
    },
    "Mercury": {
        "en": "budget changes caused by mixed planning",
        "hi": "mixed planning ki wajah se budget changes",
    },
    "Sun": {
        "en": "income pressure from status-driven spending",
        "hi": "status-driven spending se income pressure",
    },
}

HEALTH_MAP = {
    "Moon": {
        "en": "sleep and stress strain",
        "hi": "sleep aur stress strain",
    },
    "Saturn": {
        "en": "slow recovery and chronic strain",
        "hi": "slow recovery aur chronic strain",
    },
    "Mars": {
        "en": "overexertion and fast reactions in the body",
        "hi": "body mein overexertion aur fast reactions",
    },
    "Jupiter": {
        "en": "steady recovery when routine stays consistent",
        "hi": "routine consistent rahe to steady recovery",
    },
    "Venus": {
        "en": "comfort habits disrupting discipline",
        "hi": "comfort habits discipline ko tod rahi hain",
    },
    "Mercury": {
        "en": "routine changes affecting recovery",
        "hi": "routine changes recovery ko affect kar rahe hain",
    },
    "Sun": {
        "en": "pressure reducing physical balance",
        "hi": "pressure physical balance ko kam kar raha hai",
    },
}

CAREER_MAP = {
    "Saturn": {
        "en": "slow progress that improves with discipline",
        "hi": "slow progress jo discipline se improve hoti hai",
    },
    "Mars": {
        "en": "rushed work decisions creating mistakes",
        "hi": "rushed work decisions se mistakes",
    },
    "Jupiter": {
        "en": "growth opportunities that need steady follow-through",
        "hi": "growth opportunities jinhe steady follow-through chahiye",
    },
    "Moon": {
        "en": "stress affecting work decisions",
        "hi": "stress work decisions ko affect kar raha hai",
    },
    "Mercury": {
        "en": "communication gaps slowing progress",
        "hi": "communication gaps progress ko slow kar rahe hain",
    },
    "Sun": {
        "en": "authority pressure changing work direction",
        "hi": "authority pressure work direction ko badal raha hai",
    },
    "Venus": {
        "en": "comfort delaying skill growth",
        "hi": "comfort skill growth ko delay kar raha hai",
    },
}

MARRIAGE_MAP = {
    "Venus": {
        "en": "expectations around comfort and attention",
        "hi": "comfort aur attention ko lekar expectations",
    },
    "Mars": {
        "en": "quick reactions causing conflict",
        "hi": "quick reactions se conflict",
    },
    "Moon": {
        "en": "mood-driven relationship decisions",
        "hi": "mood-driven relationship decisions",
    },
    "Saturn": {
        "en": "slow commitment and serious pressure",
        "hi": "slow commitment aur serious pressure",
    },
    "Jupiter": {
        "en": "support for steady commitment",
        "hi": "steady commitment ke liye support",
    },
    "Mercury": {
        "en": "mixed communication creating doubt",
        "hi": "mixed communication se doubt",
    },
    "Sun": {
        "en": "ego pressure affecting decisions",
        "hi": "ego pressure decisions ko affect kar raha hai",
    },
}

DOMAIN_EFFECT_MAP = {
    "finance": FINANCE_MAP,
    "health": HEALTH_MAP,
    "career": CAREER_MAP,
    "marriage": MARRIAGE_MAP,
}

TOPIC_FOCUS = {
    "career": {"en": "work progress", "hi": "work progress"},
    "finance": {"en": "spending and budget", "hi": "spending aur budget"},
    "health": {"en": "health routine", "hi": "health routine"},
    "marriage": {"en": "relationship decisions", "hi": "shaadi decisions"},
}

ACTION_LIBRARY = {
    "finance": {
        "default": {
            "en": [
                "Move savings on salary day",
                "Delay non-essential spending by 24 hours",
                "Review your budget every Sunday",
                "Keep one fixed investment rule",
            ],
            "hi": [
                "Salary day par savings alag rakhiye",
                "Non-essential spending 24 ghante delay kijiye",
                "Budget Sunday ko review kijiye",
                "Ek fixed investment rule rakhiye",
            ],
        },
        "Mars": {
            "en": [
                "Move savings on salary day",
                "Delay non-essential spending by 24 hours",
                "Review your budget every Sunday",
                "Cut impulse spending above your limit",
            ],
            "hi": [
                "Salary day par savings alag rakhiye",
                "Non-essential spending 24 ghante delay kijiye",
                "Budget Sunday ko review kijiye",
                "Limit se upar impulse spending rok dijiye",
            ],
        },
        "Venus": {
            "en": [
                "Set one budget for comfort spending",
                "Check savings before any large purchase",
                "Review spending every Sunday",
                "Cap non-essential spending for the month",
            ],
            "hi": [
                "Comfort spending ke liye ek budget set kijiye",
                "Large purchase se pehle savings check kijiye",
                "Spending Sunday ko review kijiye",
                "Pura mahina non-essential spending cap rakhiye",
            ],
        },
        "Saturn": {
            "en": [
                "Increase savings on one fixed date",
                "Track spending in one budget list",
                "Review investment every week",
                "Keep the same monthly budget limit",
            ],
            "hi": [
                "Ek fixed date par savings badhaiye",
                "Spending ko ek budget list mein track kijiye",
                "Investment har week review kijiye",
                "Same monthly budget limit rakhiye",
            ],
        },
        "Jupiter": {
            "en": [
                "Move extra income into savings first",
                "Add one fixed investment amount monthly",
                "Review your budget every week",
                "Protect income from non-essential spending",
            ],
            "hi": [
                "Extra income ko pehle savings mein daliyega",
                "Har mahine ek fixed investment amount daliyega",
                "Budget har week review kijiye",
                "Income ko non-essential spending se bachaiye",
            ],
        },
        "Moon": {
            "en": [
                "Do not spend when you feel upset",
                "Move savings before daily spending starts",
                "Review your budget each evening",
                "Limit emotional spending to one budget line",
            ],
            "hi": [
                "Upset hone par spending mat kijiye",
                "Daily spending se pehle savings alag rakhiye",
                "Budget har shaam review kijiye",
                "Emotional spending ko ek budget line tak rakhiye",
            ],
        },
    },
    "health": {
        "default": {
            "en": [
                "Keep one fixed sleep time",
                "Reduce screen use before sleep",
                "Track stress and sleep daily",
                "Review your routine weekly",
            ],
            "hi": [
                "Ek fixed sleep time rakhiye",
                "Sleep se pehle screen use kam kijiye",
                "Stress aur sleep daily track kijiye",
                "Routine weekly review kijiye",
            ],
        },
        "Moon": {
            "en": [
                "Keep one fixed sleep time",
                "Reduce screen use before sleep",
                "Track stress and sleep daily",
                "Stop late-night work for now",
            ],
            "hi": [
                "Ek fixed sleep time rakhiye",
                "Sleep se pehle screen use kam kijiye",
                "Stress aur sleep daily track kijiye",
                "Abhi late-night work band kijiye",
            ],
        },
        "Saturn": {
            "en": [
                "Keep medical review dates on time",
                "Stay on one fixed sleep schedule",
                "Track symptoms weekly",
                "Follow one strict recovery routine",
            ],
            "hi": [
                "Medical review dates time par rakhiye",
                "Ek fixed sleep schedule follow kijiye",
                "Symptoms weekly track kijiye",
                "Ek strict recovery routine follow kijiye",
            ],
        },
        "Mars": {
            "en": [
                "Avoid overtraining for now",
                "Keep water intake steady",
                "Pause before intense activity when tired",
                "Reduce fast physical strain",
            ],
            "hi": [
                "Abhi overtraining avoid kijiye",
                "Water intake steady rakhiye",
                "Tired hone par intense activity se pehle rukiye",
                "Fast physical strain kam kijiye",
            ],
        },
    },
    "career": {
        "default": {
            "en": [
                "Write your top work priority daily",
                "Finish one important task before meetings",
                "Review progress every Friday",
                "Track one measurable work result",
            ],
            "hi": [
                "Daily top work priority likhiye",
                "Meetings se pehle ek important task khatam kijiye",
                "Progress Friday ko review kijiye",
                "Ek measurable work result track kijiye",
            ],
        },
        "Saturn": {
            "en": [
                "Use fixed work blocks every day",
                "Track one measurable work goal daily",
                "Review progress every Friday",
                "Finish pending work before taking more",
            ],
            "hi": [
                "Daily fixed work blocks use kijiye",
                "Ek measurable work goal daily track kijiye",
                "Progress Friday ko review kijiye",
                "Zyada lene se pehle pending work khatam kijiye",
            ],
        },
        "Mars": {
            "en": [
                "Delay big job decisions by 24 hours",
                "Finish high-priority work first",
                "Review work output every Friday",
                "Avoid rushed replies at work",
            ],
            "hi": [
                "Bade job decisions 24 ghante delay kijiye",
                "High-priority work pehle khatam kijiye",
                "Work output Friday ko review kijiye",
                "Work par rushed replies avoid kijiye",
            ],
        },
        "Jupiter": {
            "en": [
                "Apply for one growth role weekly",
                "Ask for work expansion with results",
                "Review role progress monthly",
                "Protect time for skill growth",
            ],
            "hi": [
                "Har week ek growth role ke liye apply kijiye",
                "Results ke saath work expansion maangiye",
                "Role progress monthly review kijiye",
                "Skill growth ke liye time bachaiye",
            ],
        },
    },
    "marriage": {
        "default": {
            "en": [
                "Keep one calm weekly check-in",
                "Discuss one issue at a time",
                "Review progress together every week",
                "Set one clear expectation early",
            ],
            "hi": [
                "Ek calm weekly check-in rakhiye",
                "Ek time par ek issue discuss kijiye",
                "Progress har week saath review kijiye",
                "Ek clear expectation pehle set kijiye",
            ],
        },
        "Mars": {
            "en": [
                "Pause before difficult talks",
                "Discuss one issue at a time",
                "Review conflict triggers weekly",
                "Avoid fast reactions in arguments",
            ],
            "hi": [
                "Difficult talks se pehle rukiye",
                "Ek time par ek issue discuss kijiye",
                "Conflict triggers weekly review kijiye",
                "Arguments mein fast reactions avoid kijiye",
            ],
        },
        "Venus": {
            "en": [
                "Set one clear expectation early",
                "Keep one weekly check-in",
                "Review shared decisions every week",
                "Talk about time and money directly",
            ],
            "hi": [
                "Ek clear expectation pehle set kijiye",
                "Ek weekly check-in rakhiye",
                "Shared decisions har week review kijiye",
                "Time aur money par seedha baat kijiye",
            ],
        },
        "Saturn": {
            "en": [
                "Keep commitments on the promised day",
                "Use one fixed discussion time weekly",
                "Review trust issues calmly",
                "Do not delay serious decisions",
            ],
            "hi": [
                "Promised day par commitments nibhaiye",
                "Weekly ek fixed discussion time rakhiye",
                "Trust issues ko calmly review kijiye",
                "Serious decisions delay mat kijiye",
            ],
        },
    },
}

REMEDY_LIBRARY = {
    "career": {
        "en": "Keep this work routine without breaks",
        "hi": "Is work routine ko bina break ke rakhiye",
    },
    "finance": {
        "en": "Keep the same budget limit for the full period",
        "hi": "Puri period ke liye same budget limit rakhiye",
    },
    "health": {
        "en": "Keep the same health routine every day",
        "hi": "Daily same health routine rakhiye",
    },
    "marriage": {
        "en": "Keep one fixed relationship check-in every week",
        "hi": "Har week ek fixed relationship check-in rakhiye",
    },
}

TOPIC_DEFAULT_PLANET = {
    "career": "Saturn",
    "finance": "Jupiter",
    "health": "Moon",
    "marriage": "Venus",
}


def _language_key(language):
    return "hi" if str(language or "").strip().lower() == "hindi_roman" else "en"


def _localized(payload, language):
    key = _language_key(language)
    return str(payload.get(key) or payload.get("en") or "").strip()


def _normalize_topic(topic):
    value = str(topic or "").strip().lower()
    if value in {"career", "finance", "health", "marriage"}:
        return value
    return "career"


def _normalize_planet(planet, topic):
    value = str(planet or "").strip().title()
    if value in PLANET_MAP:
        return value
    return TOPIC_DEFAULT_PLANET.get(topic, "Moon")


def _normalize_stage(stage):
    try:
        value = int(stage)
    except Exception:
        value = 1
    if value < 1:
        return 1
    if value > 5:
        return 5
    return value


def _domain_effect(topic, planet, language):
    mapping = DOMAIN_EFFECT_MAP.get(topic, {})
    payload = mapping.get(planet) or mapping.get("Moon") or {
        "en": "a direct issue in this area",
        "hi": "is area mein ek seedha issue",
    }
    return _localized(payload, language)


def _topic_focus(topic, language):
    return _localized(TOPIC_FOCUS.get(topic, TOPIC_FOCUS["career"]), language)


def _dasha_values(current_dasha):
    values = set()
    if isinstance(current_dasha, dict):
        for value in current_dasha.values():
            text = str(value or "").strip().title()
            if text:
                values.add(text)
    return values


def _time_window(score, projection, current_dasha, planet, risk_planet):
    try:
        base_score = int(score)
    except Exception:
        base_score = 55

    try:
        projected_score = int(projection)
    except Exception:
        projected_score = base_score

    pace = base_score + max(-6, min(6, projected_score - base_score))

    dasha_values = _dasha_values(current_dasha)
    if planet in dasha_values:
        pace += 5
    if risk_planet in dasha_values:
        pace -= 5

    if pace >= 72:
        return {
            "en": "2-3 weeks",
            "hi": "2-3 hafte",
        }
    if pace >= 60:
        return {
            "en": "3-4 weeks",
            "hi": "3-4 hafte",
        }
    if pace >= 48:
        return {
            "en": "4-6 weeks",
            "hi": "4-6 hafte",
        }
    return {
        "en": "6-8 weeks",
        "hi": "6-8 hafte",
    }


def _build_observation(topic, planet, stage, language):
    focus = _topic_focus(topic, language)
    stage = _normalize_stage(stage)

    if _language_key(language) == "hi":
        if stage == 1:
            return f"{planet} abhi aapke {focus} ko impact kar raha hai."
        if stage == 2:
            return f"{planet} aapke {focus} ki root problem dikha raha hai."
        if stage == 3:
            return f"{planet} abhi aapke {focus} ka timing control kar raha hai."
        if stage == 4:
            return f"{planet} dikhata hai ki {focus} mein ab direct action zaroori hai."
        return f"{planet} dikhata hai ki {focus} ke liye ab strict remedy plan chahiye."

    if stage == 1:
        return f"{planet} is influencing your {focus} right now."
    if stage == 2:
        return f"{planet} is showing the root issue in your {focus}."
    if stage == 3:
        return f"{planet} is controlling the current timing for your {focus}."
    if stage == 4:
        return f"{planet} is making direct action important in your {focus}."
    return f"{planet} is showing that a strict remedy plan is needed for your {focus}."


def _build_cause(topic, planet, risk_planet, stage, language):
    effect = _domain_effect(topic, planet, language)
    stage = _normalize_stage(stage)

    if _language_key(language) == "hi":
        if stage == 1:
            return f"{planet} se {effect}."
        if stage == 2:
            return f"{planet} se {effect}, aur {risk_planet} results ko slow kar sakta hai."
        if stage == 3:
            return f"{planet} se {effect}, aur {risk_planet} fast results ko delay kar raha hai."
        if stage == 4:
            return f"{planet} se {effect}, isliye wait karne se zyada action kaam karega."
        return f"{planet} se {effect}, isliye fixed routine ab best remedy hai."

    if stage == 1:
        return f"{planet} creates {effect}."
    if stage == 2:
        return f"{planet} creates {effect}, and {risk_planet} can slow results."
    if stage == 3:
        return f"{planet} creates {effect}, and {risk_planet} is delaying faster results."
    if stage == 4:
        return f"{planet} creates {effect}, so action works better than waiting."
    return f"{planet} creates {effect}, so a fixed routine is the best remedy now."


def _base_actions(topic, planet, language):
    topic_actions = ACTION_LIBRARY.get(topic, ACTION_LIBRARY["career"])
    payload = topic_actions.get(planet) or topic_actions.get("default")
    return list(payload.get(_language_key(language), payload.get("en", [])))


def _select_actions(topic, planet, stage, language, variant=0):
    stage = _normalize_stage(stage)
    actions = _base_actions(topic, planet, language)
    if not actions:
        return []

    count = 2 if stage == 1 else 3
    start = 1 if variant and len(actions) > count else 0
    selected = actions[start : start + count]

    if len(selected) < count:
        selected = actions[:count]

    if stage == 5 and selected:
        selected[-1] = _localized(REMEDY_LIBRARY.get(topic, REMEDY_LIBRARY["career"]), language)

    return selected[:3]


def _build_timeframe(stage, score, projection, current_dasha, planet, risk_planet, language):
    stage = _normalize_stage(stage)
    window = _localized(
        _time_window(score, projection, current_dasha, planet, risk_planet),
        language,
    )

    if _language_key(language) == "hi":
        if stage == 1:
            return f"{window} mein sudhar dikhna shuru hoga."
        if stage == 2:
            return f"{window} mein baat aur clear hogi."
        if stage == 3:
            return f"Strong result {window} mein dikh sakta hai."
        if stage == 4:
            return f"In steps ko {window} tak follow kijiye."
        return f"Is remedy ko {window} tak rakhiye."

    if stage == 1:
        return f"Improvement should start in {window}."
    if stage == 2:
        return f"This should become clearer in {window}."
    if stage == 3:
        return f"The stronger opening should show in {window}."
    if stage == 4:
        return f"Follow these steps for {window}."
    return f"Keep this remedy for {window}."


def translate_to_life_guidance(
    analysis,
    topic,
    consult_stage=1,
    language="english",
    intent="general",
    variant=0,
):
    data = analysis or {}
    topic = _normalize_topic(topic)
    stage = _normalize_stage(consult_stage)

    planet = _normalize_planet(data.get("planet"), topic)
    risk_planet = _normalize_planet(data.get("risk_planet"), topic)
    score = data.get("score", 55)
    projection = data.get("projection", score)
    current_dasha = data.get("current_dasha") or {}

    actions = _select_actions(
        topic=topic,
        planet=planet,
        stage=stage,
        language=language,
        variant=variant,
    )

    return {
        "topic": topic,
        "planet": planet,
        "observation": _build_observation(topic, planet, stage, language),
        "cause": _build_cause(topic, planet, risk_planet, stage, language),
        "actions": actions,
        "timeframe": _build_timeframe(
            stage=stage,
            score=score,
            projection=projection,
            current_dasha=current_dasha,
            planet=planet,
            risk_planet=risk_planet,
            language=language,
        ),
        "instruction_only": intent == "instruction",
    }
