import unittest
from yax.example import times_two


class TestTimesTwo(unittest.TestCase):
    def test_identities(self):
        self.assertEqual(times_two(0), 0)
        self.assertEqual(times_two(1), 2)

    def test_positive(self):
        self.assertEqual(times_two(123123), 246246)
        self.assertEqual(times_two(5), 10)
        self.assertEqual(times_two(3), 6)

    def test_negative(self):
        self.assertEqual(times_two(-2), -4)
        self.assertEqual(times_two(-444), -888)
        self.assertEqual(times_two(-7), -14)
