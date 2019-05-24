from mergedb.errors import MdbMergeError
import copy


def array_merge_simple_nodupe(left: list, right:list):
    return array_merge_simple_nodupe_inplace(list(left), right)


def array_merge_simple_nodupe_inplace(left: list, right: list):
    for right_item in right:
        if right_item not in left:
            left.append(right_item)
    return left


def keyed_array_merge(left: list,
                       right:list,
                       key,
                       merge_function=None,
                      knockout=None):
    left = copy.deepcopy(left)
    return keyed_array_merge_inplace(list(left), right, key, merge_function=merge_function, knockout=knockout)


def keyed_array_merge_inplace(left: list,
                       right:list,
                       key,
                       merge_function=None,
                      knockout=None):
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
            merge_function(left_item, right_item, list_merge=array_merge_simple_nodupe_inplace, knockout=knockout)
        else:
            left.append(right_item)
    return left
