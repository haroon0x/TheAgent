# Tests for add
def test_add():
    assert add(1, 2) == 3

def test_add_negative_numbers():
    assert add(-1, -1) == -2

def test_add_zero():
    assert add(0, 0) == 0
    assert add(0, 5) == 5
    assert add(5, 0) == 5

def test_add_floats():
    assert abs(add(1.5, 2.5) - 4.0) < 1e-9

def test_add_string():
    with pytest.raises(TypeError):
        add("a", "b")

# Tests for greet
def test_greet_default():
    assert greet("Alice") == "Hello, Alice."

def test_greet_excited():
    assert greet("Bob", excited=True) == "Hello, Bob!"

def test_greet_excited_with_exclamation():
    assert greet("Charlie", excited=True) == "Hello, Charlie!"

def test_greet_empty_string():
    assert greet("") == "Hello, ."

def test_greet_empty_string_excited():
    assert greet("", excited=True) == "Hello, !"

# Tests for factorial
import pytest

def test_factorial_zero():
    assert factorial(0) == 1

def test_factorial_one():
    assert factorial(1) == 1

def test_factorial_positive():
    assert factorial(5) == 120

def test_factorial_negative():
    with pytest.raises(ValueError):
        factorial(-3)

def test_factorial_large_number():
    assert factorial(10) == 3628800

def test_factorial_float():
    with pytest.raises(TypeError):
        factorial(2.5)

