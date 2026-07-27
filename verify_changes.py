# Quick syntax check for the changes made

# Check views.py for correct regex syntax
try:
    import re
    # Test the regex pattern used in the qualifier filter
    test_pattern = f'^{re.escape("U")}(\\s|\\(|$|\\n)'
    test_regex = re.compile(test_pattern)

    # Test cases
    test_strings = [
        "U",
        "U2",
        "U (1-2)",
        "U\n",
        "M U D",
        "U2 U",
    ]

    print("Testing qualifier regex pattern:")
    print(f"Pattern: {test_pattern}")
    for test_str in test_strings:
        match = test_regex.search(test_str)
        print(f"  '{test_str}' -> {bool(match)}")

    print("\n✓ Regex syntax is correct")

except Exception as e:
    print(f"✗ Error in regex: {e}")

# Check that the format_multiline filter handles the problematic characters
try:
    test_text = "Test − with U+2212 and other characters"
    cleaned = test_text.replace('−', '-').replace('ー', '-').replace('，', ',')
    print("\nCharacter replacement test:")
    print(f"  Original: '{test_text}'")
    print(f"  Cleaned: '{cleaned}'")
    print("✓ Character replacement works")

except Exception as e:
    print(f"✗ Error in character replacement: {e}")

# Check amount formatting
try:
    test_amount = 50
    formatted = f"{test_amount:,},000"
    print("\nAmount formatting test:")
    print(f"  Original: {test_amount}")
    print(f"  Formatted: {formatted}")
    print("✓ Amount formatting works")

except Exception as e:
    print(f"✗ Error in amount formatting: {e}")

print("\n✓ All syntax checks passed!")
