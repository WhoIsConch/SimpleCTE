def format_phone(phone_number: int, truncate: bool = True) -> str:
    """
    Convert a ten-digit or eleven-digit phone number, such as
    1234567890 or 11234567890, into a formatted phone number, such as
    (123) 456-7890 or +1 (123) 456-7890.
    """
    phone_number = str(phone_number)

    if len(phone_number) == 10:
        return f"({phone_number[:3]}) {phone_number[3:6]}-{phone_number[6:]}"
    elif len(phone_number) == 11:
        return f"+{phone_number[0]} ({phone_number[1:4]}) {phone_number[4:7]}-{phone_number[7:]}"
    else:
        if len(phone_number) > 15 and truncate:
            return str(phone_number)[:15] + "..."

        return str(phone_number)


def strip_phone(phone_number: str) -> int:
    """
    Convert a formatted phone number, such as (123) 456-7890 or
    +1 (123) 456-7890, into a ten-digit or eleven-digit phone number,
    such as 1234567890 or 11234567890.
    """
    phone_number = (
        phone_number.replace("(", "")
        .replace(")", "")
        .replace("-", "")
        .replace(" ", "")
        .replace("+", "")
    )

    return int(phone_number)
