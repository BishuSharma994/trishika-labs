class ConsultationController:

    DOMAIN_ENTRY = "DOMAIN_ENTRY"
    STATUS_CAPTURE = "STATUS_CAPTURE"
    DIAGNOSTIC = "DIAGNOSTIC"
    INTERPRETATION = "INTERPRETATION"
    GUIDANCE = "GUIDANCE"
    ACTION_PLAN = "ACTION_PLAN"

    ORDER = [
        DOMAIN_ENTRY,
        STATUS_CAPTURE,
        DIAGNOSTIC,
        INTERPRETATION,
        GUIDANCE,
        ACTION_PLAN,
    ]

    @staticmethod
    def next_stage(stage):

        if stage not in ConsultationController.ORDER:
            return ConsultationController.DOMAIN_ENTRY

        index = ConsultationController.ORDER.index(stage)

        if index + 1 >= len(ConsultationController.ORDER):
            return ConsultationController.ACTION_PLAN

        return ConsultationController.ORDER[index + 1]