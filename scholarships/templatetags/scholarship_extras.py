from django import template
from django.utils.safestring import mark_safe

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
    """Format multiline text for display"""
    if not text:
        return ""
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

@register.simple_tag
def get_qualifier_choices():
    """Get all available qualifier choices"""
    return QUALIFIER_MAPPING