from decimal import Decimal
import re


def intcomma(value):
    """
    Convert an integer to a string containing commas every three digits.
    For example, 3000 becomes '3,000' and 45000 becomes '45,000'.
    """
    result = str(value)
    match = re.match(r"-?\d+", result)
    if match:
        prefix = match[0]
        prefix_with_commas = re.sub(r"\d{3}", r"\g<0>,", prefix[::-1])[::-1]
        # Remove a leading comma, if needed.
        prefix_with_commas = re.sub(r"^(-?),", r"\1", prefix_with_commas)
        result = prefix_with_commas + result[len(prefix) :]
    return result


print(intcomma(3000.00))
print(intcomma(45000000.00))
print(intcomma(113500.0))
