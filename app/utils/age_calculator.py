from datetime import date, datetime


def calculate_age(dob: str) -> int:
    """Return age in years for a YYYY-MM-DD date string."""
    if not dob:
        return 0

    try:
        birth_date = datetime.strptime(str(dob).strip(), "%Y-%m-%d").date()
    except Exception:
        return 0

    today = date.today()
    age = today.year - birth_date.year

    if (today.month, today.day) < (birth_date.month, birth_date.day):
        age -= 1

    return max(age, 0)


class AgeCalculator:
    @staticmethod
    def calculate_age(dob: str) -> int:
        return calculate_age(dob)
