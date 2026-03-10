import json
import re
from typing import Any


class ConsultationEngine:
    DOMAIN_ENTRY = "DOMAIN_ENTRY"
    STATUS_CAPTURE = "STATUS_CAPTURE"
    DIAGNOSTIC = "DIAGNOSTIC"
    INTERPRETATION = "INTERPRETATION"
    GUIDANCE = "GUIDANCE"
    ACTION_PLAN = "ACTION_PLAN"

    # Legacy aliases kept so older callers/session values do not break.
    STAGE_CHART_READING = DOMAIN_ENTRY
    STAGE_SITUATION_ANALYSIS = DIAGNOSTIC
    STAGE_STRATEGY_GUIDANCE = GUIDANCE
    STAGE_ACTION_PLAN = ACTION_PLAN

    _STATE_MARKER = "consultation_state"
    _STATE_VERSION = 2
    _MAX_RESPONSE_WORDS = 160

    _DOMAIN_CONFIG = {
        "career": {
            "display": "career",
            "aliases": ["career", "job", "naukri", "profession", "work", "employment", "business career"],
            "score_domain": "career",
            "signals": {
                "houses": "10th and 6th house",
                "planets": ["Saturn", "Sun", "Mercury"],
                "timing_flag": "career_window_active",
                "default_driver": "Saturn",
                "default_risk": "Mercury",
            },
            "status_prompt": (
                "Before I interpret your career path, I need your current situation first.\n\n"
                "What best describes you right now?\n"
                "1. Employed\n"
                "2. Job searching\n"
                "3. Running a business"
            ),
            "statuses": {
                "employed": {
                    "label": "currently employed",
                    "keywords": ["1", "employed", "job", "working", "office", "service"],
                },
                "job_searching": {
                    "label": "currently job searching",
                    "keywords": ["2", "search", "looking", "unemployed", "job hunt"],
                },
                "business": {
                    "label": "currently running a business",
                    "keywords": ["3", "business", "self employed", "startup", "entrepreneur"],
                },
            },
            "diagnostics": {
                "employed": [
                    {
                        "key": "career_growth",
                        "question": "Do you currently feel growth in your role, or mostly stagnation?",
                        "options": {
                            "growth": ["growth", "improving", "promotion", "good"],
                            "stagnant": ["stagnant", "slow", "stuck", "no growth"],
                            "pressure": ["pressure", "stress", "toxic", "overload"],
                        },
                    },
                    {
                        "key": "role_stability",
                        "question": "Is your manager/work environment supportive, mixed, or unstable?",
                        "options": {
                            "supportive": ["supportive", "good", "stable"],
                            "mixed": ["mixed", "average", "normal"],
                            "unstable": ["unstable", "bad", "conflict", "toxic"],
                        },
                    },
                ],
                "job_searching": [
                    {
                        "key": "search_duration",
                        "question": "How long have you been searching actively?",
                        "options": {
                            "short": ["short", "few weeks", "1 month", "recent"],
                            "medium": ["2 months", "3 months", "few months"],
                            "long": ["long", "6 months", "year", "many months"],
                        },
                    },
                    {
                        "key": "interview_flow",
                        "question": "Are interviews converting to offers, or getting delayed?",
                        "options": {
                            "converting": ["offer", "converting", "positive"],
                            "delayed": ["delayed", "slow", "stuck"],
                            "low_response": ["no response", "low", "rare", "none"],
                        },
                    },
                ],
                "business": [
                    {
                        "key": "business_revenue",
                        "question": "Is revenue trend currently rising, flat, or declining?",
                        "options": {
                            "rising": ["rising", "up", "growth", "improving"],
                            "flat": ["flat", "same", "stable"],
                            "declining": ["declining", "down", "falling", "loss"],
                        },
                    },
                    {
                        "key": "cash_flow",
                        "question": "Is your cash flow smooth, tight, or under debt pressure?",
                        "options": {
                            "smooth": ["smooth", "good", "comfortable"],
                            "tight": ["tight", "limited", "manageable"],
                            "debt_pressure": ["debt", "loan", "pressure", "emi"],
                        },
                    },
                ],
            },
        },
        "marriage": {
            "display": "marriage",
            "aliases": ["marriage", "shaadi", "vivah", "wedding", "spouse", "husband", "wife"],
            "score_domain": "marriage",
            "signals": {
                "houses": "7th house and Navamsa",
                "planets": ["Venus", "Jupiter"],
                "timing_flag": "marriage_window_active",
                "default_driver": "Venus",
                "default_risk": "Jupiter",
            },
            "status_prompt": (
                "Shaadi ke baare mein sahi guidance dene ke liye pehle current situation samajhna zaroori hai.\n\n"
                "Aapki current situation kya hai?\n"
                "1. Single\n"
                "2. Relationship mein\n"
                "3. Already married"
            ),
            "statuses": {
                "single": {"label": "currently single", "keywords": ["1", "single", "unmarried", "not married"]},
                "relationship": {"label": "currently in a relationship", "keywords": ["2", "relationship", "dating", "partner"]},
                "married": {"label": "already married", "keywords": ["3", "married", "spouse", "wife", "husband"]},
            },
            "diagnostics": {
                "single": [
                    {
                        "key": "proposal_flow",
                        "question": "Have proposals or serious discussions come recently?",
                        "options": {
                            "active": ["yes", "active", "coming", "regular"],
                            "occasional": ["sometimes", "few", "occasional"],
                            "blocked": ["no", "none", "blocked", "not coming"],
                        },
                    },
                    {
                        "key": "family_alignment",
                        "question": "Is family alignment smooth or causing delay?",
                        "options": {
                            "smooth": ["smooth", "supportive", "aligned"],
                            "mixed": ["mixed", "average", "manageable"],
                            "delay": ["delay", "conflict", "issue", "resistance"],
                        },
                    },
                ],
                "relationship": [
                    {
                        "key": "relationship_stability",
                        "question": "Is the relationship stable currently, or uncertain?",
                        "options": {
                            "stable": ["stable", "good", "strong"],
                            "uncertain": ["uncertain", "confused", "mixed"],
                            "conflict": ["conflict", "fight", "stress", "problem"],
                        },
                    },
                    {
                        "key": "marriage_timeline",
                        "question": "Is the marriage timeline mutually clear, or delayed?",
                        "options": {
                            "clear": ["clear", "decided", "fixed"],
                            "delayed": ["delay", "pending", "slow"],
                            "not_discussed": ["not discussed", "unclear", "unknown"],
                        },
                    },
                ],
                "married": [
                    {
                        "key": "married_harmony",
                        "question": "Is current harmony stable, mixed, or under stress?",
                        "options": {
                            "stable": ["stable", "good", "peaceful"],
                            "mixed": ["mixed", "ups and downs", "average"],
                            "stress": ["stress", "conflict", "argument", "distance"],
                        },
                    },
                    {
                        "key": "married_focus",
                        "question": "Is your main concern communication, trust, or family pressure?",
                        "options": {
                            "communication": ["communication", "talk", "misunderstanding"],
                            "trust": ["trust", "doubt", "insecurity"],
                            "family_pressure": ["family", "in-laws", "pressure", "interference"],
                        },
                    },
                ],
            },
        },
        "relationship": {
            "display": "relationship",
            "aliases": ["relationship", "love", "dating", "partner", "commitment", "boyfriend", "girlfriend"],
            "score_domain": "marriage",
            "signals": {
                "houses": "5th and 7th house",
                "planets": ["Venus", "Moon", "Jupiter"],
                "timing_flag": None,
                "default_driver": "Venus",
                "default_risk": "Moon",
            },
            "status_prompt": (
                "For relationship clarity, I first need your current status.\n\n"
                "What best matches your situation?\n"
                "1. Single\n"
                "2. Dating\n"
                "3. Committed relationship"
            ),
            "statuses": {
                "single": {"label": "currently single", "keywords": ["1", "single", "not dating"]},
                "dating": {"label": "currently dating", "keywords": ["2", "dating", "seeing someone", "new relationship"]},
                "committed": {"label": "currently in a committed relationship", "keywords": ["3", "committed", "serious", "long term"]},
            },
            "diagnostics": {
                "single": [
                    {
                        "key": "new_connection_flow",
                        "question": "Are meaningful new connections happening or mostly not progressing?",
                        "options": {
                            "active": ["active", "happening", "good"],
                            "slow": ["slow", "few", "occasional"],
                            "blocked": ["blocked", "none", "not progressing"],
                        },
                    },
                    {
                        "key": "emotional_readiness",
                        "question": "Do you feel emotionally ready right now, or still healing from the past?",
                        "options": {
                            "ready": ["ready", "open"],
                            "healing": ["healing", "recovering", "past"],
                            "confused": ["confused", "not sure", "mixed"],
                        },
                    },
                ],
                "dating": [
                    {
                        "key": "dating_stability",
                        "question": "Is this dating phase becoming stable, or still uncertain?",
                        "options": {
                            "stable": ["stable", "clear", "good"],
                            "uncertain": ["uncertain", "mixed", "not sure"],
                            "volatile": ["volatile", "ups and downs", "conflict"],
                        },
                    },
                    {
                        "key": "commitment_signal",
                        "question": "Are both sides aligned about commitment timeline?",
                        "options": {
                            "aligned": ["aligned", "yes", "same"],
                            "partial": ["partial", "somewhat", "not fully"],
                            "misaligned": ["misaligned", "no", "different", "delay"],
                        },
                    },
                ],
                "committed": [
                    {
                        "key": "bond_strength",
                        "question": "Is trust currently strong, moderate, or under strain?",
                        "options": {
                            "strong": ["strong", "good", "stable"],
                            "moderate": ["moderate", "ok", "average"],
                            "strained": ["strained", "weak", "stress", "conflict"],
                        },
                    },
                    {
                        "key": "external_pressure",
                        "question": "Is external pressure (family/distance/career) affecting the bond?",
                        "options": {
                            "low": ["low", "minimal", "not much"],
                            "medium": ["medium", "some"],
                            "high": ["high", "major", "strong", "yes"],
                        },
                    },
                ],
            },
        },
        "finance": {
            "display": "finance",
            "aliases": ["finance", "money", "paisa", "wealth", "income", "debt", "investment", "cash"],
            "score_domain": "finance",
            "signals": {
                "houses": "2nd and 11th house",
                "planets": ["Jupiter", "Mercury", "Venus"],
                "timing_flag": None,
                "default_driver": "Jupiter",
                "default_risk": "Mercury",
            },
            "status_prompt": (
                "To read your finance trend properly, I need your current money situation first.\n\n"
                "Which is closest right now?\n"
                "1. Stable income\n"
                "2. Unstable income\n"
                "3. Debt pressure"
            ),
            "statuses": {
                "stable_income": {"label": "income is currently stable", "keywords": ["1", "stable", "regular", "consistent"]},
                "unstable_income": {"label": "income is currently unstable", "keywords": ["2", "unstable", "fluctuating", "irregular"]},
                "debt_pressure": {"label": "currently under debt pressure", "keywords": ["3", "debt", "loan", "emi", "pressure"]},
            },
            "diagnostics": {
                "stable_income": [
                    {
                        "key": "savings_rate",
                        "question": "Are you able to save monthly, or does most income get consumed?",
                        "options": {
                            "saving_consistent": ["save", "savings", "consistent", "yes"],
                            "saving_low": ["low", "little", "not much"],
                            "no_saving": ["no", "none", "consumed", "all spent"],
                        },
                    },
                    {
                        "key": "expense_spikes",
                        "question": "Do unexpected expenses happen often?",
                        "options": {
                            "rare": ["rare", "not often", "low"],
                            "moderate": ["sometimes", "moderate", "some"],
                            "frequent": ["often", "frequent", "high"],
                        },
                    },
                ],
                "unstable_income": [
                    {
                        "key": "income_variability",
                        "question": "Is income variability monthly, seasonal, or random?",
                        "options": {
                            "monthly": ["monthly", "every month"],
                            "seasonal": ["seasonal", "cycle"],
                            "random": ["random", "unpredictable", "irregular"],
                        },
                    },
                    {
                        "key": "buffer_months",
                        "question": "Do you have a cash buffer for at least 3 months?",
                        "options": {
                            "yes": ["yes", "have", "buffer"],
                            "partial": ["partial", "some", "1-2 months"],
                            "no": ["no", "none", "not yet"],
                        },
                    },
                ],
                "debt_pressure": [
                    {
                        "key": "debt_type",
                        "question": "Is debt mainly personal/consumer, business, or mixed?",
                        "options": {
                            "personal": ["personal", "consumer", "credit card"],
                            "business": ["business", "working capital"],
                            "mixed": ["mixed", "both"],
                        },
                    },
                    {
                        "key": "repayment_control",
                        "question": "Are repayments currently manageable, tight, or default-risk?",
                        "options": {
                            "manageable": ["manageable", "under control"],
                            "tight": ["tight", "difficult", "pressure"],
                            "default_risk": ["default", "miss", "overdue"],
                        },
                    },
                ],
            },
        },
        "health": {
            "display": "health",
            "aliases": ["health", "sehat", "swasthya", "stress", "disease", "illness", "fitness", "wellness"],
            "score_domain": "health",
            "signals": {
                "houses": "6th house pattern",
                "planets": ["Mars", "Saturn", "Sun"],
                "timing_flag": None,
                "default_driver": "Saturn",
                "default_risk": "Mars",
            },
            "status_prompt": (
                "For health consultation, I first need your primary concern type.\n\n"
                "What is your main concern right now?\n"
                "1. Stress / mental load\n"
                "2. Chronic issue\n"
                "3. General wellness"
            ),
            "statuses": {
                "stress": {"label": "main concern is stress", "keywords": ["1", "stress", "mental", "anxiety", "tension"]},
                "chronic_issue": {"label": "main concern is a chronic issue", "keywords": ["2", "chronic", "long term", "ongoing", "medical"]},
                "wellness": {"label": "main concern is wellness and prevention", "keywords": ["3", "wellness", "fitness", "general", "prevention"]},
            },
            "diagnostics": {
                "stress": [
                    {
                        "key": "stress_pattern",
                        "question": "Is stress mostly work-driven, relationship-driven, or internal overthinking?",
                        "options": {
                            "work": ["work", "job", "career"],
                            "relationship": ["relationship", "family", "marriage"],
                            "internal": ["internal", "overthinking", "mind", "anxiety"],
                        },
                    },
                    {
                        "key": "sleep_quality",
                        "question": "How is sleep quality currently: good, disturbed, or poor?",
                        "options": {
                            "good": ["good", "normal"],
                            "disturbed": ["disturbed", "broken", "irregular"],
                            "poor": ["poor", "bad", "insomnia"],
                        },
                    },
                ],
                "chronic_issue": [
                    {
                        "key": "chronic_trend",
                        "question": "Is the chronic condition improving, stable, or worsening recently?",
                        "options": {
                            "improving": ["improving", "better"],
                            "stable": ["stable", "same"],
                            "worsening": ["worse", "worsening", "declining"],
                        },
                    },
                    {
                        "key": "treatment_consistency",
                        "question": "Is treatment/routine consistent, or frequently interrupted?",
                        "options": {
                            "consistent": ["consistent", "regular"],
                            "mixed": ["mixed", "sometimes", "irregular"],
                            "interrupted": ["interrupted", "not regular", "stopped"],
                        },
                    },
                ],
                "wellness": [
                    {
                        "key": "energy_level",
                        "question": "How is your day-to-day energy: high, moderate, or low?",
                        "options": {
                            "high": ["high", "good", "energetic"],
                            "moderate": ["moderate", "average"],
                            "low": ["low", "tired", "fatigue"],
                        },
                    },
                    {
                        "key": "routine_discipline",
                        "question": "Is your sleep-food-exercise routine disciplined right now?",
                        "options": {
                            "disciplined": ["disciplined", "regular", "yes"],
                            "partial": ["partial", "somewhat"],
                            "undisciplined": ["undisciplined", "irregular", "no"],
                        },
                    },
                ],
            },
        },
        "family": {
            "display": "family",
            "aliases": ["family", "parents", "home", "mother", "father", "siblings", "ghar", "parivar"],
            "score_domain": "marriage",
            "signals": {
                "houses": "2nd and 4th house",
                "planets": ["Moon", "Jupiter", "Venus"],
                "timing_flag": None,
                "default_driver": "Moon",
                "default_risk": "Venus",
            },
            "status_prompt": (
                "For family consultation, I need your present family context first.\n\n"
                "Which fits best?\n"
                "1. Mostly peaceful\n"
                "2. Repeated conflicts\n"
                "3. Major decision phase"
            ),
            "statuses": {
                "peaceful": {"label": "family environment is mostly peaceful", "keywords": ["1", "peaceful", "good", "stable"]},
                "conflict": {"label": "family is facing repeated conflicts", "keywords": ["2", "conflict", "issues", "arguments", "stress"]},
                "decision": {"label": "family is in a major decision phase", "keywords": ["3", "decision", "property", "shift", "transition"]},
            },
            "diagnostics": {
                "peaceful": [
                    {
                        "key": "peace_sensitivity",
                        "question": "Do small triggers still disturb harmony often?",
                        "options": {
                            "rare": ["rare", "not often"],
                            "sometimes": ["sometimes", "few"],
                            "often": ["often", "frequent", "yes"],
                        },
                    },
                    {
                        "key": "family_priority",
                        "question": "Is your current focus emotional bonding, property, or elders health support?",
                        "options": {
                            "bonding": ["bonding", "emotion", "relationship"],
                            "property": ["property", "house", "asset"],
                            "elders_health": ["elder", "parents health", "care"],
                        },
                    },
                ],
                "conflict": [
                    {
                        "key": "conflict_source",
                        "question": "Is conflict mainly communication, money, or boundaries?",
                        "options": {
                            "communication": ["communication", "talk", "misunderstanding"],
                            "money": ["money", "finance", "expense", "property"],
                            "boundaries": ["boundaries", "control", "interference"],
                        },
                    },
                    {
                        "key": "conflict_intensity",
                        "question": "Is intensity currently low, medium, or high?",
                        "options": {
                            "low": ["low", "mild"],
                            "medium": ["medium", "moderate"],
                            "high": ["high", "severe", "strong"],
                        },
                    },
                ],
                "decision": [
                    {
                        "key": "decision_type",
                        "question": "Is this about relocation, property, or family role responsibility?",
                        "options": {
                            "relocation": ["relocation", "move", "shift"],
                            "property": ["property", "asset", "house"],
                            "role": ["role", "responsibility", "duty"],
                        },
                    },
                    {
                        "key": "decision_timeline",
                        "question": "Is the timeline immediate, 3-6 months, or long term?",
                        "options": {
                            "immediate": ["immediate", "now", "urgent"],
                            "mid": ["3", "6", "months", "mid"],
                            "long": ["long", "year", "later"],
                        },
                    },
                ],
            },
        },
        "education": {
            "display": "education",
            "aliases": ["education", "study", "exam", "college", "course", "learning", "student", "academics"],
            "score_domain": "career",
            "signals": {
                "houses": "4th and 5th house",
                "planets": ["Mercury", "Jupiter", "Sun"],
                "timing_flag": None,
                "default_driver": "Mercury",
                "default_risk": "Sun",
            },
            "status_prompt": (
                "For education guidance, tell me your present track first.\n\n"
                "Which one matches?\n"
                "1. School/college student\n"
                "2. Competitive exam prep\n"
                "3. Skill upgrade / certification"
            ),
            "statuses": {
                "student": {"label": "currently in regular academics", "keywords": ["1", "student", "college", "school", "university"]},
                "exam_prep": {"label": "currently preparing for competitive exams", "keywords": ["2", "exam", "preparation", "competitive", "upsc", "gate"]},
                "skill_upgrade": {"label": "currently focused on skill upgrade", "keywords": ["3", "skill", "certification", "course", "training"]},
            },
            "diagnostics": {
                "student": [
                    {
                        "key": "focus_quality",
                        "question": "Is your study focus consistent, patchy, or weak right now?",
                        "options": {
                            "consistent": ["consistent", "regular", "good"],
                            "patchy": ["patchy", "irregular", "ups and downs"],
                            "weak": ["weak", "low", "poor"],
                        },
                    },
                    {
                        "key": "result_trend",
                        "question": "Are results improving, flat, or declining?",
                        "options": {
                            "improving": ["improving", "better", "up"],
                            "flat": ["flat", "same", "stable"],
                            "declining": ["declining", "down", "worse"],
                        },
                    },
                ],
                "exam_prep": [
                    {
                        "key": "syllabus_coverage",
                        "question": "Is syllabus coverage on track, delayed, or far behind?",
                        "options": {
                            "on_track": ["on track", "good", "covered"],
                            "delayed": ["delayed", "behind", "slow"],
                            "far_behind": ["far behind", "very delayed", "much behind"],
                        },
                    },
                    {
                        "key": "mock_performance",
                        "question": "How is mock test consistency: improving, volatile, or weak?",
                        "options": {
                            "improving": ["improving", "better"],
                            "volatile": ["volatile", "fluctuating", "mixed"],
                            "weak": ["weak", "low", "poor"],
                        },
                    },
                ],
                "skill_upgrade": [
                    {
                        "key": "skill_goal",
                        "question": "Is your skill goal job-linked, business-linked, or exploratory?",
                        "options": {
                            "job_linked": ["job", "career", "placement"],
                            "business_linked": ["business", "freelance", "client"],
                            "exploratory": ["explore", "interest", "learning"],
                        },
                    },
                    {
                        "key": "learning_discipline",
                        "question": "Is your learning routine daily, weekly, or inconsistent?",
                        "options": {
                            "daily": ["daily", "regular"],
                            "weekly": ["weekly", "weekends"],
                            "inconsistent": ["inconsistent", "irregular", "random"],
                        },
                    },
                ],
            },
        },
        "general_life_guidance": {
            "display": "general life guidance",
            "aliases": ["general guidance", "life guidance", "overall life", "life direction", "future guidance", "general life"],
            "score_domain": None,
            "signals": {
                "houses": "Lagna and Moon pattern",
                "planets": ["Moon", "Jupiter", "Saturn"],
                "timing_flag": None,
                "default_driver": "Moon",
                "default_risk": "Saturn",
            },
            "status_prompt": (
                "For overall life guidance, I first need your current phase.\n\n"
                "Which best fits?\n"
                "1. Feeling stuck/confused\n"
                "2. Major decision ahead\n"
                "3. Stable but seeking better direction"
            ),
            "statuses": {
                "stuck": {"label": "currently feeling stuck", "keywords": ["1", "stuck", "confused", "lost", "unclear"]},
                "decision": {"label": "currently facing a major decision", "keywords": ["2", "decision", "choice", "crossroad"]},
                "optimization": {"label": "stable but seeking better direction", "keywords": ["3", "stable", "improve", "better direction", "optimize"]},
            },
            "diagnostics": {
                "stuck": [
                    {
                        "key": "stuck_area",
                        "question": "Is this stuck feeling mostly in career, relationships, or inner clarity?",
                        "options": {
                            "career": ["career", "job", "work"],
                            "relationships": ["relationship", "family", "marriage"],
                            "inner_clarity": ["inner", "mind", "clarity", "purpose"],
                        },
                    },
                    {
                        "key": "energy_shift",
                        "question": "Has this been recent, medium-term, or long-term pattern?",
                        "options": {
                            "recent": ["recent", "few weeks", "new"],
                            "medium": ["months", "3", "6"],
                            "long": ["long", "year", "years"],
                        },
                    },
                ],
                "decision": [
                    {
                        "key": "decision_area",
                        "question": "Is the decision mainly personal, professional, or financial?",
                        "options": {
                            "personal": ["personal", "relationship", "family"],
                            "professional": ["professional", "career", "job", "business"],
                            "financial": ["financial", "money", "investment", "asset"],
                        },
                    },
                    {
                        "key": "decision_urgency",
                        "question": "Is this decision immediate or can it be paced over months?",
                        "options": {
                            "immediate": ["immediate", "urgent", "now"],
                            "paced": ["paced", "months", "time", "can wait"],
                        },
                    },
                ],
                "optimization": [
                    {
                        "key": "growth_target",
                        "question": "Is your current target more stability, expansion, or inner balance?",
                        "options": {
                            "stability": ["stability", "secure", "steady"],
                            "expansion": ["expansion", "growth", "scale"],
                            "balance": ["balance", "inner peace", "alignment"],
                        },
                    },
                    {
                        "key": "time_horizon",
                        "question": "Are you planning changes for 3 months, 1 year, or longer horizon?",
                        "options": {
                            "short": ["3 months", "short", "near"],
                            "mid": ["1 year", "year", "mid"],
                            "long": ["long", "longer", "multi year"],
                        },
                    },
                ],
            },
        },
    }

    _LEGACY_STAGE_MAP = {
        "STATE_DOMAIN_ENTRY": DOMAIN_ENTRY,
        "STAGE_CHART_READING": DOMAIN_ENTRY,
        "STAGE_SITUATION_ANALYSIS": DIAGNOSTIC,
        "STAGE_STRATEGY_GUIDANCE": GUIDANCE,
        "STAGE_ACTION_PLAN": ACTION_PLAN,
    }

    _DIAGNOSTIC_WORDS = {
        "career": "career",
        "marriage": "marriage",
        "relationship": "relationship",
        "finance": "finance",
        "health": "health",
        "family": "family",
        "education": "education",
        "general_life_guidance": "life direction",
    }

    @staticmethod
    def _normalized(text: Any) -> str:
        value = str(text or "").strip().lower()
        return re.sub(r"\s+", " ", value)

    @staticmethod
    def _limit_words(text: str, limit: int | None = None) -> str:
        words = str(text or "").split()
        max_words = limit or ConsultationEngine._MAX_RESPONSE_WORDS
        if len(words) <= max_words:
            return str(text or "").strip()
        return " ".join(words[:max_words]).strip()

    @staticmethod
    def _normalize_stage(stage: str | None) -> str:
        if not stage:
            return ConsultationEngine.DOMAIN_ENTRY
        return ConsultationEngine._LEGACY_STAGE_MAP.get(str(stage), str(stage))

    @staticmethod
    def _new_state() -> dict[str, Any]:
        return {
            ConsultationEngine._STATE_MARKER: True,
            "version": ConsultationEngine._STATE_VERSION,
            "active_domain": None,
            "domain_memory": {},
            "domain_insights": {},
            "memory": {},
        }

    @staticmethod
    def _load_state(blob: Any) -> dict[str, Any]:
        if not blob:
            return ConsultationEngine._new_state()

        try:
            parsed = json.loads(str(blob))
        except Exception:
            return ConsultationEngine._new_state()

        if not isinstance(parsed, dict):
            return ConsultationEngine._new_state()

        if not parsed.get(ConsultationEngine._STATE_MARKER):
            return ConsultationEngine._new_state()

        parsed.setdefault("version", ConsultationEngine._STATE_VERSION)
        parsed.setdefault("active_domain", None)
        parsed.setdefault("domain_memory", {})
        parsed.setdefault("domain_insights", {})
        parsed.setdefault("memory", {})
        return parsed

    @staticmethod
    def _dump_state(state: dict[str, Any]) -> str:
        return json.dumps(state, ensure_ascii=False, separators=(",", ":"))

    @staticmethod
    def _ensure_domain_memory(state: dict[str, Any], domain: str) -> dict[str, Any]:
        bucket = state["domain_memory"].get(domain)
        if not isinstance(bucket, dict):
            bucket = {}

        bucket.setdefault("status", None)
        bucket.setdefault("diagnostics", {})
        bucket.setdefault("diagnostic_index", 0)
        bucket.setdefault("last_question_key", None)
        bucket.setdefault("interpretation_done", False)
        bucket.setdefault("guidance_done", False)
        bucket.setdefault("action_done", False)

        state["domain_memory"][domain] = bucket
        return bucket

    @staticmethod
    def detect_domain(text: Any, current_domain: str | None = None) -> str | None:
        t = ConsultationEngine._normalized(text)
        if not t:
            return None

        best_domain = None
        best_alias = ""
        for domain, config in ConsultationEngine._DOMAIN_CONFIG.items():
            for alias in config["aliases"]:
                a = alias.lower().strip()
                if not a:
                    continue

                matched = False
                if " " in a:
                    if a in t:
                        matched = True
                else:
                    if re.search(rf"\b{re.escape(a)}\b", t):
                        matched = True

                if matched and len(a) > len(best_alias):
                    best_domain = domain
                    best_alias = a

        if not best_domain:
            return None

        if not current_domain or best_domain == current_domain:
            return best_domain

        words = t.split()
        explicit_switch = t == best_alias

        if not explicit_switch and len(words) <= 2 and best_alias in t:
            explicit_switch = True

        if not explicit_switch:
            switch_markers = (
                "about",
                "regarding",
                "guidance",
                "consultation",
                "topic",
                "domain",
                "switch",
                "now",
            )
            if any(marker in t for marker in switch_markers) and best_alias in t:
                explicit_switch = True

        return best_domain if explicit_switch else None

    @staticmethod
    def score_domain(domain: str | None) -> str | None:
        if not domain:
            return None
        config = ConsultationEngine._DOMAIN_CONFIG.get(domain)
        if not config:
            return None
        return config.get("score_domain")

    @staticmethod
    def _domain_config(domain: str) -> dict[str, Any] | None:
        return ConsultationEngine._DOMAIN_CONFIG.get(domain)

    @staticmethod
    def _parse_from_keywords(user_text: str, keyword_map: dict[str, list[str]]) -> str | None:
        t = ConsultationEngine._normalized(user_text)
        if not t:
            return None

        if t in {"1", "2", "3"}:
            numeric = int(t) - 1
            keys = list(keyword_map.keys())
            if 0 <= numeric < len(keys):
                return keys[numeric]

        for key, values in keyword_map.items():
            for token in values:
                token_n = token.lower().strip()
                if not token_n:
                    continue

                if " " in token_n:
                    if token_n in t:
                        return key
                else:
                    if re.search(rf"\b{re.escape(token_n)}\b", t):
                        return key

        return None

    @staticmethod
    def _status_question(domain: str) -> str:
        return ConsultationEngine._DOMAIN_CONFIG[domain]["status_prompt"]

    @staticmethod
    def _parse_status(domain: str, user_text: str) -> str | None:
        status_map = {
            key: value["keywords"]
            for key, value in ConsultationEngine._DOMAIN_CONFIG[domain]["statuses"].items()
        }
        return ConsultationEngine._parse_from_keywords(user_text, status_map)

    @staticmethod
    def _status_label(domain: str, status: str) -> str:
        statuses = ConsultationEngine._DOMAIN_CONFIG[domain]["statuses"]
        info = statuses.get(status, {})
        return str(info.get("label") or status).strip()

    @staticmethod
    def _diagnostic_questions(domain: str, status: str) -> list[dict[str, Any]]:
        return list(ConsultationEngine._DOMAIN_CONFIG[domain]["diagnostics"].get(status, []))

    @staticmethod
    def _record_last_diagnostic_answer(domain: str, memory: dict[str, Any], user_text: str, state: dict[str, Any]) -> None:
        questions = ConsultationEngine._diagnostic_questions(domain, memory.get("status"))
        asked_count = int(memory.get("diagnostic_index") or 0)
        previous_index = asked_count - 1

        if previous_index < 0 or previous_index >= len(questions):
            return

        q = questions[previous_index]
        key = q["key"]

        if key in memory["diagnostics"]:
            return

        option_map = q.get("options") or {}
        parsed = ConsultationEngine._parse_from_keywords(user_text, option_map) if option_map else None

        if parsed:
            memory["diagnostics"][key] = parsed
            memory["diagnostics"][f"{key}_raw"] = str(user_text or "").strip()
            state["memory"][f"{domain}_{key}"] = parsed
            return

        raw = str(user_text or "").strip()
        if raw:
            memory["diagnostics"][key] = "free_text"
            memory["diagnostics"][f"{key}_raw"] = raw
            state["memory"][f"{domain}_{key}"] = raw

    @staticmethod
    def _next_diagnostic_question(domain: str, memory: dict[str, Any]) -> str | None:
        status = memory.get("status")
        if not status:
            return None

        questions = ConsultationEngine._diagnostic_questions(domain, status)
        idx = int(memory.get("diagnostic_index") or 0)

        if idx >= len(questions):
            return None

        q = questions[idx]
        memory["diagnostic_index"] = idx + 1
        memory["last_question_key"] = q.get("key")
        return str(q.get("question") or "").strip()

    @staticmethod
    def _diagnostic_summary(domain: str, memory: dict[str, Any]) -> str:
        items = []
        for key, value in memory.get("diagnostics", {}).items():
            if key.endswith("_raw"):
                continue
            raw = str(memory["diagnostics"].get(f"{key}_raw") or "").strip()
            if value == "free_text" and raw:
                items.append(raw)
            elif raw:
                items.append(f"{key.replace('_', ' ')}: {value}")
            else:
                items.append(f"{key.replace('_', ' ')}: {value}")

        if not items:
            return "diagnostic details are still limited"

        return "; ".join(items[:3])

    @staticmethod
    def _driver_and_risk(domain: str, domain_data: dict[str, Any]) -> tuple[str, str]:
        config = ConsultationEngine._DOMAIN_CONFIG[domain]["signals"]
        allowed = list(config["planets"])
        default_driver = str(config.get("default_driver") or allowed[0])
        default_risk = str(config.get("default_risk") or allowed[-1])

        raw_driver = str(domain_data.get("primary_driver") or "").strip().title()
        raw_risk = str(domain_data.get("risk_factor") or "").strip().title()

        driver = raw_driver if raw_driver in allowed else default_driver
        risk = raw_risk if raw_risk in allowed else default_risk

        if risk == driver and len(allowed) > 1:
            risk = allowed[-1] if allowed[-1] != driver else allowed[0]

        return driver, risk

    @staticmethod
    def _build_domain_insight(
        domain: str,
        domain_data: dict[str, Any],
        current_dasha: dict[str, Any],
        chart: dict[str, Any],
    ) -> dict[str, Any]:
        config = ConsultationEngine._DOMAIN_CONFIG[domain]
        signal_config = config["signals"]

        momentum = str(domain_data.get("momentum") or "Neutral").lower()
        driver, risk = ConsultationEngine._driver_and_risk(domain, domain_data)

        if momentum == "positive":
            observation = f"{config['display'].title()} trend shows supportive momentum with steady progress potential."
        elif momentum == "challenging":
            observation = f"{config['display'].title()} trend shows pressure and delay, so timing discipline is critical."
        else:
            observation = f"{config['display'].title()} trend is mixed but workable with structured decisions."

        signal_line = (
            f"For this question, I am reading {signal_config['houses']} with {', '.join(signal_config['planets'])}. "
            f"Current lead influence is {driver}, and caution zone is {risk}."
        )

        dasha = current_dasha or {}
        md = str(dasha.get("mahadasha") or "").strip().title()
        ad = str(dasha.get("antardasha") or "").strip().title()

        if md and ad and (md in signal_config["planets"] or ad in signal_config["planets"]):
            timing_line = f"Relevant dasha influence in this domain is {md}-{ad}."
        elif md and md in signal_config["planets"]:
            timing_line = f"Relevant dasha influence in this domain is {md}."
        else:
            timing_line = "Timing in this domain looks gradual, so phased execution will work better than sudden moves."

        timing_flag = signal_config.get("timing_flag")
        if timing_flag:
            window_open = bool((chart or {}).get(timing_flag))
            if window_open:
                timing_line = f"{timing_line} This period looks comparatively supportive for this area."
            else:
                timing_line = f"{timing_line} This period needs more patience before major moves."

        return {
            "observation": observation,
            "signal_line": signal_line,
            "timing_line": timing_line,
            "driver": driver,
            "risk": risk,
            "display": config["display"],
        }

    @staticmethod
    def _get_cached_or_build_insight(
        state: dict[str, Any],
        domain: str,
        domain_data: dict[str, Any],
        current_dasha: dict[str, Any],
        chart: dict[str, Any],
    ) -> tuple[dict[str, Any], bool]:
        cached = state["domain_insights"].get(domain)
        if isinstance(cached, dict):
            return cached, False

        built = ConsultationEngine._build_domain_insight(domain, domain_data, current_dasha, chart)
        state["domain_insights"][domain] = built
        return built, True

    @staticmethod
    def _build_interpretation_response(domain: str, memory: dict[str, Any], insight: dict[str, Any]) -> tuple[str, str]:
        status_label = ConsultationEngine._status_label(domain, memory.get("status"))
        diagnostic_summary = ConsultationEngine._diagnostic_summary(domain, memory)
        focus_word = ConsultationEngine._DIAGNOSTIC_WORDS.get(domain, domain)

        text = (
            f"Since you mentioned you are {status_label}, and shared that {diagnostic_summary}, "
            f"I can now interpret your {focus_word} signals clearly. "
            f"{insight['observation']} {insight['signal_line']} {insight['timing_line']} "
            f"Based on this, the direction is possible, but decisions should be phased and practical. "
            "Let me now give you precise guidance tailored to this exact situation."
        )

        followup = "Share your biggest immediate concern in this same domain, and I will tune guidance around it."
        return ConsultationEngine._limit_words(text), followup

    @staticmethod
    def _build_guidance_response(domain: str, memory: dict[str, Any], insight: dict[str, Any], user_text: str) -> tuple[str, str]:
        status_label = ConsultationEngine._status_label(domain, memory.get("status"))
        concern = str(user_text or "").strip()
        concern_line = f"You just added this concern: '{concern}'. " if concern else ""

        text = (
            f"Based on your chart indicators for {domain}, here is practical guidance for your current track. "
            f"Since you are {status_label}, keep actions aligned with {insight['driver']} patterns and avoid reactive decisions linked to {insight['risk']}. "
            f"{concern_line}"
            "In the next few weeks, focus on one measurable step, one communication correction, and one timing-aware decision. "
            "This keeps progress realistic and prevents repeating old patterns."
        )

        followup = "If you want, I can now convert this into a concrete 30-day action plan."
        return ConsultationEngine._limit_words(text), followup

    @staticmethod
    def _build_action_plan_response(domain: str, memory: dict[str, Any], insight: dict[str, Any], user_text: str) -> tuple[str, str]:
        status_label = ConsultationEngine._status_label(domain, memory.get("status"))
        user_need = str(user_text or "").strip()

        steps = [
            "Week 1: Define one clear objective and remove one known blocker.",
            "Week 2: Execute two disciplined actions aligned to your current context.",
            "Week 3: Review outcomes and correct decisions that were emotionally reactive.",
            "Week 4: Consolidate gains and lock the next month priority.",
        ]

        text = (
            f"30-day action plan for your {domain} consultation: "
            f"Because you are {status_label}, and we are using the same {insight['driver']}-led signal pattern, "
            f"follow this sequence. {steps[0]} {steps[1]} {steps[2]} {steps[3]} "
            f"This reduces {insight['risk']} type setbacks and keeps results stable."
        )

        if user_need:
            text = f"{text} Also, I have considered your note: '{user_need}'."

        followup = "Update me after 7 days with what moved and what got blocked; I will refine the next cycle."
        return ConsultationEngine._limit_words(text), followup

    @staticmethod
    def next_stage(current_stage: str | None) -> str:
        stage = ConsultationEngine._normalize_stage(current_stage)

        if stage == ConsultationEngine.DOMAIN_ENTRY:
            return ConsultationEngine.STATUS_CAPTURE

        if stage == ConsultationEngine.STATUS_CAPTURE:
            return ConsultationEngine.DIAGNOSTIC

        if stage == ConsultationEngine.DIAGNOSTIC:
            return ConsultationEngine.INTERPRETATION

        if stage == ConsultationEngine.INTERPRETATION:
            return ConsultationEngine.GUIDANCE

        if stage == ConsultationEngine.GUIDANCE:
            return ConsultationEngine.ACTION_PLAN

        return ConsultationEngine.ACTION_PLAN

    @staticmethod
    def generate_response(
        domain,
        domain_data,
        language,
        script,
        stage,
        age,
        life_stage,
        user_goal,
        current_dasha,
        transits,
        persona_introduced=False,
        chart=None,
        theme_shown=False,
        user_text="",
        session_state_blob=None,
        domain_switched=False,
    ):
        del language, script, age, life_stage, user_goal, transits, persona_introduced, theme_shown

        stage = ConsultationEngine._normalize_stage(stage)

        if domain not in ConsultationEngine._DOMAIN_CONFIG:
            return {
                "text": (
                    "Please tell me the area first: career, marriage, relationship, finance, health, "
                    "family, education, or general life guidance."
                ),
                "followup_question": "Which domain should we focus on right now?",
                "persona_added": False,
                "theme_used": False,
                "next_stage": ConsultationEngine.DOMAIN_ENTRY,
                "state_blob": session_state_blob,
            }

        state = ConsultationEngine._load_state(session_state_blob)
        memory = ConsultationEngine._ensure_domain_memory(state, domain)

        if domain_switched or state.get("active_domain") != domain:
            stage = ConsultationEngine.DOMAIN_ENTRY

        state["active_domain"] = domain

        response_text = ""
        followup_question = ""
        next_stage = ConsultationEngine.next_stage(stage)
        theme_used = False

        if stage == ConsultationEngine.DOMAIN_ENTRY:
            response_text = ConsultationEngine._status_question(domain)
            followup_question = response_text
            memory["last_question_key"] = "status"
            next_stage = ConsultationEngine.STATUS_CAPTURE

        elif stage == ConsultationEngine.STATUS_CAPTURE:
            parsed_status = ConsultationEngine._parse_status(domain, user_text)
            if not parsed_status:
                response_text = (
                    "To keep the consultation accurate, I need one clear status option first.\n\n"
                    f"{ConsultationEngine._status_question(domain)}"
                )
                followup_question = ConsultationEngine._status_question(domain)
                next_stage = ConsultationEngine.STATUS_CAPTURE
            else:
                memory["status"] = parsed_status
                memory["diagnostics"] = {}
                memory["diagnostic_index"] = 0
                memory["interpretation_done"] = False
                memory["guidance_done"] = False
                memory["action_done"] = False
                state["memory"][f"{domain}_status"] = parsed_status

                question = ConsultationEngine._next_diagnostic_question(domain, memory)
                if question:
                    response_text = (
                        f"Noted. Current status: {ConsultationEngine._status_label(domain, parsed_status)}. "
                        "Now I need one diagnostic point before interpretation.\n\n"
                        f"{question}"
                    )
                    followup_question = question
                    next_stage = ConsultationEngine.DIAGNOSTIC
                else:
                    insight, created = ConsultationEngine._get_cached_or_build_insight(
                        state,
                        domain,
                        domain_data or {},
                        current_dasha or {},
                        chart or {},
                    )
                    theme_used = created
                    response_text, followup_question = ConsultationEngine._build_interpretation_response(
                        domain,
                        memory,
                        insight,
                    )
                    memory["interpretation_done"] = True
                    next_stage = ConsultationEngine.INTERPRETATION

        elif stage == ConsultationEngine.DIAGNOSTIC:
            if not memory.get("status"):
                response_text = ConsultationEngine._status_question(domain)
                followup_question = response_text
                next_stage = ConsultationEngine.STATUS_CAPTURE
            else:
                ConsultationEngine._record_last_diagnostic_answer(domain, memory, user_text, state)
                question = ConsultationEngine._next_diagnostic_question(domain, memory)

                if question:
                    response_text = question
                    followup_question = question
                    next_stage = ConsultationEngine.DIAGNOSTIC
                else:
                    insight, created = ConsultationEngine._get_cached_or_build_insight(
                        state,
                        domain,
                        domain_data or {},
                        current_dasha or {},
                        chart or {},
                    )
                    theme_used = created
                    response_text, followup_question = ConsultationEngine._build_interpretation_response(
                        domain,
                        memory,
                        insight,
                    )
                    memory["interpretation_done"] = True
                    next_stage = ConsultationEngine.INTERPRETATION

        elif stage == ConsultationEngine.INTERPRETATION:
            insight, created = ConsultationEngine._get_cached_or_build_insight(
                state,
                domain,
                domain_data or {},
                current_dasha or {},
                chart or {},
            )
            theme_used = created
            response_text, followup_question = ConsultationEngine._build_guidance_response(
                domain,
                memory,
                insight,
                user_text,
            )
            next_stage = ConsultationEngine.GUIDANCE

        elif stage == ConsultationEngine.GUIDANCE:
            insight, created = ConsultationEngine._get_cached_or_build_insight(
                state,
                domain,
                domain_data or {},
                current_dasha or {},
                chart or {},
            )
            theme_used = created
            response_text, followup_question = ConsultationEngine._build_action_plan_response(
                domain,
                memory,
                insight,
                user_text,
            )
            memory["action_done"] = True
            next_stage = ConsultationEngine.ACTION_PLAN

        else:
            insight, created = ConsultationEngine._get_cached_or_build_insight(
                state,
                domain,
                domain_data or {},
                current_dasha or {},
                chart or {},
            )
            theme_used = created
            response_text, followup_question = ConsultationEngine._build_action_plan_response(
                domain,
                memory,
                insight,
                user_text,
            )
            memory["action_done"] = True
            next_stage = ConsultationEngine.ACTION_PLAN

        state["domain_memory"][domain] = memory
        state_blob = ConsultationEngine._dump_state(state)

        return {
            "text": ConsultationEngine._limit_words(response_text),
            "followup_question": followup_question,
            "persona_added": False,
            "theme_used": theme_used,
            "next_stage": next_stage,
            "state_blob": state_blob,
        }
