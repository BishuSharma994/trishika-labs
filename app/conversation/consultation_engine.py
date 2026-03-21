"""
ConsultationEngine - Deterministic Rule-Based Vedic Astrology Interpreter

This module provides deterministic chart-driven interpretations for:
- Career (10th house, D10, Saturn/Jupiter, current dasha, career_window_active)
- Marriage (7th house, Venus, D9, current dasha, marriage_window_active)
- Finance (2nd/11th house, Venus/Mercury, current dasha, ashtakavarga)
- Health (6th/8th/12th house, Mars/Saturn, current dasha, transit stress)

Each response includes:
- observation: What the chart shows
- cause: Why this is happening (chart-based reasoning)
- timeframe: When (based on dasha/transit)
- risk: Potential challenges
- action: What to do

Confidence handling:
- High: dasha + natal strength + transit align
- Medium: two signals align  
- Low: only one signal exists
"""

import json
import logging
from datetime import datetime

from app.conversation.intent_router import IntentRouter
from app.conversation.language_engine import LanguageEngine
from app.conversation.memory_engine import MemoryEngine
from app.conversation.persona_layer import PersonaLayer
from app.ai import ask_ai

logger = logging.getLogger(__name__)

# Planet name translations
PLANET_NAMES = {
    "Sun": {"en": "Sun", "hi": "Surya"},
    "Moon": {"en": "Moon", "hi": "Chandra"},
    "Mars": {"en": "Mars", "hi": "Mangal"},
    "Mercury": {"en": "Mercury", "hi": "Budh"},
    "Jupiter": {"en": "Jupiter", "hi": "Guru"},
    "Venus": {"en": "Venus", "hi": "Shukra"},
    "Saturn": {"en": "Saturn", "hi": "Shani"},
    "Rahu": {"en": "Rahu", "hi": "Rahu"},
    "Ketu": {"en": "Ketu", "hi": "Ketu"},
}

# House lords
HOUSE_LORDS = {
    1: "Sun", 2: "Moon", 3: "Mars", 4: "Mercury", 5: "Jupiter",
    6: "Venus", 7: "Saturn", 8: "Rahu", 9: "Ketu", 10: "Sun",
    11: "Moon", 12: "Mars"
}

# Sign names
SIGN_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

HINDI_SIGN_NAMES = [
    "Mesh", "Vrishabha", "Mithun", "Kark", "Simha", "Kanya",
    "Tula", "Vrishchik", "Dhanu", "Makar", "Kumbha", "Meen"
]


