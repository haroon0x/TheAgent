def add(a, b):
    """
    Adds two numbers together.
    
    This function takes two numeric inputs and returns their sum.
    
    Args:
        a (numeric): The first number to add.
        b (numeric): The second number to add.
    
    Returns:
        numeric: The sum of the two input numbers.
    
    Raises:
        TypeError: If the inputs are not numeric types.
    
    Examples:
    >>> add(2, 3)
    5
    >>> add(-1, 1)
    0
    """
    return a + b

def greet(name, excited=False):
    """
    Prints a greeting message based on the excitement level.
    
    Prints a simple "Hello" followed by the name unless the excited flag is set to True,
    in which case it prints a more enthusiastic greeting.
    
    Args:
        name (str): The name of the person to greet.
        excited (bool, optional): If True, a more enthusiastic greeting is used. Defaults to False.
    
    Returns:
        str: The greeting message.
    
    Raises:
        None
    
    Examples:
    >>> greet("Alice")
    'Hello, Alice.'
    >>> greet("Bob", excited=True)
    'Hello, Bob!'
    """
    if excited:
        return f"Hello, {name}!"
    return f"Hello, {name}."

def factorial(n):
    """
    Compute the factorial of n.
    
    This function calculates the factorial of a given non-negative integer n using
    a recursive approach. The factorial of a number n is the product of all positive
    integers less than or equal to n.
    
    Args:
        n (int): A non-negative integer whose factorial is to be computed.
    
    Returns:
        int: The factorial of the given integer n.
    
    Raises:
        ValueError: If n is negative.
    
    Note:
        This implementation uses recursion. For large values of n, consider using
        an iterative approach to avoid maximum recursion depth errors.
    """
    if n == 0:
        return 1
    return n * factorial(n - 1)
