from django import template
from django.utils.safestring import mark_safe
import re

register = template.Library()

# Qualifier code mapping
QUALIFIER_MAPPING = {
    'HS': 'High School',
    'CT': 'College of Technology',
    'ST': 'Specialized Training',
    'UJ': 'University Japanese Program',
    'JL': 'Japanese Language Institute',
    'JC': 'Junior College',
    'A': 'Auditors (Undergraduate)',
    'U': 'Undergraduate',
    'R': 'Research Student',
    'P': 'Professional Degree',
    'M': 'Master\'s',
    'D': 'Doctoral'
}

@register.filter
def expand_qualifier(qualifier_string):
    """Expand qualifier codes to readable format"""
    if not qualifier_string:
        return ""

    # Split by newlines and process each code
    codes = [code.strip() for code in qualifier_string.split('\n') if code.strip()]

    expanded_names = []
    for code in codes:
        # Handle complex codes like "U(3-4)" or "CT(4-5)"
        base_code = code.split('(')[0].strip()
        expanded_name = QUALIFIER_MAPPING.get(base_code, code)
        expanded_names.append(expanded_name)

    return ', '.join(expanded_names)

@register.filter
def display_grants(value):
    """Display plural_grants data — handle raw Y/N multi-line values"""
    if not value:
        return ""
    parts = [line.strip() for line in value.split('\n') if line.strip()]
    if not parts:
        return ""
    first = parts[0].upper()
    if first == 'Y':
        label = 'Yes'
    elif first == 'N':
        label = 'No'
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
    mapping = {'D': 'Document', 'I': 'Interview', 'W': 'Written Exam', 'O': 'Other'}
    parts = [mapping.get(p.strip(), p.strip()) for p in value.split(',') if p.strip()]
    return ', '.join(parts)

@register.filter
def format_multiline(text):
    """Format multiline text for display with encoding cleanup"""
    if not text:
        return ""

    # Clean up encoding issues
    text = str(text)
    text = text.replace('Ｍ', 'M').replace('Ｄ', 'D').replace('／', '/')
    text = text.replace('−', '-').replace('ー', '-').replace('，', ',')

    # Remove any remaining full-width characters
    import re
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)

    return mark_safe(text.replace('\n', '<br>'))

@register.filter
def get_section_display(section_code):
    """Get display name for section code"""
    section_mapping = {
        'III': 'Local Govts & Intl Associations',
        'IV': 'Private Foundations',
        'V': 'For Applicants Residing Abroad'
    }
    return section_mapping.get(section_code, section_code)

@register.filter
def expand_inquiry_method(value):
    """Expand inquiry method codes"""
    if not value:
        return ""
    
    # Normalize full-width characters
    value = str(value).replace('Ｆ', 'F').replace('Ｓ', 'S')
    
    # Split by newlines and process each code
    parts = [part.strip() for part in value.split('\n') if part.strip()]
    
    expanded_parts = []
    for part in parts:
        # Handle compound entries like "F・S" or "F / S"
        sub_parts = re.split(r'[・/]', part)
        expanded_subparts = []
        for sub_part in sub_parts:
            sub_part = sub_part.strip().upper()
            if sub_part == 'F':
                expanded_subparts.append('Fax')
            elif sub_part == 'S':
                expanded_subparts.append('Standard')
            else:
                expanded_subparts.append(sub_part)
        expanded_parts.append(' / '.join(expanded_subparts))
    
    return ', '.join(expanded_parts)

@register.filter
def expand_application_method(value):
    """Expand application method codes"""
    if not value:
        return ""
    
    # Normalize full-width characters
    value = str(value).replace('Ｆ', 'F').replace('Ｓ', 'S')
    
    # Split by newlines and process each code
    parts = [part.strip() for part in value.split('\n') if part.strip()]
    
    expanded_parts = []
    for part in parts:
        # Handle compound entries like "F・S" or "F / S"
        sub_parts = re.split(r'[・/]', part)
        expanded_subparts = []
        for sub_part in sub_parts:
            sub_part = sub_part.strip().upper()
            if sub_part == 'F':
                expanded_subparts.append('Fax')
            elif sub_part == 'S':
                expanded_subparts.append('Standard')
            else:
                expanded_subparts.append(sub_part)
        expanded_parts.append(' / '.join(expanded_subparts))
    
    return ', '.join(expanded_parts)

@register.filter
def expand_duration(value):
    """Expand duration abbreviations"""
    if not value:
        return ""
    
    # Normalize the input
    value = str(value).strip()
    
    # Split by newlines and process each part
    parts = [part.strip() for part in value.split('\n') if part.strip()]
    
    expanded_parts = []
    for part in parts:
        # Handle patterns like "M: 2y" or "D: 3y"
        if ':' in part:
            sub_parts = part.split(':')
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
    
    return ', '.join(expanded_parts)

