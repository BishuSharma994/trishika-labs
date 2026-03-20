import hashlib
import json
import logging
import random
from datetime import datetime

# UPDATED IMPORTS: Import data dictionaries directly, NOT the class
from app.conversation.life_translation_engine import (
    OUTCOME_LINES,
    MECHANISM_LINES,
    ACTION_LIBRARY,
    PLANET_MAP,
    CAREER_MAP,
    FINANCE_MAP,
    HEALTH_MAP,
    MARRIAGE_MAP
)
from app.conversation.intent_router import IntentRouter
from app.conversation.language_engine import LanguageEngine
from app.conversation.memory_engine import MemoryEngine
from app.conversation.persona_layer import PersonaLayer
from app.ai import ask_ai  # Uses your existing AI function

logger = logging.getLogger(__name__)

class ConsultationEngine:
    @staticmethod
    def load_state(blob):
        if not blob:
            return None
        if isinstance(blob, dict):
            return blob
        if isinstance(blob, str):
            try:
                state = json.loads(blob)
            except Exception:
                return None
            return state if isinstance(state, dict) else None
        return None

    @staticmethod
    def dump_state(state):
        if state is None:
            return None
        if isinstance(state, str):
            return state
        return json.dumps(state, ensure_ascii=False)

    @staticmethod
    def prime_state(session_state_blob, language, topic, dob, time, place, gender, name):
        """Initialize the consultation state."""
        existing_state = ConsultationEngine.load_state(session_state_blob)
        if existing_state:
            return ConsultationEngine.dump_state(existing_state)

        return ConsultationEngine.dump_state({
            "topic": topic,
            "profile": {
                "name": name,
                "gender": gender,
                "dob": dob,
                "tob": time,
                "place": place,
            },
            "history": [],
            "params": {
                "language": language,
                "stage": "initial",
            },
        })

    @staticmethod
    def score_domain(domain):
        """Map user topic to chart domain keys."""
        mapping = {
            "career": "career",
            "finance": "finance",
            "health": "health",
            "marriage": "marriage",
            "relationship": "marriage",
            "business": "career",
            "money": "finance",
        }
        return mapping.get(str(domain).lower(), "career")

    @staticmethod
    def _translate_to_life_guidance(domain, planet, house, strength, language):
        """
        Local helper to generate guidance using imported dictionaries.
        Replaces the old LifeTranslationEngine.translate_to_life_guidance call.
        """
        # 1. Deterministic hashing for consistent responses
        hash_input = f"{domain}-{planet}-{house}-{strength}"
        seed = int(hashlib.sha256(hash_input.encode()).hexdigest(), 16)
        
        # 2. Select Outcome
        outcomes = OUTCOME_LINES.get(domain, {}).get(language, [])
        outcome = outcomes[seed % len(outcomes)] if outcomes else ""
        
        # 3. Select Mechanism
        mechanisms = MECHANISM_LINES.get(domain, {}).get(language, [])
        mechanism = mechanisms[seed % len(mechanisms)] if mechanisms else ""
        
        # 4. Select Action (3 items)
        actions_list = ACTION_LIBRARY.get(domain, {}).get(language, [])
        # Shuffle deterministically
        random.Random(seed).shuffle(actions_list)
        actions = actions_list[:3] if actions_list else []
        
        # 5. Determine Timeframe based on planet speed
        timeframes = {
            "Saturn": "4-6 weeks" if language == "en" else "4-6 hafte",
            "Jupiter": "2-3 months" if language == "en" else "2-3 mahine",
            "Mars": "2-3 weeks" if language == "en" else "2-3 hafte",
            "Sun": "1 month" if language == "en" else "1 mahina",
            "Venus": "3-4 weeks" if language == "en" else "3-4 hafte",
            "Mercury": "1-2 weeks" if language == "en" else "1-2 hafte",
            "Moon": "2-3 days" if language == "en" else "2-3 din",
            "Rahu": "Unpredictable" if language == "en" else "Anishchit",
            "Ketu": "Sudden" if language == "en" else "Achanak",
        }
        timeframe = timeframes.get(planet, "soon")
        
        return {
            "observation": outcome.replace("{planet}", planet),
            "cause": mechanism.replace("{planet}", planet),
            "action": actions,
            "timeframe": f"{timeframe} {'mein sudhar dikhna shuru hoga' if language == 'hi' else 'to see improvements'}"
        }

    @staticmethod
    def generate_response(
        domain,
        domain_data,
        language,
        script,
        stage,
        age,
        life_stage,
        user_goal,
        current_dasha,
        transits,
        persona_introduced,
        chart,
        theme_shown,
        user_text,
        session_state_blob,
        domain_switched,
        normalized_intent,
        user_id=None,  # Added user_id
    ):
        """
        Main response generator.
        - First response: Uses template (fast & structured).
        - Follow-ups: Uses GPT-4o (smart & contextual).
        """
        state_blob = ConsultationEngine.dump_state(
            ConsultationEngine.load_state(session_state_blob) or {}
        )
        
        # 1. Handle Garbage Input (e.g. "8", "??", "asdf")
        if len(user_text) < 2 and not user_text.isalnum():
             return {
                "text": "Aap kya jaanna chahte hain? (What would you like to know?)",
                "state_blob": state_blob
            }

        # 2. Check for Follow-up (Conversation History Exists)
        is_follow_up = False
        if user_id:
            history = MemoryEngine.get_context(user_id)
            # If we have history (System + User + Bot + User...), it's a follow-up
            if len(history) > 2: 
                is_follow_up = True

        # 3. If Follow-up OR Specific Question -> Use AI
        if is_follow_up or (len(user_text.split()) > 2):
            return ConsultationEngine._generate_ai_response(
                user_id, user_text, chart, domain, language, script, state_blob
            )

        # 4. First Response (Template-based)
        # Fallback to template if it's the very first interaction or short keyword
        try:
            # Extract chart factors
            planet = domain_data.get("planet", "Saturn")
            house = domain_data.get("house", 10)
            strength = domain_data.get("strength", "neutral")
            
            # Use local helper instead of class method
            guidance = ConsultationEngine._translate_to_life_guidance(
                domain, planet, house, strength, language
            )
            
            # Format the template response
            if language == "hi":
                response_text = (
                    f"Observation: {guidance['observation']}\n"
                    f"Cause: {guidance['cause']}\n"
                    f"Action: 1. {guidance['action'][0]} 2. {guidance['action'][1]}\n"
                    f"Timeframe: {guidance['timeframe']}."
                )
            else:
                response_text = (
                    f"Observation: {guidance['observation']}\n"
                    f"Cause: {guidance['cause']}\n"
                    f"Action: 1. {guidance['action'][0]} 2. {guidance['action'][1]}\n"
                    f"Timeframe: {guidance['timeframe']}."
                )

            return {
                "text": response_text,
                "state_blob": state_blob
            }

        except Exception as e:
            logger.error(f"Template generation failed: {e}")
            # Fallback to AI if template fails
            return ConsultationEngine._generate_ai_response(
                user_id, user_text, chart, domain, language, script, state_blob
            )

    @staticmethod
    def _generate_ai_response(user_id, user_text, chart, domain, language, script, state_blob):
        """
        Generates a contextual AI response using GPT-4o.
        """
        try:
            # 1. Get History
            history = MemoryEngine.get_context(user_id) if user_id else []
            
            # 2. Prepare System Prompt with Chart Data
            system_prompt = (
                f"You are Arjun, an expert Vedic Astrologer. Keep answers short (under 60 words). "
                f"Speak in {language} ({script} script). "
                f"User is asking about {domain}. "
                f"Chart Data: {json.dumps(chart, default=str)}. "
                f"Be empathetic but direct. Give actionable advice."
            )
            
            # 3. Construct Messages for AI
            messages = [{"role": "system", "content": system_prompt}] + history
            
            # 4. Call AI
            ai_reply = ask_ai(messages)  # Ensure ask_ai returns a string
            
            return {
                "text": ai_reply,
                "state_blob": state_blob
            }
            
        except Exception as e:
            logger.error(f"AI generation failed: {e}")
            return {
                "text": "Technical glitch. Please ask again.",
                "state_blob": state_blob
            }
