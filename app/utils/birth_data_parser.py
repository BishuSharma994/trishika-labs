import re
from dateutil import parser as date_parser


class BirthDataParser:

    DATE_PATTERNS = [
        r"\d{1,2}[-/]\d{1,2}[-/]\d{4}",
        r"\d{4}-\d{2}-\d{2}",
        r"\d{1,2}\s[A-Za-z]+\s\d{4}"
    ]

    TIME_PATTERNS = [
        r"\d{1,2}[:.]\d{2}\s?(?:AM|PM|am|pm)?"
    ]

    @staticmethod
    def extract_date(text: str):
        for pattern in BirthDataParser.DATE_PATTERNS:
            match = re.search(pattern, text)
            if match:
                try:
                    dt = date_parser.parse(match.group())
                    return dt.date().isoformat(), match.group()
                except Exception:
                    continue
        return None, None

    @staticmethod
    def extract_time(text: str):
        for pattern in BirthDataParser.TIME_PATTERNS:
            match = re.search(pattern, text)
            if match:
                try:
                    dt = date_parser.parse(match.group())
                    return dt.time().strftime("%H:%M"), match.group()
                except Exception:
                    continue
        return None, None

    @staticmethod
    def extract_place(text: str, date_fragment: str, time_fragment: str):
        cleaned = text

        if date_fragment:
            cleaned = cleaned.replace(date_fragment, "")

        if time_fragment:
            cleaned = cleaned.replace(time_fragment, "")

        cleaned = cleaned.strip()

        cleaned = re.sub(r"\b(DOB|dob|born|time|place|at|on)\b", "", cleaned)

        cleaned = cleaned.strip()

        if len(cleaned) == 0:
            return None

        return cleaned

    @staticmethod
    def parse_birth_data(text: str):

        date_value, date_fragment = BirthDataParser.extract_date(text)
        time_value, time_fragment = BirthDataParser.extract_time(text)
        place_value = BirthDataParser.extract_place(text, date_fragment, time_fragment)

        return {
            "date": date_value,
            "time": time_value,
            "place": place_value
        }