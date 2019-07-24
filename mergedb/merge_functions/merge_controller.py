from mergedb.merge_functions.array import *
from mergedb.merge_functions.dict import *
import copy


# class KeyedArrayMergeOptions(object):
#
#     def __init__(self, key, strategy):
#         self.key = key
#         self.strategy = strategy
#
#
class KeyedArrayMergeRule(object):

    def __init__(self, path=[], attribute=None, key='id'):
        self.path = path
        self.key = attribute
        self.item_key = key

    def evaluate(self, path, key):
        results = []
        if self.path:
            if path == self.path:
                results.append(True)
            else:
                results.append(False)
        if self.key:
            if key == self.key:
                results.append(True)
            else:
                results.append(False)
        if not results:
            return False
        # This returns false if any values in the list are false
        return all(results)


class DeepMergeController(object):

    def __init__(self,
                 list_merge_rules=[],
                 knockout='~',
                 default_list_merge_func=array_merge_simple_nodupe):
        self.type = self.deep_merge_inplace
        self.list_merge_rules = list_merge_rules
        self.knockout = knockout
        self.default_list_merge_func = default_list_merge_func

    def merge(self, left, right):
        return self.deep_merge(left, right)

    def deep_merge(self, left, right):
        """
        Calls deep_merge_inplace, but doesn't do the merge inplace.

         :param left:
            left will have its attributes overwritten by right

        :param right:
            right will overwrite the attributes of left

        :param knockout:
            When knockout is specified, a knockout found in the place of a value will delete the key from left

        :param list_merge:
            Provide a function that accepts two arguments(left, right) to do custom list merges

        :return:
            The modified left dict
        """
        left = copy.deepcopy(left)
        return self.deep_merge_inplace(left, right)

    def deep_merge_inplace(self, left, right, path=[]):
        """
        Does a deep-merge of the right dict ONTO the left dict

        :param left:
            left will have its attributes overwritten by right

        :param right:
            right will overwrite the attributes of left

        :param path:
            Used when recursively transiting a dict

        :param knockout:
            When knockout is specified, a knockout found in the place of a value will delete the key from left

        :param list_merge:
            Provide a function that accepts two arguments(left, right) to do custom list merges

        :return:
            The modified left dict
        """
        knockout_list = []
        for key in right:
            if key in left:
                if self.knockout and isinstance(right[key], str) and right[key] == self.knockout:
                    # We can't change the dict size while iterating, so mark knockout keys for deletion after
                    knockout_list.append(key)
                else:
                    if isinstance(right[key], dict) and isinstance(left[key], dict):
                        self.deep_merge_inplace(left[key],
                                           right[key],
                                           path=path + [str(key)])
                    elif left[key] == right[key]:
                        pass
                    elif type(left[key]) is list and type(right[key]) is list:
                        if self.list_merge_rules:
                            matched_rule = None
                            for rule in self.list_merge_rules:
                                if type(rule) is KeyedArrayMergeRule:
                                    if rule.evaluate(path, key):
                                        matched_rule = rule
                                        break
                            if matched_rule:
                                left[key] = self.keyed_array_merge_inplace((left[key]),
                                                                           right[key],
                                                                           matched_rule.item_key)
                            else:
                                left[key] = self.default_list_merge_func(left[key], right[key])
                        else:
                            left[key] = self.default_list_merge_func(left[key], right[key])
                    elif type(left[key]) == type(right[key]):
                        left[key] = right[key]
                    else:
                        if key not in knockout_list:
                            raise MdbMergeError(
                                msg=f"Type conflict at {path + [str(key)]}, you cannot deep-merge differing"
                                f" resource types.")
            else:
                left[key] = right[key]
            for knockout_key in knockout_list:
                del left[knockout_key]
        return left

    def get_merge_function_from_string(self, merge_type):
        if merge_type == 'deep_merge':
            return self.deep_merge_inplace
        if merge_type == 'simple_merge':
            return simple_merge_inplace
        if merge_type == 'array_merge_simple_nodupe':
            return array_merge_simple_nodupe_inplace
        if merge_type == 'keyed_array_merge':
            return keyed_array_merge_inplace

    def keyed_array_merge(self,
                          left: list,
                          right: list,
                          key):
        left = copy.deepcopy(left)
        return keyed_array_merge_inplace(left, right, key=key)

    def keyed_array_merge_inplace(self,
                                  left: list,
                                  right: list,
                                  key):
        for right_item in right:
            left_results = list(filter(lambda x: x[key] == right_item[key], left))
            if left_results.__len__() > 1:
                raise MdbMergeError(msg=f"keyed_array_merge function matched multiple keys when comparing {key} in "
                f"{left}:{right}")
            elif left_results:
                left_item = left_results[0]
            else:
                left_item = None
            if left_item:
                # Index to modify
                index = left.index(left_item)
                new_item = self.deep_merge_inplace(left_item, right_item)
                left[index] = new_item
            else:
                left.append(right_item)
        return left