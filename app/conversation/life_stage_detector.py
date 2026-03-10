CHILDHOOD_PHASE = "childhood_phase"
EARLY_ADULTHOOD = "early_adulthood"
CAREER_BUILDING = "career_building"
CAREER_EXPANSION = "career_expansion"
LEADERSHIP_PHASE = "leadership_phase"
LEGACY_PHASE = "legacy_phase"


def detect(age: int) -> str:
    """Map age to consultation life stage."""
    if age is None:
        return CAREER_BUILDING

    if age <= 18:
        return CHILDHOOD_PHASE

    if age <= 25:
        return EARLY_ADULTHOOD

    if age <= 35:
        return CAREER_BUILDING

    if age <= 40:
        return CAREER_EXPANSION

    if age <= 55:
        return LEADERSHIP_PHASE

    return LEGACY_PHASE


class LifeStageDetector:
    CHILDHOOD_PHASE = CHILDHOOD_PHASE
    EARLY_ADULTHOOD = EARLY_ADULTHOOD
    CAREER_BUILDING = CAREER_BUILDING
    CAREER_EXPANSION = CAREER_EXPANSION
    LEADERSHIP_PHASE = LEADERSHIP_PHASE
    LEGACY_PHASE = LEGACY_PHASE

    @staticmethod
    def detect(age: int) -> str:
        return detect(age)
