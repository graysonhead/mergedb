import unittest
from mergedb.merge_functions.dict import deep_merge_inplace, deep_merge
from mergedb.errors import MdbMergeError


class TestDeepMerge(unittest.TestCase):
    """
    Tests the deep_merge function and ensure that it can merge results in nested dicts.
    """
    def test_deep_merge(self):
        # This tests a few different logic paths within the loop at the same time, they probably should
        # eventually be broken out into their own tests
        left = {'outer': {'inner': False, 'identical': True, 'overridden': 1}}
        right = {'outer': {'new_inner': True, 'identical': True, 'overridden': 2}}

        expected_result = {
            'outer': {
                'inner': False,
                'new_inner': True,
                'identical': True,
                'overridden': 2
            }
        }
        result = deep_merge(left, right)
        self.assertEqual(expected_result, result)


class TestDeepMergeTypeCheck(unittest.TestCase):
    """
    Ensures that an error is raised when trying to merge differing types
    """
    def test_deep_merge_type_conflict(self):
        left = {'outer': {'inner': False}}
        right = {'outer': {'inner': "A String"}}
        with self.assertRaises(MdbMergeError):
            result = deep_merge(left, right)


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