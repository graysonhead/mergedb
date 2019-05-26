import unittest
from mergedb.merge_functions.merge_controller import DeepMergeController, KeyedArrayMergeRule
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
        con = DeepMergeController()
        result = con.merge(left, right)
        self.assertEqual(expected_result, result)

    def test_deep_merge_with_list(self):
        left = {'outer': {'list': [1, 2, 3, 4]}}
        right = {'outer': {'list': [2, 3, 4, 5]}}

        expected_result = {
            'outer': {
                'list': [1, 2, 3, 4, 5]
            }
        }
        con = DeepMergeController()
        result = con.merge(left, right)
        self.assertEqual(expected_result, result)

    def test_deep_merge_knockout(self):
        knockout_string = '~'
        left = {'outer': {'inner': False}}
        right = {'outer': {'new_inner': True, 'inner': knockout_string}}

        expected_result = {
            'outer': {
                'new_inner': True
            }
        }
        con = DeepMergeController(knockout=knockout_string)
        result = con.merge(left, right)
        self.assertEqual(expected_result, result)

    def test_deep_merge_knockout_custom_string(self):
        knockout_string = '%%%'
        left = {'outer': {'inner': False}}
        right = {'outer': {'new_inner': True, 'inner': knockout_string}}

        expected_result = {
            'outer': {
                'new_inner': True
            }
        }
        con = DeepMergeController(knockout=knockout_string)
        result = con.merge(left, right)
        self.assertEqual(expected_result, result)

    def test_deep_merge_keyed_array_merge(self):
        left = {
            'outer': {
                'inner_list': [
                    {'key': 1, 'attribute': 'Test'},
                    {'key': 2, 'attribute': 'Test'}
                ],
                'regular_list_merge': [1,2]
            }
        }
        right = {
            'outer': {
                'inner_list': [
                    {'key': 3, 'attribute': 'Test'},
                    {'key': 2, 'attribute': 'Test2'}
                ],
                'regular_list_merge': [2,3]
            }
        }

        expected_result = {
            'outer': {
                'inner_list': [
                    {'key': 1, 'attribute': 'Test'},
                    {'key': 2, 'attribute': 'Test2'},
                    {'key': 3, 'attribute': 'Test'}
                ],
                'regular_list_merge': [1,2,3]
            }
        }

        merge_rules = [
            KeyedArrayMergeRule(
                path=['outer'],
                attribute='inner_list',
                key='key'
            )
        ]
        con = DeepMergeController(list_merge_rules=merge_rules)
        result = con.merge(left, right)
        self.assertEqual(expected_result, result)