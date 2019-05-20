def simple_merge(left, right):
    return simple_merge_inplace(dict(left), right)


def simple_merge_inplace(left, right):
    for key, value in right.items():
        left.update({key: value})
    return left
