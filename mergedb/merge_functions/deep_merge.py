from mergedb.errors import MdbMergeError


def deep_merge(left, right, knockout=None):
    """
    Calls deep_merge_inplace, but doesn't do the merge inplace.

    :param left:
        Base Dictionary

    :param right:
        Dictionary to Merge

    :return:
        Merged Dictionary
    """
    return deep_merge_inplace(dict(left), right, knockout=knockout)


def deep_merge_inplace(left, right, path=[], knockout=None):
    """
    Does a deep-merge of the right dict ONTO the left dict
    :param left:
        Base Dictionary

    :param right:
        Dictionary to merge

    :return:
        Merged Dictionary
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
                    deep_merge_inplace(left[key], right[key], path=path + [str(key)], knockout=knockout)
                elif left[key] == right[key]:
                    pass
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
