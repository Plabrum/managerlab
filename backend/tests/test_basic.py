"""Basic test to ensure pytest works in CI."""

import pytest


def test_basic_functionality():
    """Test basic functionality."""
    assert 1 + 1 == 2


def test_string_operations():
    """Test string operations."""
    result = "hello" + " " + "world"
    assert result == "hello world"


def test_list_operations():
    """Test list operations."""
    test_list = [1, 2, 3]
    test_list.append(4)
    assert len(test_list) == 4
    assert test_list[-1] == 4


@pytest.mark.parametrize("input_val,expected", [(2, 4), (3, 9), (4, 16), (5, 25)])
def test_square_function(input_val, expected):
    """Test square function with parametrized inputs."""

    def square(x):
        return x * x

    assert square(input_val) == expected
