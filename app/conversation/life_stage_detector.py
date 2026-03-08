class LifeStageDetector:

    CHILDHOOD_PHASE = "childhood_phase"
    EARLY_ADULTHOOD = "early_adulthood"
    CAREER_BUILDING = "career_building"
    CAREER_EXPANSION = "career_expansion"
    LEADERSHIP_PHASE = "leadership_phase"
    LEGACY_PHASE = "legacy_phase"

    @staticmethod
    def detect(age):
        if age is None:
            return None

        if age <= 18:
            return LifeStageDetector.CHILDHOOD_PHASE
        if age <= 25:
            return LifeStageDetector.EARLY_ADULTHOOD
        if age <= 35:
            return LifeStageDetector.CAREER_BUILDING
        if age <= 40:
            return LifeStageDetector.CAREER_EXPANSION
        if age <= 55:
            return LifeStageDetector.LEADERSHIP_PHASE

        return LifeStageDetector.LEGACY_PHASE
