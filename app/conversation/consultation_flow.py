class ConsultationFlow:

    """
    Controls the narrative structure of the astrology consultation.
    Prevents fragmented answers and ensures a structured reading.
    """

    SESSION_START = "start"
    CHART_OVERVIEW = "overview"
    DOMAIN_DISCUSSION = "domain"
    TIMING_DISCUSSION = "timing"
    FOLLOWUP = "followup"

    @staticmethod
    def detect_stage(session):

        if not getattr(session, "consultation_stage", None):
            return ConsultationFlow.SESSION_START

        return session.consultation_stage

    @staticmethod
    def move_to_overview(user_id, StateManager):

        StateManager.update_session(
            user_id,
            consultation_stage=ConsultationFlow.CHART_OVERVIEW
        )

    @staticmethod
    def move_to_domain(user_id, StateManager):

        StateManager.update_session(
            user_id,
            consultation_stage=ConsultationFlow.DOMAIN_DISCUSSION
        )

    @staticmethod
    def move_to_timing(user_id, StateManager):

        StateManager.update_session(
            user_id,
            consultation_stage=ConsultationFlow.TIMING_DISCUSSION
        )

    @staticmethod
    def move_to_followup(user_id, StateManager):

        StateManager.update_session(
            user_id,
            consultation_stage=ConsultationFlow.FOLLOWUP
        )