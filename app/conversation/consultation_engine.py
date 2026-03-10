from app.conversation.life_theme_detector import LifeThemeDetector


class ConsultationEngine:
    STAGE_CHART_READING = "STAGE_CHART_READING"
    STAGE_SITUATION_ANALYSIS = "STAGE_SITUATION_ANALYSIS"
    STAGE_STRATEGY_GUIDANCE = "STAGE_STRATEGY_GUIDANCE"
    STAGE_ACTION_PLAN = "STAGE_ACTION_PLAN"

    @staticmethod
    def _is_hi_dev(language, script):
        return language == "hi" and script == "devanagari"

    @staticmethod
    def _is_hi_rom(language, script):
        return language == "hi" and script == "roman"

    @staticmethod
    def prepare_consultation_context(domain_data, age, life_stage, current_dasha, transits, user_goal):
        payload = dict(domain_data or {})
        payload["age"] = age
        payload["life_stage"] = life_stage
        payload["current_dasha"] = current_dasha or {}
        payload["transits"] = transits or {}
        payload["user_goal"] = user_goal

        return {
            "prompt_domain_data": payload,
            "age": age,
            "life_stage": life_stage,
            "current_dasha": current_dasha or {},
            "transits": transits or {},
            "user_goal": user_goal,
        }

    @staticmethod
    def next_stage(current_stage):
        if current_stage == ConsultationEngine.STAGE_CHART_READING:
            return ConsultationEngine.STAGE_SITUATION_ANALYSIS

        if current_stage == ConsultationEngine.STAGE_SITUATION_ANALYSIS:
            return ConsultationEngine.STAGE_STRATEGY_GUIDANCE

        if current_stage == ConsultationEngine.STAGE_STRATEGY_GUIDANCE:
            return ConsultationEngine.STAGE_ACTION_PLAN

        return ConsultationEngine.STAGE_ACTION_PLAN

    @staticmethod
    def build_opening(chart, language, script):
        dominant = LifeThemeDetector.detect(chart or {})

        if not dominant:
            return ""

        if ConsultationEngine._is_hi_dev(language, script):
            names = {
                "career": "करियर",
                "finance": "धन",
                "marriage": "विवाह",
                "health": "स्वास्थ्य",
            }
            return f"आपकी कुंडली का मुख्य सक्रिय विषय अभी {names.get(dominant, dominant)} है।"

        if ConsultationEngine._is_hi_rom(language, script):
            names = {
                "career": "career",
                "finance": "paisa",
                "marriage": "shaadi",
                "health": "health",
            }
            return f"Aapki kundli ka main active theme abhi {names.get(dominant, dominant)} hai."

        return f"Your chart's most active life theme right now is {dominant}."

    @staticmethod
    def _life_stage_label(life_stage, language, script):
        if ConsultationEngine._is_hi_dev(language, script):
            labels = {
                "childhood_phase": "सीखने और बुनियाद बनाने का समय",
                "early_adulthood": "दिशा तय करने का समय",
                "career_building": "कैरियर निर्माण का समय",
                "career_expansion": "कैरियर विस्तार का समय",
                "leadership_phase": "नेतृत्व और स्थिरता का समय",
                "legacy_phase": "अनुभव से विरासत बनाने का समय",
            }
        elif ConsultationEngine._is_hi_rom(language, script):
            labels = {
                "childhood_phase": "seekhne aur buniyad banane ka samay",
                "early_adulthood": "direction set karne ka samay",
                "career_building": "career build karne ka samay",
                "career_expansion": "career expansion ka samay",
                "leadership_phase": "leadership aur stability ka samay",
                "legacy_phase": "experience se legacy banane ka samay",
            }
        else:
            labels = {
                "childhood_phase": "a foundational learning phase",
                "early_adulthood": "a direction-setting phase",
                "career_building": "a career-building phase",
                "career_expansion": "a career-expansion phase",
                "leadership_phase": "a leadership and stability phase",
                "legacy_phase": "a legacy-focused phase",
            }

        return labels.get(life_stage, "")

    @staticmethod
    def _life_stage_context(age, life_stage, language, script):
        stage_label = ConsultationEngine._life_stage_label(life_stage, language, script)

        if ConsultationEngine._is_hi_dev(language, script):
            if age:
                if stage_label:
                    return f"आपकी उम्र अभी {age} वर्ष है और यह {stage_label} है।"
                return f"आपकी उम्र अभी {age} वर्ष है, इसलिए निर्णयों में दीर्घकालिक सोच रखना बेहतर रहेगा।"

            if stage_label:
                return f"यह समय {stage_label} माना जाता है।"

            return ""

        if ConsultationEngine._is_hi_rom(language, script):
            if age:
                if stage_label:
                    return f"Aapki age abhi {age} saal hai aur yeh {stage_label} hai."
                return f"Aapki age abhi {age} saal hai, isliye decisions mein long-term soch faydemand rahegi."

            if stage_label:
                return f"Yeh samay aam taur par {stage_label} hota hai."

            return ""

        if age:
            if stage_label:
                return f"You are currently {age}, which is usually {stage_label}."
            return f"You are currently {age}, so long-term planning will help more than reactive decisions."

        if stage_label:
            return f"This period is usually {stage_label}."

        return ""

    @staticmethod
    def _stage_bridge(stage, language, script):
        if ConsultationEngine._is_hi_dev(language, script):
            mapping = {
                ConsultationEngine.STAGE_CHART_READING: "पहले मैं कुंडली के मुख्य संकेत स्पष्ट करता हूँ।",
                ConsultationEngine.STAGE_SITUATION_ANALYSIS: "अब हम आपकी मौजूदा स्थिति पर फोकस करके इसे लागू करते हैं।",
                ConsultationEngine.STAGE_STRATEGY_GUIDANCE: "अब इस संकेत को रणनीति में बदलते हैं।",
                ConsultationEngine.STAGE_ACTION_PLAN: "अब इसे अगले व्यावहारिक कदमों में बदलते हैं।",
            }
            return mapping.get(stage, "")

        if ConsultationEngine._is_hi_rom(language, script):
            mapping = {
                ConsultationEngine.STAGE_CHART_READING: "Pehle main kundli ke main sanket clear karta hoon.",
                ConsultationEngine.STAGE_SITUATION_ANALYSIS: "Ab hum aapki current situation par focus karke ise apply karte hain.",
                ConsultationEngine.STAGE_STRATEGY_GUIDANCE: "Ab is sanket ko strategy mein convert karte hain.",
                ConsultationEngine.STAGE_ACTION_PLAN: "Ab ise next practical steps mein convert karte hain.",
            }
            return mapping.get(stage, "")

        mapping = {
            ConsultationEngine.STAGE_CHART_READING: "Let me first anchor this in your core chart signal.",
            ConsultationEngine.STAGE_SITUATION_ANALYSIS: "Now let's apply that signal to your present situation.",
            ConsultationEngine.STAGE_STRATEGY_GUIDANCE: "Now we convert that signal into strategy.",
            ConsultationEngine.STAGE_ACTION_PLAN: "Now we convert this into practical next steps.",
        }
        return mapping.get(stage, "")

    @staticmethod
    def _goal_context(user_goal, language, script):
        goal = (user_goal or "").strip().replace("_", " ")
        if not goal:
            return ""

        if ConsultationEngine._is_hi_dev(language, script):
            return f"आपका मुख्य लक्ष्य अभी {goal} है, इसलिए सलाह उसी दिशा में रखी जा रही है।"

        if ConsultationEngine._is_hi_rom(language, script):
            return f"Aapka main goal abhi {goal} hai, isliye guidance isi direction mein rakhi ja rahi hai."

        return f"Your primary goal right now is {goal}, so the guidance is aligned to it."

    @staticmethod
    def _chart_reasoning(domain, domain_data, language, script, stage):
        primary_driver = str(domain_data.get("primary_driver") or "").strip() or "Saturn"
        risk_factor = str(domain_data.get("risk_factor") or "").strip() or "impulsive decisions"
        momentum = str(domain_data.get("momentum") or "").strip() or "Neutral"

        if ConsultationEngine._is_hi_dev(language, script):
            if stage == ConsultationEngine.STAGE_CHART_READING:
                return (
                    f"{domain} विषय में अभी {primary_driver} का प्रभाव सबसे मजबूत दिख रहा है, "
                    f"और {risk_factor} से जुड़े फैसलों में सावधानी ज़रूरी है। "
                    f"चार्ट का momentum अभी {momentum} है।"
                )
            return "पहले बताए गए ग्रह-संकेत को दोहराने की जगह अब उसी संकेत को आपकी स्थिति में लागू करते हैं।"

        if ConsultationEngine._is_hi_rom(language, script):
            if stage == ConsultationEngine.STAGE_CHART_READING:
                return (
                    f"{domain} area mein abhi {primary_driver} ka prabhav sabse strong dikh raha hai, "
                    f"aur {risk_factor} se jude decisions mein caution zaroori hai. "
                    f"Chart momentum abhi {momentum} hai."
                )
            return "Pehle wale chart interpretation ko repeat kiye bina ab usi signal ko aapki situation mein apply karte hain."

        if stage == ConsultationEngine.STAGE_CHART_READING:
            return (
                f"In {domain}, {primary_driver} is the strongest influence right now, "
                f"so be careful around {risk_factor}. "
                f"The current momentum reads as {momentum}."
            )

        return "Instead of repeating the base chart reading, we now apply that same signal to your current context."

    @staticmethod
    def _dasha_timing(domain, current_dasha, transits, language, script, primary_driver):
        dasha = current_dasha or {}
        mahadasha = str(dasha.get("mahadasha") or "").strip()
        antardasha = str(dasha.get("antardasha") or "").strip()
        transit_data = transits or {}

        if ConsultationEngine._is_hi_dev(language, script):
            if mahadasha and antardasha:
                line = f"आपके chart में इस समय {mahadasha} की दशा और {antardasha} का अंतर्दशा चल रहा है।"
            elif mahadasha:
                line = f"आपके chart में इस समय {mahadasha} की दशा सक्रिय है।"
            else:
                line = "इस समय दशा-आधारित timing स्थिर है, इसलिए धैर्यपूर्ण execution बेहतर रहेगा।"

            if primary_driver and primary_driver in transit_data:
                house = transit_data.get(primary_driver)
                if house:
                    line += f" ट्रांजिट में {primary_driver} का प्रभाव भी house {house} से इस विषय को सक्रिय कर रहा है।"
                else:
                    line += f" ट्रांजिट में {primary_driver} भी इस विषय को सक्रिय कर रहा है।"

            return line

        if ConsultationEngine._is_hi_rom(language, script):
            if mahadasha and antardasha:
                line = f"Aapke chart mein iss samay {mahadasha} ki dasha aur {antardasha} ka antardasha chal raha hai."
            elif mahadasha:
                line = f"Aapke chart mein iss samay {mahadasha} ki dasha active hai."
            else:
                line = "Iss phase mein dasha timing neutral hai, isliye patient execution better rahega."

            if primary_driver and primary_driver in transit_data:
                house = transit_data.get(primary_driver)
                if house:
                    line += f" Transit mein {primary_driver} ka prabhav house {house} se bhi iss theme ko activate kar raha hai."
                else:
                    line += f" Transit mein {primary_driver} bhi iss theme ko activate kar raha hai."

            return line

        if mahadasha and antardasha:
            line = f"Your chart is currently running {mahadasha} mahadasha with {antardasha} antardasha."
        elif mahadasha:
            line = f"Your chart is currently in {mahadasha} mahadasha."
        else:
            line = "Dasha timing is currently steady, so patient execution is better than rushed moves."

        if primary_driver and primary_driver in transit_data:
            house = transit_data.get(primary_driver)
            if house:
                line += f" Transit influence of {primary_driver} from house {house} is reinforcing this theme."
            else:
                line += f" Transit influence of {primary_driver} is reinforcing this theme."

        return line

    @staticmethod
    def _practical_advice(ai_guidance, language, script, user_goal, stage):
        llm_line = " ".join(line.strip() for line in str(ai_guidance or "").splitlines() if line.strip())

        if ConsultationEngine._is_hi_dev(language, script):
            stage_tip = {
                ConsultationEngine.STAGE_CHART_READING: "अभी जल्दबाज़ी में बड़ा निर्णय न लें।",
                ConsultationEngine.STAGE_SITUATION_ANALYSIS: "पहले facts स्पष्ट करें, फिर अगला कदम लें।",
                ConsultationEngine.STAGE_STRATEGY_GUIDANCE: "अब fixed routine के साथ strategy execute करें।",
                ConsultationEngine.STAGE_ACTION_PLAN: "अगले 30 दिनों के measurable actions तय करके चलें।",
            }.get(stage, "संतुलित दृष्टिकोण रखें।")

            goal_line = ""
            if user_goal:
                goal_line = f" अपने {str(user_goal).replace('_', ' ')} लक्ष्य के हिसाब से steps चुनें।"

            return f"{stage_tip}{goal_line} {llm_line}".strip()

        if ConsultationEngine._is_hi_rom(language, script):
            stage_tip = {
                ConsultationEngine.STAGE_CHART_READING: "Abhi jaldbaazi mein bada decision mat lijiye.",
                ConsultationEngine.STAGE_SITUATION_ANALYSIS: "Pehle facts clear kariye, phir next step lijiye.",
                ConsultationEngine.STAGE_STRATEGY_GUIDANCE: "Ab fixed routine ke saath strategy execute kariye.",
                ConsultationEngine.STAGE_ACTION_PLAN: "Agle 30 din ke measurable actions set karke chaliye.",
            }.get(stage, "Balanced approach rakhiye.")

            goal_line = ""
            if user_goal:
                goal_line = f" Apne {str(user_goal).replace('_', ' ')} goal ke hisaab se steps choose kariye."

            return f"{stage_tip}{goal_line} {llm_line}".strip()

        stage_tip = {
            ConsultationEngine.STAGE_CHART_READING: "Avoid a rushed big move right now.",
            ConsultationEngine.STAGE_SITUATION_ANALYSIS: "Clarify facts first, then take the next step.",
            ConsultationEngine.STAGE_STRATEGY_GUIDANCE: "Execute with a fixed routine and strategy discipline.",
            ConsultationEngine.STAGE_ACTION_PLAN: "Set measurable 30-day actions and track them weekly.",
        }.get(stage, "Maintain a balanced approach.")

        goal_line = ""
        if user_goal:
            goal_line = f" Choose actions aligned with your {str(user_goal).replace('_', ' ')} goal."

        return f"{stage_tip}{goal_line} {llm_line}".strip()

    @staticmethod
    def default_followup_question(domain, language, script, stage):
        if ConsultationEngine._is_hi_dev(language, script):
            mapping = {
                ConsultationEngine.STAGE_CHART_READING: f"{domain} में आपकी मौजूदा स्थिति एक पंक्ति में बताएंगे?",
                ConsultationEngine.STAGE_SITUATION_ANALYSIS: "क्या आप चाहेंगे कि मैं इसे strategy-first तरीके से तोड़ दूँ?",
                ConsultationEngine.STAGE_STRATEGY_GUIDANCE: "क्या आप इस पर 30-दिन का action plan चाहते हैं?",
                ConsultationEngine.STAGE_ACTION_PLAN: "क्या आप चाहेंगे कि मैं weekly checkpoints भी सेट कर दूँ?",
            }
            return mapping.get(stage, "क्या आप इस विषय में और गहराई से जाना चाहेंगे?")

        if ConsultationEngine._is_hi_rom(language, script):
            mapping = {
                ConsultationEngine.STAGE_CHART_READING: f"{domain} mein aapki current situation ek line mein bataenge?",
                ConsultationEngine.STAGE_SITUATION_ANALYSIS: "Kya aap chahenge ki main ise strategy-first tareeke se tod doon?",
                ConsultationEngine.STAGE_STRATEGY_GUIDANCE: "Kya aap iske liye 30-day action plan chahte hain?",
                ConsultationEngine.STAGE_ACTION_PLAN: "Kya aap chahenge ki main weekly checkpoints bhi set kar doon?",
            }
            return mapping.get(stage, "Kya aap is topic mein aur depth chahte hain?")

        mapping = {
            ConsultationEngine.STAGE_CHART_READING: f"Can you share your current {domain} situation in one line?",
            ConsultationEngine.STAGE_SITUATION_ANALYSIS: "Would you like me to break this into a strategy-first approach?",
            ConsultationEngine.STAGE_STRATEGY_GUIDANCE: "Would you like a 30-day action plan for this?",
            ConsultationEngine.STAGE_ACTION_PLAN: "Do you want weekly checkpoints for execution?",
        }
        return mapping.get(stage, "Would you like to go deeper in this area?")

    @staticmethod
    def build_consultation_reply(
        domain,
        domain_data,
        ai_guidance,
        language,
        script,
        stage,
        age,
        life_stage,
        user_goal,
        current_dasha,
        transits,
        followup_question,
    ):
        domain_data = domain_data or {}
        primary_driver = str(domain_data.get("primary_driver") or "").strip() or "Saturn"

        parts = []

        stage_bridge = ConsultationEngine._stage_bridge(stage, language, script)
        life_stage_line = ConsultationEngine._life_stage_context(age, life_stage, language, script)
        goal_line = ConsultationEngine._goal_context(user_goal, language, script)
        reasoning_line = ConsultationEngine._chart_reasoning(domain, domain_data, language, script, stage)
        timing_line = ConsultationEngine._dasha_timing(domain, current_dasha, transits, language, script, primary_driver)
        advice_line = ConsultationEngine._practical_advice(ai_guidance, language, script, user_goal, stage)
        question_line = followup_question or ConsultationEngine.default_followup_question(domain, language, script, stage)

        for line in [stage_bridge, life_stage_line, goal_line]:
            if line:
                parts.append(line)

        parts.append(reasoning_line)
        parts.append(timing_line)
        parts.append(advice_line)
        parts.append(question_line)

        return "\n\n".join(part.strip() for part in parts if part and part.strip())
