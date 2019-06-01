from mergedb.errors import MdbMergeError
from mergedb.merge_functions.array import array_merge_simple_nodupe


def deep_merge(left, right, knockout=None, list_merge=array_merge_simple_nodupe, array_merge_rules=[]):
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
    return deep_merge_inplace(dict(left),
                              right,
                              knockout=knockout,
                              list_merge=list_merge,
                              array_merge_rules=array_merge_rules)


def deep_merge_inplace(left, right, path=[], knockout=None, list_merge=array_merge_simple_nodupe, array_merge_rules=[]):
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
    knockout_list=[]
    for key in right:
        if key in left:
            if knockout and isinstance(right[key], str):
                if right[key] == knockout:
                    # We can't change the dict size while iterating, so mark knockout keys for deletion after
                    knockout_list.append(key)
            else:
                if isinstance(right[key], dict) and isinstance(left[key], dict):
                    deep_merge_inplace(left[key],
                                       right[key],
                                       path=path + [str(key)],
                                       knockout=knockout,
                                       list_merge=list_merge)
                elif left[key] == right[key]:
                    pass
                elif type(left[key]) is list and type(right[key]) is list:
                    if array_merge_rules:
                        for rule in array_merge_rules:
                            if rule.evaluate(path, key):
                                left[key] = rule.array_merge_function(left[key],
                                                                      right[key],
                                                                      merge_function=rule.sub_merge_function)
                            else:
                                left[key] = list_merge(left[key], right[key])
                    else:
                        left[key] = list_merge(left[key], right[key])
                elif type(left[key]) == type(right[key]):
                    left[key] = right[key]
                else:
                    if key not in knockout_list:
                        raise MdbMergeError(msg=f"Type conflict at {path + [str(key)]}, you cannot deep-merge differing"
                        f" resource types.")
        else:
            left[key] = right[key]
        for knockout_key in knockout_list:
            del left[knockout_key]
    return left


def simple_merge(left, right):
    return simple_merge_inplace(dict(left), right)


def simple_merge_inplace(left, right):
    for key, value in right.items():
        left.update({key: value})
    return left
