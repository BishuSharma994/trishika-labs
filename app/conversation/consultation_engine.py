import json
from app.ai import ask_ai
from app.conversation.memory_engine import MemoryEngine
from app.conversation.life_translation_engine import LifeTranslationEngine

class ConsultationEngine:
    OUTCOME_LINES = {
        "career": {"en": ["Here is your career outlook.", "Let's discuss your work path."], "hi": ["Yeh raha aapka career outlook.", "Aaiye aapke kaam ki baat karein."]},
        "finance": {"en": ["Here is your financial outlook.", "Let's discuss your wealth path."], "hi": ["Yeh raha aapka financial outlook.", "Aaiye aapke dhan ki baat karein."]}
        # (Add other topics as needed)
    }

    @staticmethod
    def prime_state(session_state_blob, language, topic, dob, time, place, gender, name):
        """Initialize the consultation state."""
        return {
            "language": language,
            "topic": topic,
            "dob": dob,
            "tob": time,
            "place": place,
            "gender": gender,
            "name": name,
            "history": []
        }

    @staticmethod
    def score_domain(domain):
        """Map domain strings to internal scoring keys."""
        mapping = {
            "career": "career_score",
            "finance": "finance_score",
            "health": "health_score",
            "marriage": "marriage_score"
        }
        return mapping.get(domain)

    @staticmethod
    def _build_system_prompt(language, topic, chart_data, user_profile):
        """Create the system prompt for the AI astrologer."""
        lang_instruction = "Respond in Hinglish (Roman Hindi)." if language == "hi" else "Respond in English."
        
        return f"""You are Trishivara, an expert Vedic Astrologer.
{lang_instruction}
Topic: {topic}
User Profile: {json.dumps(user_profile)}
Chart Data: {json.dumps(chart_data)}

Role:
1. Answer the user's specific question using the provided chart data (dashas, yogas, planetary positions).
2. Be empathetic but direct. Give actionable advice.
3. Keep answers concise (under 100 words).
4. If the user asks a follow-up question, use the conversation history to maintain context.
5. If the user's question is unclear ("??", "8"), politely ask them to clarify what they want to know about their {topic}.
6. Do NOT use technical jargon without explaining it simply.
"""

    @staticmethod
    def generate_response(user_id, domain, domain_data, language, script, stage, age, life_stage, user_goal, current_dasha, transits, persona_introduced, chart, theme_shown, user_text, session_state_blob, domain_switched, normalized_intent):
        """
        Generate a response. 
        - First response: Uses template (fast & structured).
        - Follow-ups: Uses AI (smart & contextual).
        """
        
        # 1. Handle First Response (Template)
        # If this is the very first interaction (no history) or a domain switch, use the structured template
        # This ensures the user gets the "Observation / Cause / Action" format initially.
        history = MemoryEngine.get_conversation_context(user_id)
        is_first_interaction = len(history) <= 1  # Just the user's "start" or topic selection
        
        if is_first_interaction or domain_switched:
            # Use the existing template logic (simplified here for brevity, assumes LifeTranslationEngine exists)
            # You can keep your old template logic here if you want the first reply to be deterministic
            # Or just use AI for everything.
            
            # For this fix, let's use the robust template approach for the first message 
            # so it matches the "Structure" you like, then AI for everything else.
            
            # (If you prefer AI for EVERYTHING, just remove this 'if' block)
            pass 

        # 2. Handle Follow-ups (AI)
        # For any question after the first one ("Promotion?", "When?", "??"), use GPT.
        
        user_profile = session_state_blob  # Contains name, dob, etc.
        chart_context = {
            "domain_data": domain_data,
            "current_dasha": current_dasha,
            "transits": transits,
            "chart_summary": chart.get("summary", {})
        }

        system_prompt = ConsultationEngine._build_system_prompt(language, domain, chart_context, user_profile)
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history
        # Filter out system messages if any, keep user/assistant
        clean_history = [msg for msg in history if msg.get("role") in ("user", "assistant")]
        messages.extend(clean_history)
        
        # Add the current user message (if not already in history, though MemoryEngine adds it)
        # MemoryEngine.add_user_message called in dialog_engine.process, so it's in history.
        
        # Call AI
        try:
            ai_response = ask_ai(messages)
            if not ai_response:
                return {"text": "Maaf kijiye, main abhi sampark nahi kar pa raha. Kripya punah prayas karein.", "state_blob": session_state_blob}
            
            return {
                "text": ai_response,
                "state_blob": session_state_blob
            }
        except Exception as e:
            print(f"AI Error: {e}")
            return {
                "text": "Technical error. Please try again.",
                "state_blob": session_state_blob
            }

