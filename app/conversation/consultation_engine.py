import hashlib
import json
import logging
import random
from datetime import datetime

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
from app.ai import ask_ai

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
        hash_input = f"{domain}-{planet}-{house}-{strength}"
        seed = int(hashlib.sha256(hash_input.encode()).hexdigest(), 16)
        
        outcomes = OUTCOME_LINES.get(domain, {}).get(language, [])
        outcome = outcomes[seed % len(outcomes)] if outcomes else ""
        
        mechanisms = MECHANISM_LINES.get(domain, {}).get(language, [])
        mechanism = mechanisms[seed % len(mechanisms)] if mechanisms else ""
        
        actions_list = ACTION_LIBRARY.get(domain, {}).get(language, [])
        random.Random(seed).shuffle(actions_list)
        actions = actions_list[:3] if actions_list else []
        
        timeframes = {
            "Saturn": "4-6 hafte", "Jupiter": "2-3 mahine", "Mars": "2-3 hafte",
            "Sun": "1 mahina", "Venus": "3-4 hafte", "Mercury": "1-2 hafte",
            "Moon": "2-3 din", "Rahu": "Anishchit", "Ketu": "Achanak",
        }
        timeframe = timeframes.get(planet, "jaldi")

        # === HINDI PLANET NAMES WHEN USER IS IN HINDI MODE ===
        if language == "hi":
            hindi_planets = {
                "Venus": "Shukra", "Saturn": "Shani", "Jupiter": "Guru",
                "Mars": "Mangal", "Mercury": "Budh", "Sun": "Surya",
                "Moon": "Chandra", "Rahu": "Rahu", "Ketu": "Ketu"
            }
            planet = hindi_planets.get(planet, planet)
        
        return {
            "observation": outcome.replace("{planet}", planet),
            "cause": mechanism.replace("{planet}", planet),
            "action": actions,
            "timeframe": f"{timeframe} mein sudhar dikhna shuru ho jayega"
        }

    @staticmethod
    def generate_response(
        domain, domain_data, language, script, stage, age, life_stage,
        user_goal, current_dasha, transits, persona_introduced, chart,
        theme_shown, user_text, session_state_blob, domain_switched,
        normalized_intent, user_id=None,
    ):
        state_blob = ConsultationEngine.dump_state(
            ConsultationEngine.load_state(session_state_blob) or {}
        )
        
        if len(user_text) < 2 and not user_text.isalnum():
            return {
                "text": "Aap kya jaanna chahte hain?",
                "state_blob": state_blob
            }

        is_follow_up = False
        if user_id:
            history = MemoryEngine.get_context(user_id)
            if len(history) > 2:
                is_follow_up = True

        if is_follow_up or len(user_text.split()) > 2:
            return ConsultationEngine._generate_ai_response(
                user_id, user_text, chart, domain, language, script, state_blob
            )

        try:
            planet = domain_data.get("planet", "Saturn")
            house = domain_data.get("house", 10)
            strength = domain_data.get("strength", "neutral")
            
            guidance = ConsultationEngine._translate_to_life_guidance(
                domain, planet, house, strength, language
            )
            
            response_text = (
                f"Observation: {guidance['observation']}\n"
                f"Cause: {guidance['cause']}\n"
                f"Action: 1. {guidance['action'][0]} 2. {guidance['action'][1]}\n"
                f"Timeframe: {guidance['timeframe']}."
            )
            return {"text": response_text, "state_blob": state_blob}

        except Exception as e:
            logger.error(f"Template failed: {e}")
            return ConsultationEngine._generate_ai_response(
                user_id, user_text, chart, domain, language, script, state_blob
            )

    @staticmethod
    def _generate_ai_response(user_id, user_text, chart, domain, language, script, state_blob):
        try:
            history = MemoryEngine.get_context(user_id) if user_id else []

            system_prompt = (
                f"You are Trishivara, a traditional Vedic Jyotishi sitting in a temple. "
                f"Respond EXACTLY like a real kundli reading. "
                f"EVERY reply MUST start with 'Aapki kundli ke anusar' or 'Graho ki sthiti se'. "
                f"Use ONLY facts from the Full Chart JSON below. "
                f"NEVER use: agar, if, shayad, ho sakti hai, dhyan dena, possible, maybe, try, should. "
                f"Speak like a real astrologer: direct, authoritative, predictive. "
                f"Keep under 60 words. Speak only in Roman Hindi. "
                f"IMPORTANT: If language is Hindi, ALWAYS use Hindi planet names: "
                f"Venus=Shukra, Saturn=Shani, Jupiter=Guru, Mars=Mangal, Mercury=Budh, "
                f"Sun=Surya, Moon=Chandra, Rahu=Rahu, Ketu=Ketu. "
                f"User domain: {domain}. "
                f"Full Chart JSON: {json.dumps(chart, default=str, ensure_ascii=False)}"
            )

            messages = [{"role": "system", "content": system_prompt}] + history
            ai_reply = ask_ai(messages)

            return {"text": ai_reply, "state_blob": state_blob}

        except Exception as e:
            logger.error(f"AI failed: {e}")
            return {
                "text": "Kripya thodi der baad puchhiye, kundli mein thodi dikkat hui.",
                "state_blob": state_blob
            }