from app.conversation.prompt_builder import AstrologerPrompts


class FollowupRouter:

    STAGE_BIRTHDATA = "STAGE_BIRTHDATA"
    STAGE_CHART_READING = "STAGE_CHART_READING"
    STAGE_SITUATION_ANALYSIS = "STAGE_SITUATION_ANALYSIS"
    STAGE_STRATEGY_GUIDANCE = "STAGE_STRATEGY_GUIDANCE"
    STAGE_ACTION_PLAN = "STAGE_ACTION_PLAN"

    OPTION_KEYWORDS = {
        "career": {
            "job_switch": ["switch", "change job", "new job", "job switch", "naukri", "job", "बदल", "नई नौकरी"],
            "promotion": ["promotion", "growth", "raise", "salary", "increment", "प्रमोशन", "वृद्धि"],
            "business": ["business", "startup", "entrepreneur", "vyapar", "व्यापार"]
        },
        "finance": {
            "savings": ["saving", "savings", "save", "bachat", "बचत"],
            "investment": ["investment", "invest", "sip", "stocks", "mutual", "nivesh", "निवेश"],
            "debt": ["debt", "loan", "emi", "karz", "कर्ज", "ऋण"]
        },
        "marriage": {
            "new_relationship": ["single", "new", "naya", "नया", "new relation"],
            "existing_relationship": ["already married", "married", "shaadi ho chuki", "rishta", "मौजूदा", "शादी हो चुकी", "विवाहित", "पति", "पत्नी"],
            "timing": ["when", "kab", "timing", "date", "कब", "समय"]
        },
        "health": {
            "stress": ["stress", "anxiety", "mental", "तनाव", "चिंता"],
            "lifestyle": ["lifestyle", "routine", "sleep", "diet", "जीवनशैली", "रूटीन"],
            "medical": ["disease", "illness", "medical", "diagnosis", "hospital", "बीमारी", "स्वास्थ्य समस्या"]
        }
    }

    INITIAL_QUESTIONS = {
        "career": {
            "en": "Are you focused more on job switch, promotion, or business direction right now?",
            "devanagari": "क्या आपका फोकस अभी नौकरी बदलने, प्रमोशन, या बिज़नेस दिशा पर है?",
            "roman": "Kya aapka focus abhi job switch, promotion, ya business direction par hai?"
        },
        "finance": {
            "en": "Are you currently prioritizing savings, investments, or debt management?",
            "devanagari": "क्या आप अभी बचत, निवेश, या कर्ज प्रबंधन को प्राथमिकता दे रहे हैं?",
            "roman": "Kya aap abhi savings, investment, ya debt management ko priority de rahe hain?"
        },
        "marriage": {
            "en": "Are you seeking clarity in an existing marriage, or relationship growth guidance?",
            "devanagari": "क्या आप मौजूदा विवाह में स्पष्टता चाहते हैं या संबंध वृद्धि पर मार्गदर्शन?",
            "roman": "Kya aap existing shaadi mein clarity chahte hain ya relationship growth guidance?"
        },
        "health": {
            "en": "Is your concern mostly stress, lifestyle balance, or a specific health issue?",
            "devanagari": "क्या आपकी चिंता मुख्यतः तनाव, लाइफस्टाइल संतुलन, या किसी विशेष स्वास्थ्य समस्या से जुड़ी है?",
            "roman": "Kya aapki concern mostly stress, lifestyle balance, ya kisi specific health issue se judi hai?"
        }
    }

    STAGE_QUESTIONS = {
        STAGE_SITUATION_ANALYSIS: {
            "en": "Can you share your current situation in one line so I can read this more precisely?",
            "devanagari": "क्या आप अपनी वर्तमान स्थिति एक पंक्ति में बता सकते हैं ताकि मैं इसे और सटीक देख सकूँ?",
            "roman": "Kya aap apni current situation ek line mein bata sakte hain taaki main ise aur precise dekh sakun?"
        },
        STAGE_STRATEGY_GUIDANCE: {
            "en": "Would you like a strategy-first approach or a timing-first approach from here?",
            "devanagari": "क्या आप यहाँ से रणनीति-प्रथम मार्गदर्शन चाहते हैं या समय-प्रथम मार्गदर्शन?",
            "roman": "Kya aap yahan se strategy-first guidance chahte hain ya timing-first guidance?"
        },
        STAGE_ACTION_PLAN: {
            "en": "Do you want a practical 30-day action plan for this area?",
            "devanagari": "क्या आप इस विषय के लिए व्यावहारिक 30-दिन की कार्ययोजना चाहते हैं?",
            "roman": "Kya aap is vishay ke liye practical 30-din ki action plan chahte hain?"
        }
    }

    @staticmethod
    def _lang_key(language, script):
        if language == "hi" and script == "devanagari":
            return "devanagari"
        if language == "hi" and script == "roman":
            return "roman"
        return "en"

    @staticmethod
    def get_initial_followup_question(domain, language, script):
        domain_map = FollowupRouter.INITIAL_QUESTIONS.get(domain, {})
        return domain_map.get(
            FollowupRouter._lang_key(language, script),
            "Would you like to go deeper in this area?"
        )

    @staticmethod
    def detect_followup_focus(domain, text):
        if not domain or not text:
            return "general"

        t = text.lower()
        options = FollowupRouter.OPTION_KEYWORDS.get(domain, {})

        for focus, keywords in options.items():
            for token in keywords:
                if token.lower() in t:
                    return focus

        return "general"

    @staticmethod
    def is_followup_answer(text, last_followup_question, domain):
        if not text or not last_followup_question:
            return False

        focus = FollowupRouter.detect_followup_focus(domain, text)
        if focus != "general":
            return True

        token_count = len(text.split())
        if token_count <= 14 and not text.strip().startswith("/"):
            return True

        return False

    @staticmethod
    def next_stage(current_stage):
        if current_stage == FollowupRouter.STAGE_CHART_READING:
            return FollowupRouter.STAGE_SITUATION_ANALYSIS
        if current_stage == FollowupRouter.STAGE_SITUATION_ANALYSIS:
            return FollowupRouter.STAGE_STRATEGY_GUIDANCE
        if current_stage == FollowupRouter.STAGE_STRATEGY_GUIDANCE:
            return FollowupRouter.STAGE_ACTION_PLAN
        return FollowupRouter.STAGE_ACTION_PLAN

    @staticmethod
    def next_followup_question(next_stage, language, script, previous_question=None):
        question_map = FollowupRouter.STAGE_QUESTIONS.get(next_stage, {})
        question = question_map.get(
            FollowupRouter._lang_key(language, script),
            ""
        )

        if previous_question and question and question.strip() == previous_question.strip():
            if language == "hi" and script == "devanagari":
                return "क्या आप चाहेंगे कि मैं इसे आपके लिए स्पष्ट चरणों में बाँट दूँ?"
            if language == "hi" and script == "roman":
                return "Kya aap chahenge ki main ise aapke liye clear steps mein tod doon?"
            return "Would you like me to break this into clear next steps for you?"

        return question

    @staticmethod
    def build_followup_prompt(
        domain,
        domain_data,
        language,
        script,
        user_id,
        user_text,
        stage,
        focus
    ):
        base_prompt = AstrologerPrompts.build_domain_prompt(
            domain=domain,
            domain_data=domain_data,
            language=language,
            script=script,
            user_id=user_id,
            question=user_text
        )

        return (
            f"{base_prompt}\n\n"
            f"Consultation stage: {stage}\n"
            f"Follow-up focus: {focus}\n"
            f"User follow-up answer: {user_text}\n\n"
            "Return ONLY one valid JSON object with keys:\n"
            "observation, cause, timing, guidance, followup\n\n"
            "Rules:\n"
            "- Keep each field conversational and concise.\n"
            "- Do not mention scores, rankings, engines, or internals.\n"
            "- Do not output markdown, headings, or text outside JSON.\n"
        )
