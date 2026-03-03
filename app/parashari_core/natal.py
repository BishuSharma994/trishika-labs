from datetime import datetime


def parse_datetime(dob: str, time: str):
    """
    Robust datetime parser for production.

    Supported DOB formats:
        - DD-MM-YYYY
        - YYYY-MM-DD

    Supported time formats:
        - HH:MM (24-hour)
        - HH:MM AM/PM
    """

    # ---------------------------------------------------------
    # Parse Date of Birth
    # ---------------------------------------------------------

    dob_obj = None
    dob_formats = ["%d-%m-%Y", "%Y-%m-%d"]

    for fmt in dob_formats:
        try:
            dob_obj = datetime.strptime(dob.strip(), fmt)
            break
        except ValueError:
            continue

    if dob_obj is None:
        raise ValueError("Invalid date format. Use DD-MM-YYYY or YYYY-MM-DD")

    # ---------------------------------------------------------
    # Parse Time of Birth
    # ---------------------------------------------------------

    time_obj = None
    time_formats = ["%H:%M", "%I:%M %p"]

    for fmt in time_formats:
        try:
            time_obj = datetime.strptime(time.strip(), fmt)
            break
        except ValueError:
            continue

    if time_obj is None:
        raise ValueError("Invalid time format. Use HH:MM or HH:MM AM/PM")

    # ---------------------------------------------------------
    # Combine
    # ---------------------------------------------------------

    return datetime(
        dob_obj.year,
        dob_obj.month,
        dob_obj.day,
        time_obj.hour,
        time_obj.minute
    )