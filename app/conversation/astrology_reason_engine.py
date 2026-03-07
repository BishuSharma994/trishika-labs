class AstrologyReasonEngine:

    @staticmethod
    def build_reason(domain_data):

        driver = domain_data.get("primary_driver")
        risk = domain_data.get("risk_factor")
        momentum = domain_data.get("momentum")

        reason = []

        if driver:
            reason.append(
                f"The primary planetary influence here is {driver}."
            )

        if risk:
            reason.append(
                f"Some pressure may come from {risk}."
            )

        if momentum:
            reason.append(
                f"The current momentum appears {momentum}."
            )

        return " ".join(reason)