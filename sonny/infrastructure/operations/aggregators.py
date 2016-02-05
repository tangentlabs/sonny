from sonny.infrastructure.context import helpers


def multilevel_group_by(levels_columns, flat=False):
    """
    Group by in multiple levels, same as group_by.

    If flat=False, then the
    keys are tuples of the values, if flat=True, then each level has 1 column
    to group by, and the keys are the values themselves

    >>> multilevel_group_by([["a"], ["b"]], flat=True)([{'a': 1, 'b': 2}, {'a': 1, 'b': 3}, {'a': 2, 'b': 4}])
    {1: {2: [{'a': 1, 'b': 2}], 3: [{'a': 1, 'b': 3}]}, 2: {4: [{'a': 2, 'b': 4}]}}
    """
    if flat:
        if any(len(level_columns) != 1 for level_columns in levels_columns):
            raise Exception("Cannot set flat=True with composite keys in "
                            "multilevel_group_by")

    @helpers.step
    def do_multilevel_group_by(data):
        grouped = {}
        for datum in data:
            levels_keys = [
                tuple(datum[column] for column in level_columns)
                for level_columns in levels_columns
            ]
            datum_parent = grouped
            for index, level_key in enumerate(levels_keys, start=1):
                if flat:
                    level_key = level_key[0]
                if index == len(levels_columns):
                    default = []
                else:
                    default = {}
                datum_parent = datum_parent.setdefault(level_key, default)
            datum_parent.append(datum)

        return grouped

    return do_multilevel_group_by


def group_by(columns, flat=False):
    """
    Like multilevel_group_by, but for one level
    """
    return multilevel_group_by([columns], flat=flat)


def ungroup(columns, flat=False):
    """
    Un-do the grouping done by group_by, and also update the rows with the
    grouping key
    """
    if flat:
        if len(columns) != 1:
            raise Exception("Cannot set flat=True with composite keys in "
                            "ungroup")

        column_name = columns[0]

    @helpers.step
    def do_ungroup(grouped):
        for key, data in grouped.iteritems():
            if flat:
                named_key = {column_name: key}
            else:
                named_key = dict(zip(columns, key))
            for datum in data:
                ungrouped = dict(datum)
                ungrouped.update(named_key)
                yield ungrouped

    return do_ungroup