class ConsultationEngine:
    """Deterministic rule-based Vedic astrology interpreter."""

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

    # =========================================================
    # CONFIDENCE CALCULATION
    # =========================================================
    
    @staticmethod
    def _calculate_confidence(chart, domain, domain_data):
        """
        Calculate confidence based on signal alignment:
        - High (3): dasha + natal strength + transit align
        - Medium (2): two signals align
        - Low (1): only one signal exists
        """
        signals = []
        
        # Signal 1: Current dasha relevant to domain
        current_dasha = chart.get("current_dasha", {})
        md = current_dasha.get("mahadasha")
        
        domain_dasha_map = {
            "career": ["Sun", "Saturn", "Jupiter", "Mars"],
            "marriage": ["Venus", "Jupiter", "Ketu"],
            "finance": ["Venus", "Jupiter", "Mercury", "Moon"],
            "health": ["Mars", "Saturn", "Rahu", "Sun"]
        }
        
        if md in domain_dasha_map.get(domain, []):
            signals.append("dasha")
        
        # Signal 2: Domain score and momentum
        if domain_data:
            score = domain_data.get("score", 0)
            momentum = domain_data.get("momentum", "Neutral")
            if momentum == "Positive" or score > 65:
                signals.append("natal_strength")
            elif score > 50:
                signals.append("natal_strength")
        
        # Signal 3: Window activation
        if domain == "career" and chart.get("career_window_active"):
            signals.append("window")
        elif domain == "marriage" and chart.get("marriage_window_active"):
            signals.append("window")
        
        # Signal 4: Activated houses relevant to domain
        activated = chart.get("activated_houses", [])
        domain_houses = {
            "career": [10, 6],
            "marriage": [7, 5, 2],
            "finance": [2, 11, 5],
            "health": [1, 6, 8, 12]
        }
        
        relevant_houses = domain_houses.get(domain, [])
        if any(h in activated for h in relevant_houses):
            signals.append("house_activation")
        
        # Calculate confidence level
        signal_count = len(signals)
        if signal_count >= 3:
            return "high", signals
        elif signal_count >= 2:
            return "medium", signals
        else:
            return "low", signals

    # =========================================================
    # CHART FACT EXTRACTION
    # =========================================================
    
    @staticmethod
    def _get_planet_name(planet, language):
        """Get localized planet name."""
        # Handle Unknown - don't expose to user
        if planet == "Unknown":
            return ""  # Return empty string for unknown planets
        if language == "hi":
            return PLANET_NAMES.get(planet, {}).get("hi", planet)
        return PLANET_NAMES.get(planet, {}).get("en", planet)
    
    @staticmethod
    def _get_planet_strength(chart, planet):
        """Get planet's shadbala strength."""
        shadbala = chart.get("shadbala", {})
        planet_data = shadbala.get(planet, {})
        return planet_data.get("total", 0)
    
    @staticmethod
    def _get_house_lord(chart, house):
        """Get the lord of a house."""
        houses = chart.get("planetary_houses", {})
        return houses.get(house, {}).get("lord", HOUSE_LORDS.get(house, "Unknown"))
    
    @staticmethod
    def _get_planet_dignity(chart, planet):
        """Get planet's dignity status."""
        dignity = chart.get("dignity", {})
        return dignity.get(planet, "neutral")
    
    @staticmethod
    def _is_planet_in_own_sign(chart, planet):
        """Check if planet is in own sign."""
        dignity = chart.get("dignity", {})
        return dignity.get(planet, {}).get("own_sign", False)
    
    @staticmethod
    def _is_planet_exalted(chart, planet):
        """Check if planet is exalted."""
        dignity = chart.get("dignity", {})
        return dignity.get(planet, {}).get("exalted", False)

    # =========================================================
    # CAREER INTERPRETATION
    # =========================================================
    
    @staticmethod
    def _interpret_career(chart, domain_data, language):
        """Generate deterministic career interpretation."""
        
        # Get current dasha
        current_dasha = chart.get("current_dasha", {})
        md = current_dasha.get("mahadasha", "Unknown")
        ad = current_dasha.get("antardasha", "Unknown")
        
        # Get domain score info
        score = domain_data.get("score", 50)
        momentum = domain_data.get("momentum", "Neutral")
        primary_driver = domain_data.get("primary_driver", "Unknown")
        
        # Get career-related houses
        house_10_lord = ConsultationEngine._get_planet_name(
            ConsultationEngine._get_house_lord(chart, 10), language
        )
        house_6_lord = ConsultationEngine._get_house_lord(chart, 6)
        
        # Get planet strengths
        saturn_strength = ConsultationEngine._get_planet_strength(chart, "Saturn")
        jupiter_strength = ConsultationEngine._get_planet_strength(chart, "Jupiter")
        mars_strength = ConsultationEngine._get_planet_strength(chart, "Mars")
        
        # Get dignity
        saturn_dignity = ConsultationEngine._get_planet_dignity(chart, "Saturn")
        jupiter_dignity = ConsultationEngine._get_planet_dignity(chart, "Jupiter")
        
        career_window = chart.get("career_window_active", False)
        
        # Build observation based on chart facts
        observations = []
        
        # Dasha-based observation
        if md == "Saturn":
            if language == "hi":
                observations.append(f"Shani Mahadasha chal raha hai - yeh career stability ka samay hai.")
            else:
                observations.append(f"Saturn Mahadasha is active - this is a period for career stability.")
        elif md == "Jupiter":
            if language == "hi":
                observations.append(f"Guru Mahadasha chal raha hai - growth aur promotion ke yog hain.")
            else:
                observations.append(f"Jupiter Mahadasha is active - growth and promotion are indicated.")
        elif md == "Mars":
            if language == "hi":
                observations.append(f"Mangal Mahadasha chal raha hai - energy aur action ka samay hai.")
            else:
                observations.append(f"Mars Mahadasha is active - this is a time for energy and action.")
        elif md == "Sun":
            if language == "hi":
                observations.append(f"Surya Mahadasha chal raha hai - leadership aur authority ke yog hain.")
            else:
                observations.append(f"Sun Mahadasha is active - leadership and authority are indicated.")
        
        # House 10 (career) analysis
        if score >= 70:
            if language == "hi":
                observations.append(f"10th house strong hai - career achi situation mein hai.")
            else:
                observations.append(f"10th house is strong - career is in a good position.")
        elif score >= 50:
            if language == "hi":
                observations.append(f"10th house moderate hai - career steady hai par improvement possible hai.")
            else:
                observations.append(f"10th house is moderate - career is steady with room for improvement.")
        else:
            if language == "hi":
                observations.append(f"10th house challenging hai - career effort zyada chahiye.")
            else:
                observations.append(f"10th house shows challenges - extra effort needed in career.")
        
        # Primary driver analysis
        if primary_driver != "Unknown":
            driver_name = ConsultationEngine._get_planet_name(primary_driver, language)
            if language == "hi":
                observations.append(f"Primary driver: {driver_name} hai jo career ko influence kar raha hai.")
            else:
                observations.append(f"Primary driver: {driver_name} is influencing your career.")
        
        # Build cause based on chart
        causes = []
        
        if saturn_strength > 200:
            causes.append("Saturn strong hai - discipline aur patience required hai." if language == "hi" 
                         else "Saturn is strong - discipline and patience are required.")
        elif saturn_strength < 100:
            causes.append("Saturn weak hai - delayed results expect kar sakte hain." if language == "hi"
                         else "Saturn is weak - expect delayed results.")
        
        if jupiter_strength > 200:
            causes.append("Guru strong hai - growth opportunities available hain." if language == "hi"
                         else "Jupiter is strong - growth opportunities are available.")
        
        # Dignity checks
        if saturn_dignity in ["own_sign", "exalted"]:
            causes.append(f"{'Shani apne ghar mein hai' if language == 'hi' else 'Saturn is in own sign'} - stable career growth.")
        elif saturn_dignity in ["debilitated", "enemy_sign"]:
            causes.append(f"{'Shani weak position mein hai' if language == 'hi' else 'Saturn is in weak position'} - challenges in career.")
        
        # Timeframe based on dasha
        timeframes = []
        
        if ad == "Saturn":
            timeframes.append("4-6 mahine" if language == "hi" else "4-6 months")
        elif ad == "Jupiter":
            timeframes.append("2-3 mahine" if language == "hi" else "2-3 months")
        elif ad == "Mars":
            timeframes.append("2-3 hafte" if language == "hi" else "2-3 weeks")
        elif ad == "Mercury":
            timeframes.append("1-2 hafte" if language == "hi" else "1-2 weeks")
        elif ad == "Venus":
            timeframes.append("3-4 hafte" if language == "hi" else "3-4 weeks")
        else:
            timeframes.append("1-2 mahine" if language == "hi" else "1-2 months")
        
        # Risk assessment
        risks = []
        
        if 6 in chart.get("activated_houses", []):
            risks.append("6th house active hai - competition ya rivals ka saamna kar sakte hain." if language == "hi"
                        else "6th house is active - may face competition or rivals.")
        
        if chart.get("transit"):
            transit = chart.get("transit", {})
            saturn_transit = transit.get("Saturn", {})
            if saturn_transit.get("sign") in ["Capricorn", "Aquarius", "Libra"]:
                risks.append("Shani transit challenging hai - patience zaroori hai." if language == "hi"
                            else "Saturn transit is challenging - patience is essential.")
        
        # Actions based on chart
        actions = []
        
        if md == "Saturn":
            actions.append("Mehnat aur patience jare rakhein." if language == "hi"
                         else "Continue with hard work and patience.")
        elif md == "Jupiter":
            actions.append("Naye opportunities explore karein." if language == "hi"
                         else "Explore new opportunities.")
        elif md == "Mars":
            actions.append("Proactive steps lein, hesitant nahein." if language == "hi"
                         else "Take proactive steps, don't hesitate.")
        
        if score < 60:
            actions.append("Skills improve karein - online courses ya certifications lein." if language == "hi"
                         else "Improve skills - take online courses or certifications.")
        
        if career_window:
            actions.append("Career window active hai - important decisions le sakte hain." if language == "hi"
                         else "Career window is active - can make important decisions.")
        
        # Format final response
        obs_text = " | ".join(observations)
        cause_text = " | ".join(causes) if causes else ("Chart analysis ke hisab se." if language == "hi" else "Based on chart analysis.")
        time_text = ", ".join(timeframes)
        risk_text = ", ".join(risks) if risks else ("Specific risk nahi dikh raha." if language == "hi" else "No specific risk indicated.")
        action_text = " | ".join(actions[:3])  # Max 3 actions
        
        return {
            "observation": obs_text,
            "cause": cause_text,
            "timeframe": time_text,
            "risk": risk_text,
            "action": action_text
        }

    # =========================================================
    # MARRIAGE INTERPRETATION
    # =========================================================
    
    @staticmethod
    def _interpret_marriage(chart, domain_data, language):
        """Generate deterministic marriage interpretation."""
        
        current_dasha = chart.get("current_dasha", {})
        md = current_dasha.get("mahadasha", "Unknown")
        ad = current_dasha.get("antardasha", "Unknown")
        
        score = domain_data.get("score", 50)
        momentum = domain_data.get("momentum", "Neutral")
        primary_driver = domain_data.get("primary_driver", "Unknown")
        
        marriage_window = chart.get("marriage_window_active", False)
        
        # Get planet strengths
        venus_strength = ConsultationEngine._get_planet_strength(chart, "Venus")
        jupiter_strength = ConsultationEngine._get_planet_strength(chart, "Jupiter")
        moon_strength = ConsultationEngine._get_planet_strength(chart, "Moon")
        
        venus_dignity = ConsultationEngine._get_planet_dignity(chart, "Venus")
        
        observations = []
        
        # Dasha analysis
        if md == "Venus":
            observations.append("Shukra Mahadasha chal raha hai - marriage/relationship ke favorable samay." if language == "hi"
                              else "Venus Mahadasha is active - favorable time for marriage/relationship.")
        elif md == "Jupiter":
            observations.append("Guru Mahadasha chal raha hai - spouse ya partner ke through growth." if language == "hi"
                              else "Jupiter Mahadasha is active - growth through spouse or partner.")
        elif md == "Ketu":
            observations.append("Ketu Mahadasha chal raha hai - spiritual growth par focus." if language == "hi"
                              else "Ketu Mahadasha is active - focus on spiritual growth.")
        
        # 7th house analysis
        if score >= 70:
            observations.append("7th house strong hai - relationship favorable situation mein." if language == "hi"
                              else "7th house is strong - relationship is in favorable position.")
        elif score >= 50:
            observations.append("7th house moderate hai - steady relationship with growth potential." if language == "hi"
                              else "7th house is moderate - steady relationship with growth potential.")
        else:
            observations.append("7th house challenging hai - relationship mein effort zaroori." if language == "hi"
                              else "7th house shows challenges - extra effort needed in relationship.")
        
        # Venus analysis
        venus_name = ConsultationEngine._get_planet_name("Venus", language)
        if venus_strength > 200:
            observations.append(f"{venus_name} strong hai - relationship happiness ke liye favorable." if language == "hi"
                              else f"{venus_name} is strong - favorable for relationship happiness.")
        elif venus_strength < 100:
            observations.append(f"{venus_name} weak hai - relationship challenges ho sakte hain." if language == "hi"
                              else f"{venus_name} is weak - may face relationship challenges.")
        
        if venus_dignity in ["own_sign", "exalted"]:
            observations.append(f"{venus_name} apne ghar mein hai - relationship stability." if language == "hi"
                              else f"{venus_name} is in own sign - relationship stability.")
        
        causes = []
        
        if moon_strength > 200:
            causes.append("Chandra strong hai - emotional compatibility strong hai." if language == "hi"
                         else "Moon is strong - emotional compatibility is strong.")
        
        if jupiter_strength > 200:
            causes.append("Guru se blessing mil rahi hai - marriage ke liye positive." if language == "hi"
                         else "Jupiter's blessing is present - positive for marriage.")
        
        # Timeframe
        timeframes = []
        
        if ad == "Venus":
            timeframes.append("3-4 mahine" if language == "hi" else "3-4 months")
        elif ad == "Jupiter":
            timeframes.append("6-8 mahine" if language == "hi" else "6-8 months")
        elif ad == "Ketu":
            timeframes.append("Anishchit - is samay spiritual focus better hai." if language == "hi"
                             else "Uncertain - better to focus on spiritual growth now.")
        else:
            timeframes.append("2-3 mahine" if language == "hi" else "2-3 months")
        
        # Risk
        risks = []
        
        if 7 in chart.get("activated_houses", []) and 6 in chart.get("activated_houses", []):
            risks.append("7th aur 6th both active hain - relationship challenges ho sakte hain." if language == "hi"
                       else "Both 7th and 6th are active - may face relationship challenges.")
        
        # Action
        actions = []
        
        if marriage_window:
            actions.append("Marriage window active hai - important decisions le sakte hain." if language == "hi"
                         else "Marriage window is active - can make important decisions.")
        
        if md == "Venus":
            actions.append("Relationship building activities focus karein." if language == "hi"
                         else "Focus on relationship building activities.")
        elif md == "Ketu":
            actions.append("Self-reflection aur spiritual practices helpful honge." if language == "hi"
                         else "Self-reflection and spiritual practices will be helpful.")
        
        obs_text = " | ".join(observations)
        cause_text = " | ".join(causes) if causes else ("Chart analysis ke hisab se." if language == "hi" else "Based on chart analysis.")
        time_text = ", ".join(timeframes)
        risk_text = ", ".join(risks) if risks else ("Specific risk nahi dikh raha." if language == "hi" else "No specific risk indicated.")
        action_text = " | ".join(actions[:3])
        
        return {
            "observation": obs_text,
            "cause": cause_text,
            "timeframe": time_text,
            "risk": risk_text,
            "action": action_text
        }

    # =========================================================
    # FOLLOW-UP RESPONSE (Shorter, continuation style)
    # =========================================================
    
    @staticmethod
    def _generate_followup_response(user_id, user_text, domain, language, chart, state_blob):
        """
        Generate a shorter follow-up response for clarification/elaboration requests.
        Does not repeat the full reading - just provides continuation.
        """
        # Generate elaboration prompts based on domain
        elaborations = {
            "finance": {
                "hi": [
                    "Finance ke baare mein aur details: Mahadasha ke dauran aapko investitions par focus karna chahiye. Long-term planning madad karegi.",
                    "Aapke finance indicators strong hain. Regular savings aur careful spending se behtar hoga.",
                ],
                "en": [
                    "More on your finances: During this mahadasha, focus on investments. Long-term planning will help.",
                    "Your finance indicators are strong. Regular savings and careful spending will improve things.",
                ]
            },
            "career": {
                "hi": [
                    "Career ke baare mein: Saturn ki strength good hai. Patience rakhna hoga, results aayenge.",
                    "Aapka career mansik roop se strong hai. Niche se upar aana fixed goals se hoga.",
                ],
                "en": [
                    "More on career: Saturn's strength is good. Have patience, results will come.",
                    "Your career is mentally strong. Moving up will happen through fixed goals.",
                ]
            },
            "health": {
                "hi": [
                    "Health ke baare mein: Daily routine consistent rakhna zaroori hai. Exercise aur diet balance maintain karein.",
                    "Aapki health indicators decent hain. Regular checkups aur preventive care helpful hoga.",
                ],
                "en": [
                    "More on health: Keep daily routine consistent. Maintain exercise and diet balance.",
                    "Your health indicators are decent. Regular checkups and preventive care will help.",
                ]
            },
            "marriage": {
                "hi": [
                    "Marriage ke baare mein: Relationship mein communication key hai. Patience aur understanding zaroori hai.",
                    "Aapke marriage indicators stable hain. Mutual respect aur trust important hai.",
                ],
                "en": [
                    "More on marriage: Communication is key in relationships. Patience and understanding are important.",
                    "Your marriage indicators are stable. Mutual respect and trust are important.",
                ]
            }
        }
        
        import random
        domain_key = domain or "finance"
        options = elaborations.get(domain_key, elaborations["finance"])
        response_text = random.choice(options.get(language, options["en"]))
        
        return {"text": response_text, "state_blob": state_blob}

    # =========================================================
    # FINANCE INTERPRETATION
    # =========================================================
    
    @staticmethod
    def _interpret_finance(chart, domain_data, language):
        """Generate deterministic finance interpretation."""
        
        current_dasha = chart.get("current_dasha", {})
        md = current_dasha.get("mahadasha", "Unknown")
        ad = current_dasha.get("antardasha", "Unknown")
        
        score = domain_data.get("score", 50)
        momentum = domain_data.get("momentum", "Neutral")
        primary_driver = domain_data.get("primary_driver", "Unknown")
        
        # Get planet strengths
        venus_strength = ConsultationEngine._get_planet_strength(chart, "Venus")
        jupiter_strength = ConsultationEngine._get_planet_strength(chart, "Jupiter")
        mercury_strength = ConsultationEngine._get_planet_strength(chart, "Mercury")
        moon_strength = ConsultationEngine._get_planet_strength(chart, "Moon")
        
        venus_dignity = ConsultationEngine._get_planet_dignity(chart, "Venus")
        
        observations = []
        
        # Dasha analysis - only include if we have valid mahadasha
        md_name = ConsultationEngine._get_planet_name(md, language)
        if md_name:  # Only add if we have a valid mahadasha name
            observations.append(f"{md_name} Mahadasha chal raha hai - financial situation is affected." if language == "hi"
                              else f"{md_name} Mahadasha is active - financial situation is affected.")
        
        # Finance house analysis (2nd and 11th)
        if score >= 70:
            observations.append("Finance houses strong hain - financial situation achi hai." if language == "hi"
                              else "Finance houses are strong - financial situation is good.")
        elif score >= 50:
            observations.append("Finance houses moderate hain - steady finances with growth potential." if language == "hi"
                              else "Finance houses are moderate - steady finances with growth potential.")
        else:
            observations.append("Finance houses challenging hain - financial management zaroori." if language == "hi"
                              else "Finance houses show challenges - financial management is essential.")
        
        # Primary driver
        if primary_driver != "Unknown":
            driver_name = ConsultationEngine._get_planet_name(primary_driver, language)
            observations.append(f"Primary driver: {driver_name} financial matters ko influence kar raha hai." if language == "hi"
                              else f"Primary driver: {driver_name} is influencing financial matters.")
        
        causes = []
        
        if venus_strength > 200:
            causes.append("Shukra strong hai - financial gains aur comfort available hain." if language == "hi"
                         else "Venus is strong - financial gains and comfort are available.")
        
        if jupiter_strength > 200:
            causes.append("Guru strong hai - wealth aur prosperity blessings available hain." if language == "hi"
                         else "Jupiter is strong - wealth and prosperity blessings are available.")
        
        if venus_dignity in ["own_sign", "exalted"]:
            causes.append("Shukra apne ghar mein hai - financial stability." if language == "hi"
                         else "Venus is in own sign - financial stability.")
        
        # Timeframe
        timeframes = []
        
        if ad == "Venus":
            timeframes.append("3-4 mahine" if language == "hi" else "3-4 months")
        elif ad == "Jupiter":
            timeframes.append("6-8 mahine" if language == "hi" else "6-8 months")
        elif ad == "Mercury":
            timeframes.append("1-2 mahine" if language == "hi" else "1-2 months")
        else:
            timeframes.append("2-3 mahine" if language == "hi" else "2-3 months")
        
        # Risk
        risks = []
        
        if 12 in chart.get("activated_houses", []):
            risks.append("12th house active hai - expenses ya losses ho sakte hain." if language == "hi"
                       else "12th house is active - may face expenses or losses.")
        
        # Action
        actions = []
        
        if md == "Venus":
            actions.append("Investments aur wealth creation focus karein." if language == "hi"
                         else "Focus on investments and wealth creation.")
        elif md == "Jupiter":
            actions.append("Long-term financial planning shuru karein." if language == "hi"
                         else "Start long-term financial planning.")
        
        if score < 60:
            actions.append("Budget management improve karein aur unnecessary expenses kam karein." if language == "hi"
                         else "Improve budget management and reduce unnecessary expenses.")
        
        obs_text = " | ".join(observations)
        cause_text = " | ".join(causes) if causes else ("Chart analysis ke hisab se." if language == "hi" else "Based on chart analysis.")
        time_text = ", ".join(timeframes)
        risk_text = ", ".join(risks) if risks else ("Specific risk nahi dikh raha." if language == "hi" else "No specific risk indicated.")
        action_text = " | ".join(actions[:3])
        
        return {
            "observation": obs_text,
            "cause": cause_text,
            "timeframe": time_text,
            "risk": risk_text,
            "action": action_text
        }

    # =========================================================
    # HEALTH INTERPRETATION
    # =========================================================
    
    @staticmethod
    def _interpret_health(chart, domain_data, language):
        """Generate deterministic health interpretation."""
        
        current_dasha = chart.get("current_dasha", {})
        md = current_dasha.get("mahadasha", "Unknown")
        ad = current_dasha.get("antardasha", "Unknown")
        
        score = domain_data.get("score", 50)
        momentum = domain_data.get("momentum", "Neutral")
        primary_driver = domain_data.get("primary_driver", "Unknown")
        
        # Get planet strengths
        mars_strength = ConsultationEngine._get_planet_strength(chart, "Mars")
        saturn_strength = ConsultationEngine._get_planet_strength(chart, "Saturn")
        sun_strength = ConsultationEngine._get_planet_strength(chart, "Sun")
        
        mars_dignity = ConsultationEngine._get_planet_dignity(chart, "Mars")
        
        observations = []
        
        # Dasha analysis
        if md == "Mars":
            observations.append("Mangal Mahadasha chal raha hai - energy high hai, accidents ka risk." if language == "hi"
                              else "Mars Mahadasha is active - high energy, risk of accidents.")
        elif md == "Saturn":
            observations.append("Shani Mahadasha chal raha hai - chronic health issues ka dhyan rakhein." if language == "hi"
                              else "Saturn Mahadasha is active - pay attention to chronic health issues.")
        elif md == "Rahu":
            observations.append("Rahu Mahadasha chal raha hai - unexpected health challenges ho sakte hain." if language == "hi"
                              else "Rahu Mahadasha is active - unexpected health challenges may arise.")
        
        # Health house analysis
        if score >= 70:
            observations.append("Health strong hai - body抵抗力 achi hai." if language == "hi"
                              else "Health is strong - body resistance is good.")
        elif score >= 50:
            observations.append("Health moderate hai - maintain karein, precautions lein." if language == "hi"
                              else "Health is moderate - maintain and take precautions.")
        else:
            observations.append("Health careful hai - doctor se regular checkup zaroori." if language == "hi"
                              else "Health needs care - regular doctor checkup is essential.")
        
        # Planet analysis
        if mars_strength > 200 and mars_dignity in ["own_sign", "exalted"]:
            observations.append("Mangal strong hai - physical energy good hai." if language == "hi"
                              else "Mars is strong - physical energy is good.")
        elif mars_strength < 100:
            observations.append("Mangal weak hai - injuries ka risk." if language == "hi"
                              else "Mars is weak - risk of injuries.")
        
        if saturn_strength > 200:
            observations.append("Shani strong hai - bones aur joints ka dhyan rakhein." if language == "hi"
                              else "Saturn is strong - pay attention to bones and joints.")
        
        causes = []
        
        if 6 in chart.get("activated_houses", []):
            causes.append("6th house active hai - diseases ka risk increased." if language == "hi"
                         else "6th house is active - disease risk is increased.")
        
        if 8 in chart.get("activated_houses", []):
            causes.append("8th house active hai - transformative health changes possible." if language == "hi"
                         else "8th house is active - transformative health changes possible.")
        
        if 12 in chart.get("activated_houses", []):
            causes.append("12th house active hai - hospital ya isolation ka risk." if language == "hi"
                         else "12th house is active - risk of hospital or isolation.")
        
        # Timeframe
        timeframes = []
        
        if ad == "Mars":
            timeframes.append("2-3 hafte" if language == "hi" else "2-3 weeks")
        elif ad == "Saturn":
            timeframes.append("4-6 mahine" if language == "hi" else "4-6 months")
        elif ad == "Rahu":
            timeframes.append("Anishchit - precautions continue karein." if language == "hi"
                             else "Uncertain - continue precautions.")
        else:
            timeframes.append("1-2 mahine" if language == "hi" else "1-2 months")
        
        # Risk
        risks = []
        
        if md == "Mars":
            risks.append("Accidents ya injuries ka risk - driving mein careful rahein." if language == "hi"
                       else "Risk of accidents or injuries - be careful while driving.")
        
        if md == "Saturn":
            risks.append("Chronic issues flare-up ka risk - regular checkup karein." if language == "hi"
                       else "Risk of chronic issue flare-ups - get regular checkups.")
        
        # Action
        actions = []
        
        if md == "Mars":
            actions.append("Physical exercise balance mein rakhein - overexertion avoid karein." if language == "hi"
                         else "Keep physical exercise in balance - avoid overexertion.")
        elif md == "Saturn":
            actions.append("Consistent routine banayein - diet aur sleep discipline maintain karein." if language == "hi"
                         else "Establish consistent routine - maintain diet and sleep discipline.")
        
        actions.append("Regular health checkups karein - prevention better hai." if language == "hi"
                     else "Get regular health checkups - prevention is better.")
        
        obs_text = " | ".join(observations)
        cause_text = " | ".join(causes) if causes else ("Chart analysis ke hisab se." if language == "hi" else "Based on chart analysis.")
        time_text = ", ".join(timeframes)
        risk_text = ", ".join(risks) if risks else ("Specific risk nahi dikh raha." if language == "hi" else "No specific risk indicated.")
        action_text = " | ".join(actions[:3])
        
        return {
            "observation": obs_text,
            "cause": cause_text,
            "timeframe": time_text,
            "risk": risk_text,
            "action": action_text
        }

    # =========================================================
    # MAIN RESPONSE GENERATOR
    # =========================================================
    
    @staticmethod
    def generate_response(
        domain, domain_data, language, script, stage, age, life_stage,
        user_goal, current_dasha, transits, persona_introduced, chart,
        theme_shown, user_text, session_state_blob, domain_switched,
        normalized_intent, user_id=None, response_type="initial",
    ):
        """
        Generate deterministic chart-driven response.
        
        This is the main entry point. It:
        1. Calculates confidence based on signal alignment
        2. Generates rule-based interpretation from chart facts
        3. Only uses AI for polishing the wording (not for deciding content)
        
        response_type: "initial", "followup", "elaboration", "clarification"
        - initial: Full consultation answer
        - followup/clarification/elaboration: Shorter continuation response
        """
        
        state_blob = ConsultationEngine.dump_state(
            ConsultationEngine.load_state(session_state_blob) or {}
        )
        
        # For follow-up responses, generate shorter continuation
        if response_type in ("followup", "elaboration", "clarification"):
            return ConsultationEngine._generate_followup_response(
                user_id=user_id,
                user_text=user_text,
                domain=domain,
                language=language,
                chart=chart,
                state_blob=state_blob,
            )
        
        if len(user_text) < 2 and not user_text.isalnum():
            return {
                "text": "Aap kya jaanna chahte hain?" if language == "hi" else "What would you like to know?",
                "state_blob": state_blob
            }
        
        # Determine domain
        score_domain = ConsultationEngine.score_domain(domain or "career")
        
        # Ensure domain_data has complete info
        full_domain_data = dict(domain_data or {})
        if chart and score_domain:
            chart_domain_data = chart.get("domain_scores", {}).get(score_domain, {})
            for k, v in chart_domain_data.items():
                if k not in full_domain_data:
                    full_domain_data[k] = v
        
        # Calculate confidence
        confidence, signals = ConsultationEngine._calculate_confidence(chart, score_domain, full_domain_data)
        
        # Generate deterministic interpretation based on domain
        if score_domain == "career":
            interpretation = ConsultationEngine._interpret_career(chart, full_domain_data, language)
        elif score_domain == "marriage":
            interpretation = ConsultationEngine._interpret_marriage(chart, full_domain_data, language)
        elif score_domain == "finance":
            interpretation = ConsultationEngine._interpret_finance(chart, full_domain_data, language)
        elif score_domain == "health":
            interpretation = ConsultationEngine._interpret_health(chart, full_domain_data, language)
        else:
            # Fallback
            interpretation = ConsultationEngine._interpret_career(chart, full_domain_data, language)
        
        # Add confidence to response (internal only, not exposed to user)
        conf_text = ""
        if confidence == "high":
            conf_text = "[HIGH CONFIDENCE] " if language == "en" else "[UCHA VISHVAS] "
        elif confidence == "medium":
            conf_text = "[MEDIUM CONFIDENCE] " if language == "en" else "[MADHYAM VISHVAS] "
        else:
            # For low confidence, do NOT expose to user - provide best available answer
            conf_text = ""
        
        # Format final response (clean format without confidence labels exposed to user)
        response_text = (
            f"Observation: {interpretation['observation']}\n"
            f"Cause: {interpretation['cause']}\n"
            f"Timeframe: {interpretation['timeframe']}\n"
            f"Risk: {interpretation['risk']}\n"
            f"Action: {interpretation['action']}"
        )
        
        # NO low-confidence disclaimer - bot provides best available answer internally
        
        # Try to polish the response using AI
        try:
            polished_response = ConsultationEngine._generate_ai_polished_response(
                user_id=user_id,
                user_text=user_text,
                chart=chart,
                domain=score_domain,
                language=language,
                script=script,
                state_blob=state_blob,
                interpretation=interpretation
            )
            if polished_response and polished_response.get("text"):
                return polished_response
        except Exception as e:
            # If AI polishing fails, fall back to deterministic response
            pass
        
        return {"text": response_text, "state_blob": state_blob}

    # =========================================================
    # AI RESPONSE (Only for wording, not content)
    # =========================================================
    
    @staticmethod
    def _generate_ai_polished_response(user_id, user_text, chart, domain, language, script, state_blob, interpretation):
        """
        Polish the deterministic output using AI.
        
        IMPORTANT: AI is only allowed to REWORD the interpretation, NOT to:
        - Add new astrology facts
        - Change confidence
        - Invent planets/houses/dasha
        - Make up timelines
        - Suggest consulting external experts
        - Mention confidence levels to users
        
        The rule engine already decided the content; AI only polishes.
        """
        
        # Determine output language requirement
        if language == "hi":
            lang_requirement = "You MUST write in Roman Hindi (Latin script, NOT Devanagari). Example: 'Aapka mahadasha chal raha hai'"
            lang_examples = "Roman Hindi examples: 'Shukra strong hai', '2-3 mahino mein behtar hoga'"
        else:
            lang_requirement = "You MUST write in English."
            lang_examples = "English examples: 'Your Venus is strong', 'Things will improve in 2-3 months'"
        
        # Build the system prompt for AI polishing
        system_prompt = (
            f"You are a warm, conversational Vedic astrology consultant. "
            f"Rewrite the following astrological analysis in a natural, conversational tone that sounds like a real person explaining. "
            f"Use simple language that anyone can understand.\n\n"
            f"CRITICAL LANGUAGE RULE: {lang_requirement}\n"
            f"{lang_examples}\n"
            f"DO NOT mix languages. Output must be entirely in {language}.\n\n"
            f"CRITICAL: Never suggest the user consult another astrologer or expert. "
            f"Never mention that chart data is limited or confidence is low. "
            f"The bot provides the best reading possible.\n\n"
            f"User domain: {domain}\n\n"
            f"FACTS (use exactly these, do not add new information):\n"
            f"Observation: {interpretation.get('observation', '')}\n"
            f"Cause: {interpretation.get('cause', '')}\n"
            f"Timeframe: {interpretation.get('timeframe', '')}\n"
            f"Risk: {interpretation.get('risk', '')}\n"
            f"Action: {interpretation.get('action', '')}"
        )
        
        messages = [{"role": "system", "content": system_prompt}]
        polished = ask_ai(messages)
        return {"text": polished, "state_blob": state_blob}
