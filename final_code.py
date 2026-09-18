def is_palindrome(s):
    """
    Check if a given string is a palindrome, ignoring spaces and case.
    
    Args:
    s (str): The string to check.
    
    Returns:
    bool: True if the string is a palindrome, False otherwise.
    """
    s = s.replace(" ", "").lower()  # Remove spaces and convert to lowercase
    return s == s[::-1]  # Check if the string is equal to its reverse