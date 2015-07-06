import context


def keep_keys(keys):
    @context.auto_section
    def do_keep_keys(inputs):
        return (
            {
                key: value
                for key, value in inputs.iteritems
                if key in keys
            }
        )

    return do_keep_keys


def dicts_to_tuples(keys):
    @context.auto_section
    def do_dicts_to_tuples(inputs):
        return (
            tuple(
                _input[key]
                for key in keys
            )
            for _input in inputs
        )

    return do_dicts_to_tuples
