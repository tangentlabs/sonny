from tangent_importer.infrastructure.context import helpers


def _input_matches_static_values(static_values, _input):
    for key, value in static_values.iteritems():
        if _input[key] != value:
            return False

    return True


def exclude_if_matching_static_values(static_values):
    """
    Only keep rows that don't match all key-value pairs from static_values
    """

    @helpers.step
    def do_exclude_if_matching_static_values(inputs):
        for _input in inputs:
            if not _input_matches_static_values(static_values, _input):
                yield _input

    return do_exclude_if_matching_static_values
