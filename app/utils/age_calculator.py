from datetime import date, datetime


class AgeCalculator:

    @staticmethod
    def calculate_age(dob):
        if not dob:
            return None

        try:
            if isinstance(dob, date):
                birth_date = dob
            else:
                birth_date = datetime.strptime(str(dob).strip(), "%Y-%m-%d").date()
        except Exception:
            return None

        today = date.today()
        age = today.year - birth_date.year

        if (today.month, today.day) < (birth_date.month, birth_date.day):
            age -= 1

        return max(age, 0)
