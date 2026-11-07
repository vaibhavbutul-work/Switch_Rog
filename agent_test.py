"""Simple arithmetic helpers and their unit tests."""

import unittest


def add_numbers(a, b):
    """Return the sum of a and b."""
    return a + b


def multiply_numbers(a, b):
    """Return the product of a and b."""
    return a * b


class TestArithmetic(unittest.TestCase):
    def test_add_numbers(self):
        self.assertEqual(add_numbers(2, 3), 5)
        self.assertEqual(add_numbers(-1, 1), 0)
        self.assertEqual(add_numbers(0, 0), 0)

    def test_multiply_numbers(self):
        self.assertEqual(multiply_numbers(2, 3), 6)
        self.assertEqual(multiply_numbers(-2, 3), -6)
        self.assertEqual(multiply_numbers(0, 99), 0)


if __name__ == "__main__":
    unittest.main()
