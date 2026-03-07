class PromptBuilder:

    # -----------------------------
    # SYSTEM ROLE
    # -----------------------------
    SYSTEM_PROMPT = """
You are a traditional Vedic astrologer speaking to a client.

Rules:
1. Never mention calculations or scores.
2. Interpret signals like a human astrologer.
3. Speak calmly and conversationally.
4. Avoid robotic phrasing.
5. Respond in the user's language.
6. Give practical guidance where appropriate.
"""

    # -----------------------------
    # DOMAIN PROMPT
    # -----------------------------
    @staticmethod
    def build_domain_prompt(domain, domain_data, language):

        driver = domain_data.get("primary_driver")
        risk = domain_data.get("risk_factor")
        momentum = domain_data.get("momentum")

        if language == "hi":

            user_context = f"""
Jeevan ka shetra: {domain}

Graha prabhav:
Primary graha: {driver}
Risk graha: {risk}
Momentum: {momentum}

User ko is shetra ke baare mein samajhna hai.
Unhe friendly aur practical tareeke se samjhao.
"""

        else:

            user_context = f"""
Life domain: {domain}

Planetary influence:
Primary planet: {driver}
Risk planet: {risk}
Momentum: {momentum}

Explain the situation naturally as an astrologer would.
"""

        return PromptBuilder.SYSTEM_PROMPT + "\n" + user_context

    # -----------------------------
    # DECISION PROMPT
    # -----------------------------
    @staticmethod
    def build_decision_prompt(domain, domain_data, language):

        driver = domain_data.get("primary_driver")
        momentum = domain_data.get("momentum")

        if language == "hi":

            return (
                PromptBuilder.SYSTEM_PROMPT
                + f"""
User {domain} ke sambandh mein decision lena chah raha hai.

Planet influence:
{driver}

Momentum:
{momentum}

Unhe samjhao ki kaise decisions aa sakte hain aur kaise sochna chahiye.
"""
            )

        else:

            return (
                PromptBuilder.SYSTEM_PROMPT
                + f"""
The user is considering decisions related to {domain}.

Planet influencing this area:
{driver}

Momentum:
{momentum}

Explain what kind of decisions may arise and how the user should approach them.
"""
            )

    # -----------------------------
    # FUTURE PROJECTION PROMPT
    # -----------------------------
    @staticmethod
    def build_future_prompt(domain, prediction_data, language):

        projection = prediction_data.get("projection_12_months")

        if language == "hi":

            return (
                PromptBuilder.SYSTEM_PROMPT
                + f"""
User {domain} ka bhavishya jaana chahta hai.

Agle 12 mahino ka trend:
{projection}

In trends ko astrologer ki tarah explain karo.
User ko simple bhasha mein samjhao.
"""
            )

        else:

            return (
                PromptBuilder.SYSTEM_PROMPT
                + f"""
The user wants to understand the future of their {domain}.

12 month trend:
{projection}

Explain the upcoming trend like a professional astrologer.
Avoid technical explanations.
"""
            )
