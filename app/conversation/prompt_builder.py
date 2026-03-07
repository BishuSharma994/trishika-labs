import json
from app.conversation.memory_engine import MemoryEngine


class AstrologerPrompts:

    SYSTEM_CONTEXT = """
You are a thoughtful Vedic astrologer speaking directly to a client.

Rules:
- Speak like a real human astrologer.
- Do not mention technical structures.
- Do not mention scores or engines.
- Explain planetary influence naturally.
- Be conversational.
"""

    @staticmethod
    def build_domain_prompt(domain, domain_data, language, user_id, question):

        context = MemoryEngine.build_context(user_id)

        signals = {
            "domain": domain,
            "primary_driver": domain_data.get("primary_driver"),
            "risk_factor": domain_data.get("risk_factor"),
            "momentum": domain_data.get("momentum")
        }

        prompt = f"""
{AstrologerPrompts.SYSTEM_CONTEXT}

Conversation so far:
{context}

User question:
{question}

Astrology signals:
{json.dumps(signals, indent=2)}

Explain what this means for the user in real life.
"""

        if language == "hi":
            prompt += "\nRespond in Hindi."

        return prompt

    @staticmethod
    def build_general_prompt(chart_data, question, language, user_id):

        context = MemoryEngine.build_context(user_id)

        chart_summary = {
            "lagna": chart_data.get("lagna"),
            "moon_sign": chart_data.get("moon_sign"),
            "current_dasha": chart_data.get("current_dasha")
        }

        prompt = f"""
{AstrologerPrompts.SYSTEM_CONTEXT}

Conversation so far:
{context}

User question:
{question}

Birth chart summary:
{json.dumps(chart_summary, indent=2)}

Answer conversationally.
"""

        if language == "hi":
            prompt += "\nRespond in Hindi."

        return prompt