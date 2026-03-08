class AstrologyResponseTemplate:

    MOMENTUM_LINES_EN = {
        "Positive": "Momentum is currently supportive, so near-term progress is realistic with disciplined effort.",
        "Neutral": "Momentum is steady, so outcomes should improve gradually through consistent actions.",
        "Challenging": "Momentum is slower right now, so cautious pacing and patience are important."
    }

    MOMENTUM_LINES_DEV = {
        "Positive": "अभी गति सहयोगी है, इसलिए अनुशासित प्रयास से निकट भविष्य में प्रगति संभव है।",
        "Neutral": "अभी गति स्थिर है, इसलिए निरंतर प्रयास से परिणाम धीरे-धीरे बेहतर होंगे।",
        "Challenging": "अभी गति धीमी है, इसलिए धैर्य और सावधानी के साथ आगे बढ़ना बेहतर रहेगा।"
    }

    MOMENTUM_LINES_ROM = {
        "Positive": "Abhi momentum supportive hai, isliye disciplined effort se near-term progress mumkin hai.",
        "Neutral": "Abhi momentum steady hai, isliye lagataar action se results dheere-dheere better honge.",
        "Challenging": "Abhi momentum slow hai, isliye patience aur caution ke saath aage badhna better rahega."
    }

    @staticmethod
    def _is_hi_dev(language, script):
        return language == "hi" and script == "devanagari"

    @staticmethod
    def _is_hi_rom(language, script):
        return language == "hi" and script == "roman"

    @staticmethod
    def _clean(text, fallback):
        value = (text or "").strip()
        return value if value else fallback

    @staticmethod
    def _merge(primary, secondary):
        first = (primary or "").strip()
        second = (secondary or "").strip()

        if first and second:
            return f"{first} {second}"
        if first:
            return first
        return second

    @staticmethod
    def _deterministic_observation(domain, score, language, script):
        if AstrologyResponseTemplate._is_hi_dev(language, script):
            return f"{domain} क्षेत्र का संकेतक स्कोर अभी {score}/100 दिख रहा है।"

        if AstrologyResponseTemplate._is_hi_rom(language, script):
            return f"{domain} shetra ka sanketik score abhi {score}/100 dikh raha hai."

        return f"The {domain} signal score is {score}/100 in this chart snapshot."

    @staticmethod
    def _deterministic_cause(primary_driver, language, script):
        driver = (primary_driver or "Unknown").strip() or "Unknown"

        if AstrologyResponseTemplate._is_hi_dev(language, script):
            return f"इस विषय में मुख्य ग्रह-कारक {driver} है।"

        if AstrologyResponseTemplate._is_hi_rom(language, script):
            return f"Is vishay mein primary grah-driver {driver} hai."

        return f"The primary planetary driver here is {driver}."

    @staticmethod
    def _deterministic_timing(momentum, language, script):
        if AstrologyResponseTemplate._is_hi_dev(language, script):
            return AstrologyResponseTemplate.MOMENTUM_LINES_DEV.get(
                momentum,
                AstrologyResponseTemplate.MOMENTUM_LINES_DEV["Neutral"]
            )

        if AstrologyResponseTemplate._is_hi_rom(language, script):
            return AstrologyResponseTemplate.MOMENTUM_LINES_ROM.get(
                momentum,
                AstrologyResponseTemplate.MOMENTUM_LINES_ROM["Neutral"]
            )

        return AstrologyResponseTemplate.MOMENTUM_LINES_EN.get(
            momentum,
            AstrologyResponseTemplate.MOMENTUM_LINES_EN["Neutral"]
        )

    @staticmethod
    def _deterministic_caution(risk_factor, language, script):
        risk = (risk_factor or "Unknown").strip() or "Unknown"

        if AstrologyResponseTemplate._is_hi_dev(language, script):
            return f"सावधानी: {risk} से जुड़ी स्थितियों में जल्दबाज़ी से बचें।"

        if AstrologyResponseTemplate._is_hi_rom(language, script):
            return f"Savdhani: {risk} se judi situations mein jaldbaazi se bachein."

        return f"Caution: avoid impulsive decisions around {risk}-linked pressure."

    @staticmethod
    def build_response(
        domain,
        domain_data,
        llm_fields,
        language,
        script,
        followup_question=None
    ):
        domain_data = domain_data or {}
        llm_fields = llm_fields or {}

        score = domain_data.get("score", 50)
        primary_driver = domain_data.get("primary_driver", "Unknown")
        risk_factor = domain_data.get("risk_factor", "Unknown")
        momentum = domain_data.get("momentum", "Neutral")

        llm_observation = llm_fields.get("observation", "")
        llm_cause = llm_fields.get("cause", "")
        llm_timing = llm_fields.get("timing", "")
        llm_guidance = llm_fields.get("guidance", "")
        llm_followup = llm_fields.get("followup", "")

        observation = AstrologyResponseTemplate._clean(
            AstrologyResponseTemplate._merge(
                AstrologyResponseTemplate._deterministic_observation(domain, score, language, script),
                llm_observation
            ),
            AstrologyResponseTemplate._deterministic_observation(domain, score, language, script)
        )

        cause = AstrologyResponseTemplate._clean(
            AstrologyResponseTemplate._merge(
                AstrologyResponseTemplate._deterministic_cause(primary_driver, language, script),
                llm_cause
            ),
            AstrologyResponseTemplate._deterministic_cause(primary_driver, language, script)
        )

        timing = AstrologyResponseTemplate._clean(
            AstrologyResponseTemplate._merge(
                AstrologyResponseTemplate._deterministic_timing(momentum, language, script),
                llm_timing
            ),
            AstrologyResponseTemplate._deterministic_timing(momentum, language, script)
        )

        guidance = AstrologyResponseTemplate._clean(
            AstrologyResponseTemplate._merge(
                AstrologyResponseTemplate._deterministic_caution(risk_factor, language, script),
                llm_guidance
            ),
            AstrologyResponseTemplate._deterministic_caution(risk_factor, language, script)
        )

        followup = AstrologyResponseTemplate._clean(
            followup_question or llm_followup,
            (
                "क्या आप इस विषय को और विस्तार से समझना चाहेंगे?"
                if AstrologyResponseTemplate._is_hi_dev(language, script)
                else (
                    "Kya aap is vishay ko aur detail mein samajhna chahenge?"
                    if AstrologyResponseTemplate._is_hi_rom(language, script)
                    else "Would you like to explore this area in more detail?"
                )
            )
        )

        return (
            f"Observation:\n{observation}\n\n"
            f"Planetary Cause:\n{cause}\n\n"
            f"Timing Insight:\n{timing}\n\n"
            f"Guidance:\n{guidance}\n\n"
            f"Follow-up Question:\n{followup}"
        )
