class PromptBuilder:

    @staticmethod
    def domain_prompt(domain_data, language):

        driver = domain_data["primary_driver"]
        risk = domain_data["risk_factor"]
        momentum = domain_data["momentum"]

        if language == "hi":

            return (
                f"Aapke jeevan ke iss shetra par {driver} ka prabhav hai. "
                f"Is samay momentum {momentum} hai. "
                f"{risk} kuch challenges la sakta hai. "
                "Iska matlab hai ki aapko dhyaan se decisions lene honge."
            )

        else:

            return (
                f"This area of your life is currently influenced by {driver}. "
                f"The momentum is {momentum}. "
                f"{risk} may introduce certain challenges, "
                "so decisions should be made carefully."
            )