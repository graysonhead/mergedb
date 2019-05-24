import unittest
from mergedb.merge_functions.dict import simple_merge_inplace, simple_merge


class TestSimpleMerge(unittest.TestCase):
    """
    Tests the simple merge function
    """
    def test_simple_merge(self):
        left = {'one': 1}
        right = {'two': 2}

        expected_result = {
            'one': 1,
            'two': 2
        }
        result = simple_merge(left, right)
        self.assertEqual(expected_result, result)