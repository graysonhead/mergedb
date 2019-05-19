import unittest
from mergedb.merge_functions import deep_merge_inplace, deep_merge


class TestDeepMerge(unittest.TestCase):
    """
    Tests the deep_merge function and ensure that it can merge results in nested dicts.
    """
    def test_deep_merge(self):
        left = {'outer': {'inner': False}}
        right = {'outer': {'new_inner': True}}

        expected_result = {
            'outer': {
                'inner': False,
                'new_inner': True
            }
        }
        result = deep_merge(left, right)
        self.assertEqual(expected_result, result)


class TestDeepMergeKnockout(unittest.TestCase):
    """
    Test the deep_merge function and ensure that it can merge results while also removing keys with a knockout prefix.
    """
    def test_deep_merge_knockout(self):
        knockout_string = '~'
        left = {'outer': {'inner': False}}
        right = {'outer': {'new_inner': True, 'inner': knockout_string}}

        expected_result = {
            'outer': {
                'new_inner': True
            }
        }
        result = deep_merge(left, right, knockout=knockout_string)
        self.assertEqual(expected_result, result)