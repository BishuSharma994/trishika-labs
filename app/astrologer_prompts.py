import json


class AstrologerPrompts:

    SYSTEM_BASE = """You are a deterministic Parāśari Vedic astrology analyst.

STRICT RULES:
1) Use ONLY the provided structured numeric data.
2) Do NOT assume planetary placements.
3) Do NOT invent afflictions or yogas.
4) Do NOT recommend gemstones or rituals.
5) Explain ONLY using numeric component values.
"""

    DETERMINISTIC_PROMPT = """
DETERMINISTIC DOMAIN DATA:
{data_json}

USER QUESTION:
"{user_query}"

INSTRUCTIONS:
- Explain how each numeric component contributes to the final score.
- Explain why the driver planet dominates.
- Explain why the risk factor weakens.
- Explain how dasha_activation affects momentum.
- Do NOT introduce new astrology variables.
"""

    @staticmethod
    def build_deterministic_prompt(user_query, structured_data):

        return (
            AstrologerPrompts.SYSTEM_BASE
            + "\n"
            + AstrologerPrompts.DETERMINISTIC_PROMPT.format(
                user_query=user_query,
                data_json=json.dumps(structured_data, indent=2),
            )
        )