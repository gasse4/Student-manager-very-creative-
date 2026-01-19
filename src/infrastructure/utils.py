import os
import re


def is_admin_string_hard(s: str) -> bool:
    """
    Validate admin password/string strength.
    Requirements: at least 12 characters, with uppercase, lowercase, digit, and symbol.
    """
    if len(s) < 12:
        return False
    
    has_upper = re.search(r"[A-Z]", s)
    has_lower = re.search(r"[a-z]", s)
    has_digit = re.search(r"\d", s)
    has_symbol = re.search(r"[^a-zA-Z0-9]", s)
    
    return all([has_upper, has_lower, has_digit, has_symbol])


def clear_screen():
    """Clear the console screen (cross-platform)."""
    os.system('cls' if os.name == 'nt' else 'clear')