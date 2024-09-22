def string_prefix(a, b):
    return a.upper().startswith(b.upper())

import re

def custom_split(s):
    # Check if the string starts with a quote (single or double)
    if s.startswith('"') or s.startswith("'"):
        # Determine which type of quote we're dealing with
        quote = s[0]
        # Find the position of the closing quote
        end_quote = s.find(quote, 1)
        
        if end_quote != -1:
            # If we found a closing quote:
            # Return the content between quotes (excluding the quotes themselves)
            # and the rest of the string (stripped of leading/trailing whitespace)
            return s[1:end_quote], s[end_quote+1:].strip()
        else:
            # If no closing quote is found:
            # Return the whole string without the opening quote, and an empty string
            return s[1:], ""
    else:
        # For strings not starting with a quote:
        # Use regex to find the first whitespace character
        match = re.search(r'\s', s)
        if match:
            # If whitespace is found:
            # Split at the first occurrence of whitespace
            # Return everything before the whitespace, and everything after (stripped)
            return s[:match.start()], s[match.end():].strip()
        else:
            # If no whitespace is found:
            # Return the whole string and an empty string
            return s, ""

def test_custom_split():
# Test cases
    test_cases = [
        'test "123"',
        '"test 123" 456',
        "'test",
        "regular string with spaces",
        "single_word"
    ]

    # Run test cases
    for case in test_cases:
        result = custom_split(case)
        print(f"Input: {case}")
        print(f"Output: {result}")
        print()

def is_whole_number(value):
    if isinstance(value, str):
        return bool(re.match(r'^\-?[0-9]+$', value))
    return False