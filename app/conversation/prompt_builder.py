import json


class PromptBuilder:

    SYSTEM_ASTROLOGER = """
You are a thoughtful Vedic astrologer speaking directly to a client.

Behavior rules:
- Sound natural, calm, and human.
- Do NOT mention scores, engines, data structures, or JSON.
- Translate planetary influence into real-life guidance.
- Avoid excessive technical jargon.
- If the user writes in Hindi, reply in Hindi.
- If the user writes in English, reply in English.
- Be concise but meaningful (4–7 sentences).
"""

    DOMAIN_TEMPLATE = """
Client question:
{question}

Astrology signals for the domain:
{signals}

Task:
Explain what these planetary influences mean for the client's life right now.
Focus on practical implications and decisions.
"""

    GENERAL_TEMPLATE = """
Client question:
{question}

Birth chart summary:
{chart}

Task:
Answer like a professional astrologer in a conversational way.
Give insight rather than technical explanation.
"""

    FUTURE_TEMPLATE = """
Client question:
{question}

Chart context:
{chart}

Task:
Provide a short outlook about the near future based on planetary trends.
Keep it practical and grounded.
"""

    # --------------------------------------------------
    # DOMAIN PROMPT
    # --------------------------------------------------

    @staticmethod
    def build_domain_prompt(domain, domain_data, language):

        signals = {
            "domain": domain,
            "primary_influence": domain_data.get("primary_driver"),
            "risk_factor": domain_data.get("risk_factor"),
            "momentum": domain_data.get("momentum")
        }

        prompt = (
            PromptBuilder.SYSTEM_ASTROLOGER
            + "\n"
            + PromptBuilder.DOMAIN_TEMPLATE.format(
                question=f"The client is asking about {domain}.",
                signals=json.dumps(signals, indent=2)
            )
        )

        if language == "hi":
            prompt += "\nRespond in Hindi."

        return prompt

    # --------------------------------------------------
    # GENERAL CHAT PROMPT
    # --------------------------------------------------

    @staticmethod
    def build_general_prompt(chart_data, question, language):

        summary = {
            "lagna": chart_data.get("lagna"),
            "moon_sign": chart_data.get("moon_sign"),
            "dominant_planet": chart_data.get("deterministic_summary", {}).get("strongest_planet")
        }

        prompt = (
            PromptBuilder.SYSTEM_ASTROLOGER
            + "\n"
            + PromptBuilder.GENERAL_TEMPLATE.format(
                question=question,
                chart=json.dumps(summary, indent=2)
            )
        )

        if language == "hi":
            prompt += "\nRespond in Hindi."

        return prompt

    # --------------------------------------------------
    # FUTURE OUTLOOK PROMPT
    # --------------------------------------------------

    @staticmethod
    def build_future_prompt(chart_data, question, language):

        dasha = chart_data.get("current_dasha", {})

        future_context = {
            "mahadasha": dasha.get("mahadasha"),
            "antardasha": dasha.get("antardasha"),
            "activated_houses": chart_data.get("activated_houses")
        }

        prompt = (
            PromptBuilder.SYSTEM_ASTROLOGER
            + "\n"
            + PromptBuilder.FUTURE_TEMPLATE.format(
                question=question,
                chart=json.dumps(future_context, indent=2)
            )
        )

        if language == "hi":
            prompt += "\nRespond in Hindi."

        return prompt