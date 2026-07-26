from django import template
from django.utils.safestring import mark_safe
import re

register = template.Library()

# Qualifier code mapping
QUALIFIER_MAPPING = {
    "HS": "High School",
    "CT": "College of Technology",
    "ST": "Specialized Training",
    "UJ": "University Japanese Program",
    "JL": "Japanese Language Institute",
    "JC": "Junior College",
    "A": "Auditors (Undergraduate)",
    "U": "Undergraduate",
    "R": "Research Student",
    "P": "Professional Degree",
    "M": "Master's",
    "D": "Doctoral",
}


@register.filter
def expand_qualifier(qualifier_string):
    """Expand qualifier codes to readable format"""
    if not qualifier_string:
        return ""

    # Split by newlines and process each code
    codes = [code.strip() for code in qualifier_string.split("\n") if code.strip()]

    expanded_names = []
    for code in codes:
        # Handle complex codes like "U(3-4)" or "CT(4-5)"
        base_code = code.split("(")[0].strip()
        expanded_name = QUALIFIER_MAPPING.get(base_code, code)
        expanded_names.append(expanded_name)

    return ", ".join(expanded_names)


@register.filter
def display_grants(value):
    """Display plural_grants data — handle raw Y/N multi-line values"""
    if not value:
        return ""
    parts = [line.strip() for line in value.split("\n") if line.strip()]
    if not parts:
        return ""
    first = parts[0].upper()
    if first == "Y":
        label = "Yes"
    elif first == "N":
        label = "No"
    else:
        label = parts[0]
    if len(parts) > 1:
        return f"{label} — {' '.join(parts[1:])}"
    return label


@register.filter
def expand_selection_method(value):
    """Expand selection method codes"""
    if not value:
        return ""
    mapping = {"D": "Document", "I": "Interview", "W": "Written Exam", "O": "Other"}
    parts = [mapping.get(p.strip(), p.strip()) for p in value.split(",") if p.strip()]
    return ", ".join(parts)


@register.filter
def format_multiline(text):
    """Format multiline text for display with encoding cleanup"""
    if not text:
        return ""

    # Clean up encoding issues
    text = str(text)
    text = text.replace("Ｍ", "M").replace("Ｄ", "D").replace("／", "/")
    text = text.replace("−", "-").replace("ー", "-").replace("，", ",")

    # Remove any remaining full-width characters
    import re

    text = re.sub(r"[^\x00-\x7F]+", " ", text)

    return mark_safe(text.replace("\n", "<br>"))


@register.filter
def get_section_display(section_code):
    """Get display name for section code"""
    section_mapping = {
        "III": "Local Govts & Intl Associations",
        "IV": "Private Foundations",
        "V": "For Applicants Residing Abroad",
    }
    return section_mapping.get(section_code, section_code)


@register.filter
def expand_inquiry_method(value):
    """Expand inquiry method codes"""
    if not value:
        return ""

    # Normalize full-width characters
    value = str(value).replace("Ｆ", "F").replace("Ｓ", "S")

    # Split by newlines and process each code
    parts = [part.strip() for part in value.split("\n") if part.strip()]

    expanded_parts = []
    for part in parts:
        # Handle compound entries like "F・S" or "F / S"
        sub_parts = re.split(r"[・/]", part)
        expanded_subparts = []
        for sub_part in sub_parts:
            sub_part = sub_part.strip().upper()
            if sub_part == "F":
                expanded_subparts.append("Fax")
            elif sub_part == "S":
                expanded_subparts.append("Standard")
            else:
                expanded_subparts.append(sub_part)
        expanded_parts.append(" / ".join(expanded_subparts))

    return ", ".join(expanded_parts)


@register.filter
def expand_application_method(value):
    """Expand application method codes"""
    if not value:
        return ""

    # Normalize full-width characters
    value = str(value).replace("Ｆ", "F").replace("Ｓ", "S")

    # Split by newlines and process each code
    parts = [part.strip() for part in value.split("\n") if part.strip()]

    expanded_parts = []
    for part in parts:
        # Handle compound entries like "F・S" or "F / S"
        sub_parts = re.split(r"[・/]", part)
        expanded_subparts = []
        for sub_part in sub_parts:
            sub_part = sub_part.strip().upper()
            if sub_part == "F":
                expanded_subparts.append("Fax")
            elif sub_part == "S":
                expanded_subparts.append("Standard")
            else:
                expanded_subparts.append(sub_part)
        expanded_parts.append(" / ".join(expanded_subparts))

    return ", ".join(expanded_parts)


@register.filter
def expand_duration(value):
    """Expand duration abbreviations"""
    if not value:
        return ""

    # Normalize the input
    value = str(value).strip()

    # Split by newlines and process each part
    parts = [part.strip() for part in value.split("\n") if part.strip()]

    expanded_parts = []
    for part in parts:
        # Handle patterns like "M: 2y" or "D: 3y"
        if ":" in part:
            sub_parts = part.split(":")
            if len(sub_parts) == 2:
                prefix = sub_parts[0].strip()
                duration = sub_parts[1].strip()
                # Expand prefix if it's a qualifier code
                prefix_expanded = QUALIFIER_MAPPING.get(prefix.upper(), prefix)
                # Expand duration
                duration_expanded = _expand_duration_string(duration)
                expanded_parts.append(f"{prefix_expanded}: {duration_expanded}")
                continue

        # Handle simple duration strings
        expanded_parts.append(_expand_duration_string(part))

    return ", ".join(expanded_parts)


