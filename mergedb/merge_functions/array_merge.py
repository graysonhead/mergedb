def array_merge_simple_nodupe(left: list, right:list):
    return array_merge_simple_nodupe_inplace(list(left), right)


def array_merge_simple_nodupe_inplace(left: list, right: list):
    for right_item in right:
        if right_item not in left:
            left.append(right_item)
    return left