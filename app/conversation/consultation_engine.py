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
    def _life_stage_label(life_stage, language, script):
        if ConsultationEngine._is_hi_dev(language, script):
            mapping = {
                "childhood_phase": "सीखने और बुनियाद मजबूत करने का चरण",
                "early_adulthood": "दिशा तय करने और अवसर पहचानने का चरण",
                "career_building": "कैरियर निर्माण और कौशल विस्तार का चरण",
                "career_expansion": "कैरियर विस्तार और जिम्मेदारी बढ़ने का चरण",
                "leadership_phase": "नेतृत्व और स्थिरता का चरण",
                "legacy_phase": "अनुभव साझा करने और विरासत बनाने का चरण"
            }
        elif ConsultationEngine._is_hi_rom(language, script):
            mapping = {
                "childhood_phase": "seekhne aur buniyad majboot karne ka phase",
                "early_adulthood": "direction set karne aur opportunities pehchanne ka phase",
                "career_building": "career build karne aur skills badhane ka phase",
                "career_expansion": "career expansion aur zimmedari badhne ka phase",
                "leadership_phase": "leadership aur stability ka phase",
                "legacy_phase": "anubhav share karne aur legacy banane ka phase"
            }
        else:
            mapping = {
                "childhood_phase": "a foundational learning phase",
                "early_adulthood": "a direction-setting phase",
                "career_building": "a career-building phase",
                "career_expansion": "a career-expansion phase",
                "leadership_phase": "a leadership and stability phase",
                "legacy_phase": "a legacy-focused phase"
            }

        return mapping.get(life_stage, "")

    @staticmethod
    def _life_stage_context(age, life_stage, language, script):
        stage_label = ConsultationEngine._life_stage_label(life_stage, language, script)

        if ConsultationEngine._is_hi_dev(language, script):
            if age is None and not stage_label:
                return ""
            if age is None:
                return f"जीवन का यह समय {stage_label} के रूप में काम करता है।"
            if stage_label:
                return f"आपकी उम्र अभी {age} वर्ष है और यह {stage_label} माना जाता है।"
            return f"आपकी उम्र अभी {age} वर्ष है, इसलिए निर्णयों में संतुलित और दीर्घकालिक दृष्टि रखना उपयोगी रहेगा।"

        if ConsultationEngine._is_hi_rom(language, script):
            if age is None and not stage_label:
                return ""
            if age is None:
                return f"Jeevan ka yeh samay aam taur par {stage_label} maana jata hai."
            if stage_label:
                return f"Aapki umr abhi {age} saal hai aur yeh {stage_label} hota hai."
            return f"Aapki umr abhi {age} saal hai, isliye balanced aur long-term nazariya rakhna faydemand rahega."

        if age is None and not stage_label:
            return ""
        if age is None:
            return f"This stage of life is typically {stage_label}."
        if stage_label:
            return f"You are currently {age}, and this is usually {stage_label}."
        return f"You are currently {age}, so a balanced long-term approach will serve you well."

    @staticmethod
    def _observation(domain, llm_observation, language, script, stage, age, life_stage):
        if ConsultationEngine._is_hi_dev(language, script):
            stage_fallbacks = {
                FollowupRouter.STAGE_CHART_READING: f"कुंडली संकेत देते हैं कि {domain} का विषय अभी सक्रिय है।",
                FollowupRouter.STAGE_SITUATION_ANALYSIS: f"आपकी वर्तमान स्थिति में {domain} का प्रभाव अधिक स्पष्ट रूप से सामने आ रहा है।",
                FollowupRouter.STAGE_STRATEGY_GUIDANCE: f"अब {domain} में रणनीतिक कदम लेना आपके लिए अधिक लाभकारी रहेगा।",
                FollowupRouter.STAGE_ACTION_PLAN: f"अब {domain} के लिए व्यावहारिक और क्रमबद्ध कदम तय करने का समय है।"
            }
        elif ConsultationEngine._is_hi_rom(language, script):
            stage_fallbacks = {
                FollowupRouter.STAGE_CHART_READING: f"Kundli sanket dete hain ki {domain} ka vishay abhi active hai.",
                FollowupRouter.STAGE_SITUATION_ANALYSIS: f"Aapki current situation mein {domain} ka prabhav ab zyada clear dikh raha hai.",
                FollowupRouter.STAGE_STRATEGY_GUIDANCE: f"Ab {domain} mein strategy-based steps lena aapke liye zyada faydemand rahega.",
                FollowupRouter.STAGE_ACTION_PLAN: f"Ab {domain} ke liye practical aur step-wise action plan banana sahi rahega."
            }
        else:
            stage_fallbacks = {
                FollowupRouter.STAGE_CHART_READING: f"Your chart shows that {domain} is currently an active life theme.",
                FollowupRouter.STAGE_SITUATION_ANALYSIS: f"In your present situation, {domain} is becoming more directly influential.",
                FollowupRouter.STAGE_STRATEGY_GUIDANCE: f"At this point, a strategy-led approach in {domain} will help most.",
                FollowupRouter.STAGE_ACTION_PLAN: f"This is the right time to turn your {domain} insight into practical actions."
            }

        fallback = stage_fallbacks.get(stage, stage_fallbacks[FollowupRouter.STAGE_CHART_READING])
        observation = ConsultationEngine._clean(llm_observation, fallback)
        life_stage_context = ConsultationEngine._life_stage_context(age, life_stage, language, script)

        if life_stage_context:
            return f"{life_stage_context} {observation}".strip()

        return observation

    @staticmethod
    def _planetary_reasoning(primary_driver, llm_cause, language, script):
        driver = (primary_driver or "Unknown").strip() or "Unknown"

        if ConsultationEngine._is_hi_dev(language, script):
            fallback = f"इस विषय की दिशा पर अभी {driver} का प्रभाव सबसे अधिक दिखाई दे रहा है।"
        elif ConsultationEngine._is_hi_rom(language, script):
            fallback = f"Is vishay ki direction par abhi {driver} ka prabhav sabse zyada dikh raha hai."
        else:
            fallback = f"{driver} is currently the strongest planetary influence in this area."

        if llm_cause and llm_cause.strip():
            return f"{fallback} {llm_cause.strip()}"

        return fallback

    @staticmethod
    def _momentum_fallback(momentum, language, script):
        m = (momentum or "Neutral").strip()

        if ConsultationEngine._is_hi_dev(language, script):
            mapping = {
                "Positive": "समय सहयोगी है, इसलिए निरंतर प्रयास से प्रगति तेज हो सकती है।",
                "Neutral": "समय स्थिर है, इसलिए धैर्यपूर्ण और लगातार प्रयास परिणाम देगा।",
                "Challenging": "समय थोड़ा धीमा है, इसलिए अनुशासित और योजनाबद्ध तरीके से आगे बढ़ना बेहतर होगा।"
            }
        elif ConsultationEngine._is_hi_rom(language, script):
            mapping = {
                "Positive": "Samay supportive hai, isliye lagataar mehnat se progress tez ho sakti hai.",
                "Neutral": "Samay stable hai, isliye patience aur consistency se results milenge.",
                "Challenging": "Samay thoda slow hai, isliye disciplined aur planned tareeke se aage badhna better hoga."
            }
        else:
            mapping = {
                "Positive": "Timing is supportive, so consistent effort can move things quickly.",
                "Neutral": "Timing is steady, so patient consistency will deliver results.",
                "Challenging": "Timing is slower now, so a disciplined and planned approach is best."
            }

        return mapping.get(m, mapping["Neutral"])

    @staticmethod
    def _dasha_line(current_dasha, language, script):
        dasha = current_dasha or {}
        md = str(dasha.get("mahadasha") or "").strip()
        ad = str(dasha.get("antardasha") or "").strip()

        if ConsultationEngine._is_hi_dev(language, script):
            if md and ad:
                return f"आपके चार्ट में इस समय {md} की दशा और {ad} का अंतर्दशा चल रहा है।", md, ad
            if md:
                return f"आपके चार्ट में इस समय {md} की दशा सक्रिय है।", md, ad
            if ad:
                return f"इस समय {ad} का अंतर्दशा प्रभाव दिखा रहा है।", md, ad
            return "", md, ad

        if ConsultationEngine._is_hi_rom(language, script):
            if md and ad:
                return f"Aapke chart mein is samay {md} ki dasha aur {ad} ka antardasha chal raha hai.", md, ad
            if md:
                return f"Aapke chart mein is samay {md} ki dasha active hai.", md, ad
            if ad:
                return f"Is samay {ad} ka antardasha apna prabhav dikha raha hai.", md, ad
            return "", md, ad

        if md and ad:
            return f"Your chart is currently running {md} mahadasha with {ad} antardasha.", md, ad
        if md:
            return f"Your chart is currently in {md} mahadasha.", md, ad
        if ad:
            return f"The current antardasha influence is {ad}.", md, ad
        return "", md, ad

    @staticmethod
    def _timing_interpretation(domain, primary_driver, momentum, current_dasha, transits, llm_timing, language, script):
        domain_ruler = (primary_driver or "").strip()
        dasha_line, md, ad = ConsultationEngine._dasha_line(current_dasha, language, script)

        is_strong_window = bool(domain_ruler and (domain_ruler == md or domain_ruler == ad))
        momentum_line = ConsultationEngine._momentum_fallback(momentum, language, script)

        if ConsultationEngine._is_hi_dev(language, script):
            if is_strong_window:
                match_line = f"{domain_ruler} की सक्रियता के कारण {domain} के लिए समय खिड़की अपेक्षाकृत मजबूत बन रही है।"
            else:
                match_line = momentum_line
        elif ConsultationEngine._is_hi_rom(language, script):
            if is_strong_window:
                match_line = f"{domain_ruler} ke active hone se {domain} ke liye timing window relatively strong ban rahi hai."
            else:
                match_line = momentum_line
        else:
            if is_strong_window:
                match_line = f"Because {domain_ruler} is active in dasha, the timing window for {domain} is relatively stronger."
            else:
                match_line = momentum_line

        transit_line = ""
        transit = transits or {}
        if domain_ruler and domain_ruler in transit:
            house = transit.get(domain_ruler)
            if ConsultationEngine._is_hi_dev(language, script):
                transit_line = f"ट्रांजिट में {domain_ruler} का प्रभाव भी इस विषय को सक्रिय कर रहा है।"
            elif ConsultationEngine._is_hi_rom(language, script):
                transit_line = f"Transit mein {domain_ruler} ka prabhav bhi is vishay ko activate kar raha hai."
            else:
                transit_line = f"Transit influence of {domain_ruler} is also activating this theme."

            if house:
                if ConsultationEngine._is_hi_dev(language, script):
                    transit_line += f" यह प्रभाव मुख्यतः घर {house} से दिखाई देता है।"
                elif ConsultationEngine._is_hi_rom(language, script):
                    transit_line += f" Yeh effect primarily house {house} se dikh raha hai."
                else:
                    transit_line += f" This influence is currently visible from house {house}."

        parts = []
        if dasha_line:
            parts.append(dasha_line)
        if match_line:
            parts.append(match_line)
        if transit_line:
            parts.append(transit_line)

        fallback = " ".join(parts).strip() or momentum_line

        if llm_timing and llm_timing.strip():
            return f"{fallback} {llm_timing.strip()}"

        return fallback

    @staticmethod
    def _practical_advice(risk_factor, llm_guidance, language, script, stage):
        risk = (risk_factor or "Unknown").strip() or "Unknown"

        if ConsultationEngine._is_hi_dev(language, script):
            stage_line = {
                FollowupRouter.STAGE_SITUATION_ANALYSIS: "इस चरण में पहले स्थिति स्पष्ट करें, फिर बड़ा निर्णय लें।",
                FollowupRouter.STAGE_STRATEGY_GUIDANCE: "अब प्रतिक्रिया नहीं, रणनीति-आधारित निर्णय अधिक लाभ देंगे।",
                FollowupRouter.STAGE_ACTION_PLAN: "अब छोटे और मापने योग्य कदम लेकर निरंतरता बनाए रखें।"
            }.get(stage, "फिलहाल संतुलित और व्यावहारिक दृष्टिकोण रखें।")
            caution = f"{risk} से जुड़े मामलों में जल्दबाज़ी से बचना महत्वपूर्ण रहेगा। {stage_line}"
        elif ConsultationEngine._is_hi_rom(language, script):
            stage_line = {
                FollowupRouter.STAGE_SITUATION_ANALYSIS: "Is stage par pehle situation clear karein, phir bada decision lein.",
                FollowupRouter.STAGE_STRATEGY_GUIDANCE: "Ab reaction nahi, strategy-based decisions zyada fayda denge.",
                FollowupRouter.STAGE_ACTION_PLAN: "Ab chhote aur measurable steps lekar consistency banaye rakhein."
            }.get(stage, "Filhaal balanced aur practical approach rakhein.")
            caution = f"{risk} se jude mamlo mein jaldbaazi se bachna important rahega. {stage_line}"
        else:
            stage_line = {
                FollowupRouter.STAGE_SITUATION_ANALYSIS: "At this stage, get clarity before making a big move.",
                FollowupRouter.STAGE_STRATEGY_GUIDANCE: "Now strategy-led decisions will work better than reactive moves.",
                FollowupRouter.STAGE_ACTION_PLAN: "Now execute with small measurable steps and consistency."
            }.get(stage, "Maintain a balanced and practical approach.")
            caution = f"Avoid rushed decisions around {risk}. {stage_line}"

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
            return "क्या आप चाहेंगे कि मैं इसे आपके लिए अगले स्पष्ट कदमों में बाँट दूँ?"
        if ConsultationEngine._is_hi_rom(language, script):
            return "Kya aap chahenge ki main ise aapke liye next clear steps mein tod doon?"
        return "Would you like me to break this into clear next steps for you?"

    @staticmethod
    def build_consultation_payload(
        domain,
        domain_data,
        llm_fields,
        language,
        script,
        followup_question,
        stage,
        age,
        life_stage,
        current_dasha,
        transits
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
                stage=stage,
                age=age,
                life_stage=life_stage
            ),
            "planetary_reasoning": ConsultationEngine._planetary_reasoning(
                primary_driver=primary_driver,
                llm_cause=llm_fields.get("cause", ""),
                language=language,
                script=script
            ),
            "timing_interpretation": ConsultationEngine._timing_interpretation(
                domain=domain,
                primary_driver=primary_driver,
                momentum=momentum,
                current_dasha=current_dasha,
                transits=transits,
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
