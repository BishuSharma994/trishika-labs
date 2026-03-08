class ConsultationEngine:

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
    def _observation(domain, llm_observation, language, script):
        if ConsultationEngine._is_hi_dev(language, script):
            fallback = f"आपकी कुंडली में {domain} से जुड़े संकेत क्रमिक रूप से सक्रिय दिख रहे हैं।"
        elif ConsultationEngine._is_hi_rom(language, script):
            fallback = f"Aapki kundli mein {domain} se jude sanket dheere dheere active dikh rahe hain."
        else:
            fallback = f"Your chart shows active themes around {domain} developing gradually."

        return ConsultationEngine._clean(llm_observation, fallback)

    @staticmethod
    def _planetary_reasoning(primary_driver, llm_cause, language, script):
        driver = (primary_driver or "Unknown").strip() or "Unknown"

        if ConsultationEngine._is_hi_dev(language, script):
            fallback = f"{driver} का प्रभाव इस स्थिति की दिशा तय कर रहा है।"
        elif ConsultationEngine._is_hi_rom(language, script):
            fallback = f"{driver} ka prabhav is sthiti ki direction set kar raha hai."
        else:
            fallback = f"{driver} is the primary planetary influence shaping this situation."

        if llm_cause and llm_cause.strip():
            return f"{fallback} {llm_cause.strip()}"
        return fallback

    @staticmethod
    def _timing_interpretation(momentum, llm_timing, language, script):
        m = (momentum or "Neutral").strip()

        if ConsultationEngine._is_hi_dev(language, script):
            mapping = {
                "Positive": "समय सहयोगी है, इसलिए निरंतर प्रयास से बेहतर परिणाम मिलने की संभावना मजबूत है।",
                "Neutral": "समय स्थिर है, इसलिए धैर्य और नियमित प्रयास से सुधार दिखेगा।",
                "Challenging": "समय थोड़ा धीमा है, इसलिए संयम और सही कदमों से आगे बढ़ना बेहतर रहेगा।"
            }
        elif ConsultationEngine._is_hi_rom(language, script):
            mapping = {
                "Positive": "Samay supportive hai, isliye lagataar effort se better results milne ki sambhavna strong hai.",
                "Neutral": "Samay stable hai, isliye patience aur regular action se sudhar dikhne lagega.",
                "Challenging": "Samay thoda slow hai, isliye sambhal kar sahi steps lena behtar rahega."
            }
        else:
            mapping = {
                "Positive": "Momentum is supportive, so steady effort can open better outcomes soon.",
                "Neutral": "Momentum is stable, so consistent action and patience should improve results.",
                "Challenging": "Momentum is slower right now, so careful pacing and disciplined action are important."
            }

        fallback = mapping.get(m, mapping["Neutral"])

        if llm_timing and llm_timing.strip():
            return f"{fallback} {llm_timing.strip()}"
        return fallback

    @staticmethod
    def _practical_advice(risk_factor, llm_guidance, language, script):
        risk = (risk_factor or "Unknown").strip() or "Unknown"

        if ConsultationEngine._is_hi_dev(language, script):
            caution = f"सलाह: {risk} से जुड़े निर्णयों में जल्दबाज़ी से बचें और व्यावहारिक कदम चुनें।"
        elif ConsultationEngine._is_hi_rom(language, script):
            caution = f"Salah: {risk} se jude decisions mein jaldbaazi se bachein aur practical steps chunen."
        else:
            caution = f"Advice: avoid impulsive moves around {risk}-linked pressure and choose practical steps."

        if llm_guidance and llm_guidance.strip():
            return f"{caution} {llm_guidance.strip()}"
        return caution

    @staticmethod
    def _followup_question(followup_question, llm_followup, language, script):
        if followup_question and followup_question.strip():
            return followup_question.strip()

        if llm_followup and llm_followup.strip():
            return llm_followup.strip()

        if ConsultationEngine._is_hi_dev(language, script):
            return "क्या आप इस विषय को और गहराई से समझना चाहते हैं?"

        if ConsultationEngine._is_hi_rom(language, script):
            return "Kya aap is vishay ko aur gehraai se samajhna chahte hain?"

        return "Would you like to explore this area in more depth?"

    @staticmethod
    def build_consultation_payload(
        domain,
        domain_data,
        llm_fields,
        language,
        script,
        followup_question
    ):
        domain_data = domain_data or {}
        llm_fields = llm_fields or {}

        primary_driver = domain_data.get("primary_driver", "Unknown")
        risk_factor = domain_data.get("risk_factor", "Unknown")
        momentum = domain_data.get("momentum", "Neutral")

        return {
            "observation": ConsultationEngine._observation(
                domain=domain,
                llm_observation=llm_fields.get("observation", ""),
                language=language,
                script=script
            ),
            "planetary_reasoning": ConsultationEngine._planetary_reasoning(
                primary_driver=primary_driver,
                llm_cause=llm_fields.get("cause", ""),
                language=language,
                script=script
            ),
            "timing_interpretation": ConsultationEngine._timing_interpretation(
                momentum=momentum,
                llm_timing=llm_fields.get("timing", ""),
                language=language,
                script=script
            ),
            "practical_advice": ConsultationEngine._practical_advice(
                risk_factor=risk_factor,
                llm_guidance=llm_fields.get("guidance", ""),
                language=language,
                script=script
            ),
            "followup_question": ConsultationEngine._followup_question(
                followup_question=followup_question,
                llm_followup=llm_fields.get("followup", ""),
                language=language,
                script=script
            )
        }
