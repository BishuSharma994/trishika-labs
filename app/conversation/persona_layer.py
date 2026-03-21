import re


class PersonaLayer:

    ASTROLOGER_NAME = "Trishivara"   # ← Premium simple name (no bot vibe)
    BLOCKED_WORDS = ("momentum", "energy", "patterns", "alignment")
    PLANET_NAMES = ("sun", "moon", "mars", "mercury", "jupiter", "venus", "saturn", "rahu", "ketu")
    FINANCE_ALLOWED = ("savings", "spending", "income", "investment", "budget", "salary", "loan", "debt")
    FINANCE_REJECTED = ("relationship", "harmony", "self-care", "self care", "partner", "love")

    TOPIC_LABELS = {
        "career": {"en": "career", "hi": "career"},
        "finance": {"en": "finance", "hi": "finance"},
        "health": {"en": "health", "hi": "health"},
        "marriage": {"en": "marriage", "hi": "shaadi"},
    }

    GENDER_LABELS = {
        "male": {"en": "Male", "hi": "Male"},
        "female": {"en": "Female", "hi": "Female"},
        "other": {"en": "Other", "hi": "Other"},
    }

    @staticmethod
    def _language_key(language, script="latin"):
        mode = str(language or "").strip().lower()
        if mode == "hindi_roman" or str(script or "").strip().lower() == "roman":
            return "hi"
        return "en"

    @staticmethod
    def _text(language, script, english, roman_hindi):
        return roman_hindi if PersonaLayer._language_key(language, script) == "hi" else english

    @staticmethod
    def _topic_label(topic, language, script="latin"):
        key = PersonaLayer._language_key(language, script)
        labels = PersonaLayer.TOPIC_LABELS.get(str(topic or "").strip().lower(), PersonaLayer.TOPIC_LABELS["career"])
        return labels.get(key, labels["en"])

    @staticmethod
    def _gender_label(gender, language, script="latin"):
        key = PersonaLayer._language_key(language, script)
        labels = PersonaLayer.GENDER_LABELS.get(str(gender or "").strip().lower(), PersonaLayer.GENDER_LABELS["other"])
        return labels.get(key, labels["en"])

    @staticmethod
    def language_prompt():
        return "Choose your language."

    @staticmethod
    def topic_prompt(language, script="latin"):
        return PersonaLayer._text(
            language,
            script,
            "Choose a topic.",
            "Ek topic chuniye.",
        )

    @staticmethod
    def dob_prompt(language, script="latin"):
        return PersonaLayer._text(
            language,
            script,
            "Enter your date of birth (DD/MM/YYYY).",
            "Apni date of birth likhiye (DD/MM/YYYY).",
        )

    @staticmethod
    def time_prompt(language, script="latin"):
        return PersonaLayer._text(
            language,
            script,
            "Enter your birth time (HH:MM AM/PM).",
            "Apna birth time likhiye (HH:MM AM/PM).",
        )

    @staticmethod
    def place_prompt(language, script="latin"):
        return PersonaLayer._text(
            language,
            script,
            "Enter your birth place.",
            "Apna birth place likhiye.",
        )

    @staticmethod
    def gender_prompt(language, script="latin"):
        return PersonaLayer._text(
            language,
            script,
            "Select your gender.",
            "Apna gender chuniye.",
        )

    @staticmethod
    def name_prompt(language, script="latin"):
        return PersonaLayer._text(
            language,
            script,
            "Enter your name.",
            "Apna naam likhiye.",
        )

    @staticmethod
    def confirmation_prompt(topic, dob, birth_time, place, gender, name, language, script="latin"):
        topic_label = PersonaLayer._topic_label(topic, language, script).title()
        gender_label = PersonaLayer._gender_label(gender, language, script)
        summary = f"Confirm: {topic_label} | {dob} | {birth_time} | {place} | {gender_label} | {name}"
        question = PersonaLayer._text(
            language,
            script,
            "Is this correct?",
            "Kya yeh sahi hai?",
        )
        return f"{summary}\n{question}"

    @staticmethod
    def astrologer_intro(language, script="latin"):
        return PersonaLayer._text(
            language,
            script,
            "I am Trishivara, your Vedic astrologer.",
            "Main Trishivara hoon, aapka Vedic jyotishi.",
        )

    @staticmethod
    def consult_prompt(topic, language, script="latin"):
        topic_label = PersonaLayer._topic_label(topic, language, script)
        return PersonaLayer._text(
            language,
            script,
            f"What do you want to ask about {topic_label}?",
            f"Aap {topic_label} ke baare mein kya puchna chahte hain?",
        )

    @staticmethod
    def invalid_choice(language, script="latin"):
        return PersonaLayer._text(
            language,
            script,
            "Please use the available options.",
            "Kripya diye gaye options use kijiye.",
        )

    @staticmethod
    def devanagari_block(language, script="latin"):
        return PersonaLayer._text(
            language,
            script,
            "Please use English or Roman Hindi only.",
            "Sirf English ya Roman Hindi likhiye.",
        )

    @staticmethod
    def language_lock(language, script="latin"):
        return PersonaLayer._text(
            language,
            script,
            "Please continue in English.",
            "Roman Hindi mein likhiye.",
        )

    @staticmethod
    def restart_prompt(language, script="latin"):
        return PersonaLayer._text(
            language,
            script,
            "Let us restart from topic selection.",
            "Chaliye topic selection se phir shuru karte hain.",
        )

    @staticmethod
    def technical_issue(language, script="latin"):
        return PersonaLayer._text(
            language,
            script,
            "There is a temporary issue. Please ask again.",
            "Temporary issue hai. Kripya phir se puchhiye.",
        )

    @staticmethod
    def _clean_line(text):
        value = re.sub(r"\s+", " ", str(text or "").strip())
        return value.strip()

    @staticmethod
    def _action_line(actions):
        parts = []
        for index, action in enumerate(actions[:3], start=1):
            cleaned = PersonaLayer._clean_line(action)
            if cleaned:
                parts.append(f"{index}. {cleaned}")
        return " ".join(parts).strip()

    @staticmethod
    def format_guidance(guidance, language="english", script="latin", intent="general"):
        data = guidance or {}
        action_line = PersonaLayer._action_line(data.get("actions") or [])
        timeframe = PersonaLayer._clean_line(data.get("timeframe"))

        if intent == "instruction" or data.get("instruction_only"):
            lines = [
                f"Action: {action_line}",
                f"Timeframe: {timeframe}",
            ]
            return "\n".join(line for line in lines if line.strip())

        observation = PersonaLayer._clean_line(data.get("observation"))
        cause = PersonaLayer._clean_line(data.get("cause"))

        lines = [
            f"Observation: {observation}",
            f"Cause: {cause}",
            f"Action: {action_line}",
            f"Timeframe: {timeframe}",
        ]
        return "\n".join(line for line in lines if line.strip())

    @staticmethod
    def validate_response(text, topic=None, intent="general"):
        raw = str(text or "").strip()
        lowered = raw.lower()
        lines = [line.strip() for line in raw.splitlines() if line.strip()]

        if not raw:
            return False

        if any(word in lowered for word in PersonaLayer.BLOCKED_WORDS):
            return False

        if len(lines) > 6:
            return False

        if intent == "instruction":
            if len(lines) != 2:
                return False
            if not lines[0].startswith("Action:"):
                return False
            if not lines[1].startswith("Timeframe:"):
                return False
            return True

        # Default validation for normal replies
        return len(lines) >= 2 and "Observation:" in raw