def _expand_duration_string(duration_str):
    """Helper function to expand individual duration strings"""
    if not duration_str:
        return duration_str

    # Replace common abbreviations
    expanded = duration_str

    # Handle time unit abbreviations
    expanded = re.sub(r"(\d+)\s*y\b", r"\1 year(s)", expanded, flags=re.IGNORECASE)
    expanded = re.sub(r"(\d+)\s*m\b", r"\1 month(s)", expanded, flags=re.IGNORECASE)
    expanded = re.sub(r"(\d+)\s*d\b", r"\1 day(s)", expanded, flags=re.IGNORECASE)

    # Handle standalone qualifier codes in duration context
    expanded = re.sub(r"\bM\b", "Master's", expanded)
    expanded = re.sub(r"\bD\b", "Doctoral", expanded)

    # Handle "Within" and "Up to" patterns
    expanded = expanded.replace("Within", "Within")
    expanded = expanded.replace("Up to", "Up to")

    return expanded


@register.simple_tag
def get_qualifier_choices():
    """Get all available qualifier choices"""
    return QUALIFIER_MAPPING


@register.filter
def transform_award_amount(amount_string):
    """
    Transform award amount to formatted monthly value.
    For ranges, shows the range properly formatted.
    For variable amounts, shows "Variable".
    Fixes "0,000" display issues.
    """
    if not amount_string:
        return ""

    try:
        amount_string = str(amount_string).strip()

        # Normalize full-width characters
        amount_string = (
            amount_string.replace("Ｍ", "M").replace("Ｄ", "D").replace("／", "/")
        )
        amount_string = amount_string.replace("−", "-").replace("ー", "-")

        # Handle variable/non-fixed amounts
        variable_indicators = [
            "not fixed",
            "tba",
            "tbc",
            "to be announced",
            "to be confirmed",
            "variable",
            "未定",
            "未確定",
        ]
        if any(indicator in amount_string.lower() for indicator in variable_indicators):
            return "Variable"

        # Handle "Up to..." format
        if (
            "up to" in amount_string.lower()
            or "最大" in amount_string
            or "最高" in amount_string
        ):
            match = re.search(
                r"(\d[\d,]*)\s*(?:/|／)?\s*([YMymy年月])?", amount_string, re.IGNORECASE
            )
            if match:
                value = format_single_value(match.group(1), match.group(2))
                if value:
                    return f"Up to {value}"
            return "Variable"

        # Handle range format (e.g., "25-41,000/Y" or "300-500/Y")
        range_pattern = r"(\d[\d,]*)\s*[-−ー]\s*(\d[\d,]*)\s*(?:/|／)?\s*([YMymy年月])?"
        range_match = re.search(range_pattern, amount_string, re.IGNORECASE)
        if range_match:
            min_val = format_single_value(range_match.group(1), range_match.group(3))
            max_val = format_single_value(range_match.group(2), range_match.group(3))
            if min_val and max_val:
                return f"{min_val} - {max_val}"

        # Handle single value format
        single_pattern = r"(\d[\d,]*)\s*(?:/|／)?\s*([YMymy年月])?"
        single_match = re.search(single_pattern, amount_string, re.IGNORECASE)
        if single_match:
            value = format_single_value(single_match.group(1), single_match.group(2))
            if value:
                return value

        # If no pattern matches, try to find any numbers
        numbers = re.findall(r"\d[\d,]*", amount_string)
        if numbers:
            # Use the largest number found
            clean_numbers = []
            for n in numbers:
                try:
                    clean_numbers.append(float(n.replace(",", "")))
                except ValueError:
                    continue

            if clean_numbers:
                largest = max(clean_numbers) * 1000  # CSV values are in ¥1,000 units
                # Assume it's yearly if very large, otherwise monthly
                if largest > 500000:
                    largest = largest / 12
                return f"¥{int(largest):,}"

        # Return original string if no parsing possible
        return amount_string

    except Exception:
        return amount_string if amount_string else ""


def format_single_value(value_str, time_unit):
    """
    Format a single numeric value as monthly amount in yen.
    Returns formatted string like "¥50,000" or None if parsing fails.
    """
    try:
        # Clean and parse the value (CSV values are in ¥1,000 units)
        value = float(value_str.replace(",", "")) * 1000

        # Convert to monthly if yearly
        time_unit = time_unit.upper() if time_unit else ""
        if time_unit in ["Y", "年"]:
            monthly_value = value / 12
        else:
            monthly_value = value

        # Format with commas and yen symbol
        return f"¥{int(monthly_value):,}"

    except (ValueError, TypeError):
        return None


def extract_single_amount(amount_str, original_string):
    """
    Extract single numeric value and convert to monthly integer.
    Simplified version that handles ranges properly.
    """
    try:
        amount_str = str(amount_str).strip()

        # Clean up full-width characters and hyphens
        amount_str = amount_str.replace("Ｍ", "M").replace("Ｄ", "D").replace("／", "/")
        amount_str = amount_str.replace("−", "-").replace("ー", "-")

        # Clean commas from the amount
        amount_str = amount_str.replace(",", "")

        # Parse the numeric value
        amount = float(amount_str)

        # Determine if yearly or monthly
        yearly_indicators = ["Y", "y", "年"]
        monthly_indicators = ["M", "m", "月"]

        is_yearly = any(
            indicator in str(original_string) for indicator in yearly_indicators
        )
        is_monthly = any(
            indicator in str(original_string) for indicator in monthly_indicators
        )

        if is_yearly and not is_monthly:
            monthly_amount = amount / 12
        else:
            monthly_amount = amount

        return int(monthly_amount)
    except (ValueError, TypeError):
        return None
