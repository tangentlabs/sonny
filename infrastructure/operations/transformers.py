import itertools

from infrastructure import context


def keep_keys(keys):
    @context.job_step
    def do_keep_keys(inputs):
        return (
            {
                key: value
                for key, value in _input.iteritems()
                if key in keys
            }
            for _input in inputs
        )

    return do_keep_keys


def dicts_to_tuples(keys):
    @context.job_step
    def do_dicts_to_tuples(inputs):
        return (
            tuple(
                _input[key]
                for key in keys
            )
            for _input in inputs
        )

    return do_dicts_to_tuples


def _maybe_cast_value(maybe_caster, value):
    """
    Cast a value if there is a caster
    """
    if not maybe_caster:
        return value

    return maybe_caster(value)


def cast_dicts_values(keys_casts):
    @context.job_step
    def do_cast_dicts_values(inputs):
        return (
            {
                key: _maybe_cast_value(keys_casts.get(key), value)
                for key, value in _input.iteritems()
            }
            for _input in inputs
        )

    return do_cast_dicts_values


def generic_map(func):
    @context.job_step
    def do_generic_map(inputs):
        return itertools.imap(func, inputs)

    return do_generic_map


def update_with_static_values(static_values):
    static_values_items = static_values.items()

    def update_with_static_values_for_input(_input):
        return dict(_input.items() + static_values_items)

    return generic_map(update_with_static_values_for_input)