def _expand_duration_string(duration_str):
    """Helper function to expand individual duration strings"""
    if not duration_str:
        return duration_str
    
    # Replace common abbreviations
    expanded = duration_str
    
    # Handle time unit abbreviations
    expanded = re.sub(r'(\d+)\s*y\b', r'\1 year(s)', expanded, flags=re.IGNORECASE)
    expanded = re.sub(r'(\d+)\s*m\b', r'\1 month(s)', expanded, flags=re.IGNORECASE)
    expanded = re.sub(r'(\d+)\s*d\b', r'\1 day(s)', expanded, flags=re.IGNORECASE)
    
    # Handle standalone qualifier codes in duration context
    expanded = re.sub(r'\bM\b', "Master's", expanded)
    expanded = re.sub(r'\bD\b', "Doctoral", expanded)
    
    # Handle "Within" and "Up to" patterns
    expanded = expanded.replace('Within', 'Within')
    expanded = expanded.replace('Up to', 'Up to')
    
    return expanded

@register.simple_tag
def get_qualifier_choices():
    """Get all available qualifier choices"""
    return QUALIFIER_MAPPING

@register.filter
def transform_award_amount(amount_string):
    """Transform award amount to monthly integer range with proper formatting"""
    if not amount_string:
        return ""

    try:
        amount_string = str(amount_string).strip()

        # Normalize full-width characters
        amount_string = amount_string.replace('Ｍ', 'M').replace('Ｄ', 'D').replace('／', '/')

        # Handle variable/non-fixed amounts
        variable_indicators = ['not fixed', 'tba', 'tbc', 'to be announced', 'to be confirmed', 'variable']
        if any(indicator in amount_string.lower() for indicator in variable_indicators):
            return "Variable"

        # Handle "Up to..." format
        if 'up to' in amount_string.lower():
            match = __import__('re').search(r'(\d+(?:-\d+)?)\s*[/／]?[MYmy月]', amount_string, __import__('re').IGNORECASE)
            if match:
                return extract_and_format_amount(match.group(1), amount_string)
            return "Variable"

        # Handle tiered amounts (e.g., "U150/M M180/M D200/M")
        tiered_pattern = r'(\d+(?:-\d+)?\s*[/／]?[MYmy月])'
        tiered_matches = __import__('re').findall(tiered_pattern, amount_string, __import__('re').IGNORECASE)
        if len(tiered_matches) > 1:
            amounts = [extract_single_amount(match, amount_string) for match in tiered_matches]
            valid_amounts = [a for a in amounts if a is not None]
            if valid_amounts:
                return f"{min(valid_amounts):,} - {max(valid_amounts):,},000"

        # Handle range format (e.g., "300-500/Y")
        range_pattern = r'(\d+)\s*[-−ー]\s*(\d+)\s*[/／]?([MYmy月])'
        range_match = __import__('re').search(range_pattern, amount_string, __import__('re').IGNORECASE)
        if range_match:
            return extract_and_format_amount(f"{range_match.group(1)}-{range_match.group(2)}", amount_string)

        # Handle single value format (e.g., "600/Y")
        single_pattern = r'(\d+(?:-\d+)?)\s*[/／]?([MYmy月])'
        single_match = __import__('re').search(single_pattern, amount_string, __import__('re').IGNORECASE)
        if single_match:
            return extract_and_format_amount(single_match.group(1), amount_string)

        # If no pattern matches, try to extract any numbers
        numbers = __import__('re').findall(r'\d+', amount_string)
        if numbers:
            return f"{numbers[0]:,},000"

        return amount_string
    except Exception:
        return amount_string if amount_string else ""

def extract_and_format_amount(amount_part, original_string):
    """Extract and format amount from matched pattern"""
    import re

    # Check if it's a range
    if '-' in amount_part or '−' in amount_part or 'ー' in amount_part:
        parts = re.split(r'[-−ー]', amount_part)
        if len(parts) == 2:
            try:
                min_val = extract_single_amount(parts[0], original_string)
                max_val = extract_single_amount(parts[1], original_string)
                if min_val is not None and max_val is not None:
                    return f"{min_val:,} - {max_val:,},000"
            except (ValueError, TypeError):
                pass

    # Single value
    value = extract_single_amount(amount_part, original_string)
    if value is not None:
        return f"{value:,},000"

    return amount_part

def extract_single_amount(amount_str, original_string):
    """Extract single numeric value and convert to monthly integer"""

    try:
        amount_str = str(amount_str).strip()
        # Clean up full-width characters
        amount_str = amount_str.replace('Ｍ', 'M').replace('Ｄ', 'D').replace('／', '/')

        amount = float(amount_str)

        # Determine if yearly or monthly
        yearly_indicators = ['Y', 'y', '年']
        monthly_indicators = ['M', 'm', '月']

        is_yearly = any(indicator in original_string for indicator in yearly_indicators)
        is_monthly = any(indicator in original_string for indicator in monthly_indicators)

        if is_yearly and not is_monthly:
            monthly_amount = amount / 12
        else:
            monthly_amount = amount

        return int(monthly_amount)
    except (ValueError, TypeError):
        return None
