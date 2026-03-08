from app.conversation.followup_router import FollowupRouter


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
    def _observation(domain, llm_observation, language, script, stage):
        if ConsultationEngine._is_hi_dev(language, script):
            stage_fallbacks = {
                FollowupRouter.STAGE_CHART_READING: f"आपकी कुंडली देखने पर {domain} के संकेत स्पष्ट रूप से सक्रिय दिख रहे हैं।",
                FollowupRouter.STAGE_SITUATION_ANALYSIS: f"आपकी वर्तमान स्थिति के संदर्भ में {domain} का प्रभाव अधिक प्रत्यक्ष दिखाई दे रहा है।",
                FollowupRouter.STAGE_STRATEGY_GUIDANCE: f"अब आपके लिए {domain} में रणनीतिक कदम लेना सबसे अधिक उपयोगी रहेगा।",
                FollowupRouter.STAGE_ACTION_PLAN: f"अब समय है कि {domain} के लिए स्पष्ट और व्यावहारिक कदम तय किए जाएँ।"
            }
        elif ConsultationEngine._is_hi_rom(language, script):
            stage_fallbacks = {
                FollowupRouter.STAGE_CHART_READING: f"Aapki kundli dekhne par {domain} ke sanket kaafi clear active dikh rahe hain.",
                FollowupRouter.STAGE_SITUATION_ANALYSIS: f"Aapki current situation ke context mein {domain} ka prabhav ab zyada direct dikh raha hai.",
                FollowupRouter.STAGE_STRATEGY_GUIDANCE: f"Ab aapke liye {domain} mein strategy-based steps lena sabse zyada useful rahega.",
                FollowupRouter.STAGE_ACTION_PLAN: f"Ab samay hai ki {domain} ke liye clear aur practical action steps taiyar kiye jayein."
            }
        else:
            stage_fallbacks = {
                FollowupRouter.STAGE_CHART_READING: f"From your chart, the {domain} theme is clearly active.",
                FollowupRouter.STAGE_SITUATION_ANALYSIS: f"In your present situation, the {domain} influence appears more direct.",
                FollowupRouter.STAGE_STRATEGY_GUIDANCE: f"At this point, a strategy-led approach in {domain} will be most effective.",
                FollowupRouter.STAGE_ACTION_PLAN: f"This is the right phase to convert your {domain} insight into practical action steps."
            }

        fallback = stage_fallbacks.get(stage, stage_fallbacks[FollowupRouter.STAGE_CHART_READING])
        return ConsultationEngine._clean(llm_observation, fallback)

    @staticmethod
    def _planetary_reasoning(primary_driver, llm_cause, language, script):
        driver = (primary_driver or "Unknown").strip() or "Unknown"

        if ConsultationEngine._is_hi_dev(language, script):
            fallback = f"{driver} का प्रभाव अभी इस विषय की दिशा को गहराई से प्रभावित कर रहा है।"
        elif ConsultationEngine._is_hi_rom(language, script):
            fallback = f"{driver} ka prabhav abhi is vishay ki direction ko gehra tareeke se influence kar raha hai."
        else:
            fallback = f"{driver} is currently the key planetary influence shaping this area."

        if llm_cause and llm_cause.strip():
            return f"{fallback} {llm_cause.strip()}"
        return fallback

    @staticmethod
    def _timing_interpretation(momentum, llm_timing, language, script):
        m = (momentum or "Neutral").strip()

        if ConsultationEngine._is_hi_dev(language, script):
            mapping = {
                "Positive": "समय सहयोगी है, इसलिए निरंतर कदमों से अनुकूल परिणाम मिलने की संभावना मजबूत है।",
                "Neutral": "समय स्थिर है, इसलिए धैर्यपूर्ण और निरंतर प्रयास से सुधार स्पष्ट होगा।",
                "Challenging": "समय थोड़ा धीमा है, इसलिए संयमित और योजनाबद्ध तरीके से आगे बढ़ना बेहतर रहेगा।"
            }
        elif ConsultationEngine._is_hi_rom(language, script):
            mapping = {
                "Positive": "Samay supportive hai, isliye lagataar steps se favorable results milne ki sambhavna strong hai.",
                "Neutral": "Samay stable hai, isliye patience aur consistency se clear improvement milega.",
                "Challenging": "Samay thoda slow hai, isliye planned aur disciplined tareeke se aage badhna better rahega."
            }
        else:
            mapping = {
                "Positive": "Timing is supportive, so steady action can yield favorable progress.",
                "Neutral": "Timing is stable, so consistent and patient effort should improve outcomes.",
                "Challenging": "Timing is slower right now, so a disciplined and planned approach is important."
            }

        fallback = mapping.get(m, mapping["Neutral"])
        if llm_timing and llm_timing.strip():
            return f"{fallback} {llm_timing.strip()}"
        return fallback

    @staticmethod
    def _practical_advice(risk_factor, llm_guidance, language, script, stage):
        risk = (risk_factor or "Unknown").strip() or "Unknown"

        if ConsultationEngine._is_hi_dev(language, script):
            stage_line = {
                FollowupRouter.STAGE_SITUATION_ANALYSIS: "इस चरण में जल्दबाज़ी के बजाय स्पष्ट स्थिति समझना प्राथमिकता रखें।",
                FollowupRouter.STAGE_STRATEGY_GUIDANCE: "अब रणनीति-आधारित निर्णय लें और प्रतिक्रिया-आधारित निर्णयों से बचें।",
                FollowupRouter.STAGE_ACTION_PLAN: "अब छोटे, मापने योग्य और निरंतर कदम तय करें।"
            }.get(stage, "फिलहाल संतुलित और व्यावहारिक दृष्टिकोण रखें।")
            caution = f"सावधानी: {risk} से जुड़े निर्णयों में आवेग से बचें। {stage_line}"
        elif ConsultationEngine._is_hi_rom(language, script):
            stage_line = {
                FollowupRouter.STAGE_SITUATION_ANALYSIS: "Is stage par jaldbaazi ke bajay clear situation samajhna priority rakhein.",
                FollowupRouter.STAGE_STRATEGY_GUIDANCE: "Ab strategy-based decisions lein, reaction-based decisions se bachein.",
                FollowupRouter.STAGE_ACTION_PLAN: "Ab chhote, measurable aur consistent steps tay karein."
            }.get(stage, "Filhaal balanced aur practical approach rakhein.")
            caution = f"Savdhani: {risk} se jude decisions mein impulsive approach se bachein. {stage_line}"
        else:
            stage_line = {
                FollowupRouter.STAGE_SITUATION_ANALYSIS: "At this stage, prioritize clarity over speed.",
                FollowupRouter.STAGE_STRATEGY_GUIDANCE: "Now use strategy-led decisions instead of reactive moves.",
                FollowupRouter.STAGE_ACTION_PLAN: "Now define small, measurable, and consistent action steps."
            }.get(stage, "Maintain a balanced and practical approach.")
            caution = f"Caution: avoid impulsive decisions around {risk}. {stage_line}"

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
            return "क्या आप चाहेंगे कि मैं इसे अगले कदमों में स्पष्ट कर दूँ?"
        if ConsultationEngine._is_hi_rom(language, script):
            return "Kya aap chahenge ki main ise next steps mein clear kar doon?"
        return "Would you like me to break this into clear next steps?"

    @staticmethod
    def build_consultation_payload(
        domain,
        domain_data,
        llm_fields,
        language,
        script,
        followup_question,
        stage
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
                script=script,
                stage=stage
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
                script=script,
                stage=stage
            ),
            "followup_question": ConsultationEngine._followup_question(
                followup_question=followup_question,
                llm_followup=llm_fields.get("followup", ""),
                language=language,
                script=script
            )
        }
