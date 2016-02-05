import itertools

from sonny.infrastructure.context import helpers


def keep_keys(keys):
    """
    Do a filter on columns
    """

    @helpers.step
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
    """
    Convert dicts to tuples, using a key ordering. Potentionally doing a filter
    on columns, if not all dict keys are in the `keys`
    """

    @helpers.step
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
    Cast a value if there is a caster, else return the value
    """
    if not maybe_caster:
        return value

    return maybe_caster(value)


def cast_dicts_values(keys_casts):
    """
    Cast (some of) the dict's values, using a dictionary of casters
    """

    @helpers.step
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
    """
    A generic mapper using a function that operates on rows
    """

    @helpers.step
    def do_generic_map(inputs):
        return itertools.imap(func, inputs)

    return do_generic_map


def update_with_static_values(static_values):
    """
    Update ech dict with static values

    >>> list(update_with_static_values({'a':1, 'b':2})([{'a':3, 'c':4}, {}]))
    [{'a': 1, 'b':2, 'c':4}]
    """

    static_values_items = static_values.items()

    def update_with_static_values_for_input(_input):
        return dict(_input.items() + static_values_items)

    return generic_map(update_with_static_values_for_input)


def update_with_dynamic_values(dynamic_values):
    """
    Update ech dict with dynamic values, using functions
    >>> list(update_with_dynamic_values({'a': lambda _input: _input['b'] or 5})
        ([{'b':2, 'c': 3}, {'a':1}]))
    [{'a': 2, 'b':2, 'c': 3}, {'a': 5}]
    """

    dynamic_values_items = dynamic_values.items()

    def update_with_static_values_for_input(_input):
        updated = dict(_input)
        updated.update({
            key: func(_input)
            for key, func in dynamic_values_items
        })

        return updated

    return generic_map(update_with_static_values_for_input)


def generator_to_tuples():
    """
    Consume a generator into a tuple
    >>> generator_to_tuples(xrange(5))
    tuple(xrange(5))
    """

    @helpers.step
    def do_generator_to_tuples(inputs):
        return tuple(inputs)

    return do_generator_to_tuples
