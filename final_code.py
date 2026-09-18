def subtract_numbers(a, b, c):
    """
    Subtracts the values of b and c from a, and prints the result.

    Parameters:
    - a (int/float): The first number.
    - b (int/float): The second number to be subtracted from a.
    - c (int/float): The third number to be subtracted from a.

    Returns:
    - None: This function does not return a value.

    Example usage:
    >>> subtract_numbers(10, 5, 2)
    3
    >>> subtract_numbers(20, 10, 10)
    0
    >>> subtract_numbers(-5, 1, 2)
    its a negative
    """
    result = a - b - c
    if result < 0:
        print("its a negative")
    else:
        print(result)