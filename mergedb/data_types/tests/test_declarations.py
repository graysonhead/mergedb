import unittest
from mergedb.data_types.declaration import Declaration


class TestDeclarationInheritance(unittest.TestCase):
    """
    Test the declaration class with a deep_merge style configuration
    """
    def test_dec_deep_merge(self):
        layer1 = {'outer_option': {'inner_option': True}}
        base_layer = {'mergedb': {'merge_type': 'deep_merge'}, 'outer_option': {'inner_option': False}}
        l1 = Declaration('layer1', layer1)
        base = Declaration('base', base_layer, inherited_declarations=[l1])
        result = base.merge_inherited()

        expected_result = {'outer_option': {'inner_option': False}}
        self.assertEqual(expected_result, result)

    def test_3_layer_deep_merge(self):
        layer1 = {'outer': 1}
        layer2 = {'outer': 3}
        base_layer = {'mergedb': {'merge_type': 'deep_merge'}}
        l1 = Declaration('layer1', layer1)
        l2 = Declaration('layer2', layer2)
        base = Declaration('base', base_layer, inherited_declarations=[l1, l2])
        result = base.merge_inherited()

        expected_result = {'outer': 3}
        self.assertEqual(expected_result, result)


class TestDeclarationKnockout(unittest.TestCase):
    """
    Ensure knockouts work when you want them to, and don't when you don't
    """
    def test_knockout_merge_default_string(self):
        layer1 = {'outer': {'inner': True}}
        base_layer = {
            'mergedb':
                          {
                              'merge_type': 'deep_merge',
                              'knockout': '~',
                          },
            'outer': '~'
                      }
        l1 = Declaration('layer1', layer1)
        base = Declaration('base', base_layer, inherited_declarations=[l1])
        result = base.merge_inherited()

        expected_result = {}
        self.assertEqual(expected_result, result)