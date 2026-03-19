Single consolidated file. No splits. No missing sections. Use this as-is.

---

````markdown
# Codex Refactor Specification — Astro Telegram UX + Deterministic Human-like Responses

## Objective

Refactor the Telegram astrology bot to:

1. Enforce strict onboarding UX (HiAstro style)
2. Eliminate vague, repeated, and generic responses
3. Produce deterministic, human-like astrology outputs
4. Enforce state-driven conversation control
5. Support ONLY:
   - English
   - Roman Hindi

---

## PART 1 — UX FLOW (STRICT)

Sequence must NEVER change:

1. Language
2. Topic
3. Date of Birth
4. Birth Time
5. Birth Place
6. Gender
7. Name
8. Confirmation
9. Astrologer Introduction
10. Consultation

Rules:
- One question per step
- Wait for user input
- No skipping
- No repetition

---

## PART 2 — LANGUAGE RULES

Allowed:
- English
- Roman Hindi

Remove:
- Devanagari Hindi
- Mixed scripts

---

## PART 3 — ASTROLOGER PERSONA

Name: Arjun

English:
"I am Arjun, your AI astrologer."

Roman Hindi:
"Main Arjun hoon, aapka AI astrologer."

Rules:
- No mystical tone
- No filler phrases
- No exaggerated claims

---

## PART 4 — SESSION STRUCTURE

```python
session = {
    "step": str,
    "topic": str,
    "dob": str,
    "time": str,
    "place": str,
    "gender": str,
    "name": str,
    "consult_stage": int,
    "last_response": str
}
````

---

## PART 5 — STEP FLOW

```text
language → topic → dob → time → place → gender → name → confirm → consult
```

---

## PART 6 — INTENT NORMALIZATION

```python
INTENT_MAP = {
    "how": "instruction",
    "kaise": "instruction",
    "kaisey": "instruction",
    "what should i do": "instruction",
    "how long": "timing",
    "aur": "detail",
    "more": "detail"
}
```

---

## PART 7 — CONSULTATION ENGINE (DEPTH CONTROL)

```python
CONSULT_STAGES = {
    1: "observation",
    2: "explanation",
    3: "timing",
    4: "action",
    5: "remedy"
}

INTENT_STAGE_MAP = {
    "timing": 3,
    "instruction": 4,
    "remedy": 5,
    "detail": 2
}

if intent in INTENT_STAGE_MAP:
    stage = INTENT_STAGE_MAP[intent]
else:
    stage = session["consult_stage"]

session["consult_stage"] += 1
```

Rules:

* Never repeat same stage twice
* Always escalate depth

---

## PART 8 — ASTRO PIPELINE

```text
astro_engine
   ↓
astro_interpretation
   ↓
domain_translation
   ↓
persona_output
```

---

## PART 9 — PLANET MAP

```python
PLANET_MAP = {
    "Moon": {
        "meaning": "emotional patterns",
        "effects": ["stress", "sleep disruption"]
    },
    "Mars": {
        "meaning": "action",
        "effects": ["impulsive decisions"]
    },
    "Venus": {
        "meaning": "comfort",
        "effects": ["luxury spending"]
    },
    "Saturn": {
        "meaning": "discipline",
        "effects": ["slow progress"]
    },
    "Jupiter": {
        "meaning": "growth",
        "effects": ["opportunity"]
    }
}
```

---

## PART 10 — DOMAIN TRANSLATION

### Finance

```python
FINANCE_MAP = {
    "Mars": "impulsive spending",
    "Venus": "luxury expenses",
    "Saturn": "disciplined saving",
    "Jupiter": "income growth",
    "Moon": "emotional spending"
}
```

### Health

```python
HEALTH_MAP = {
    "Moon": "sleep and stress cycles",
    "Saturn": "chronic issues",
    "Mars": "energy imbalance",
    "Jupiter": "recovery strength"
}
```

Rules:

* Always map planet → domain effect
* No generic advice allowed

---

## PART 11 — RESPONSE TEMPLATE (MANDATORY)

```text
[Observation]

[Cause — planet based]

[Action — 2 to 3 steps]

[Timeframe]
```

---

## PART 12 — EXAMPLE OUTPUT (REFERENCE)

```
Mars is influencing your financial behavior.

This creates impulsive spending during quick decisions.

To control this:
1. Move savings immediately after salary
2. Delay purchases by 24 hours
3. Review expenses weekly

You will see stability in 3–4 weeks.
```

---

## PART 13 — INSTRUCTION HANDLING

If user says:

* kaise karu
* how do I do this

Then:

* return only steps
* no explanation
* no astrology jargon

---

## PART 14 — REPETITION GUARD

```python
if response == session["last_response"]:
    session["consult_stage"] += 1
```

---

## PART 15 — BLOCKED WORDS

Reject response if contains:

* momentum
* energy
* patterns
* alignment

---

## PART 16 — DOMAIN VALIDATION

If topic == finance:

Allowed:

* savings
* spending
* income
* investment
* budget

Reject:

* relationship
* harmony
* self-care

---

## PART 17 — OUTPUT VALIDATION

Response must:

* include at least 1 planet reference
* include 2–3 actionable steps
* include timeframe
* be under 6 lines
* contain no repetition

If any condition fails → regenerate

---

## PART 18 — FAILSAFE RULES

Before sending response:

```python
if response == session["last_response"]:
    regenerate_with_higher_stage()

if not contains_actions(response):
    regenerate()

if not contains_timeframe(response):
    regenerate()

if contains_blocked_words(response):
    regenerate()
```

---

## PART 19 — FILES TO MODIFY

Modify:

* app/conversation/dialog_engine.py
* app/conversation/consultation_engine.py
* app/conversation/intent_router.py
* app/conversation/persona_layer.py

Create:

* app/conversation/life_translation_engine.py

---

## PART 20 — ONBOARDING RULES

* One question per message
* Max 2 lines
* Use inline buttons wherever possible

---

## FINAL INSTRUCTION

Refactor the repository to enforce ALL rules above.

Do NOT redesign architecture.

Return:

1. Modified files
2. Full working code
3. No placeholders
4. No explanations

```
```
