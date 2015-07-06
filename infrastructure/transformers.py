from context import with_new_section
from logging import log_call
from profiling import profile


@with_new_section
@profile
@log_call
def keep_keys(keys):
    def do_keep_keys(inputs):
        return (
            {
                key: value
                for key, value in inputs.iteritems
                if key in keys
            }
        )

    return do_keep_keys


@with_new_section
@profile
@log_call
def keys_to_tuple(keys):
    def do_keys_to_tuple(inputs):
        return (
            tuple(
                _input[key]
                for key in keys
            )
            for _input in inputs
        )

    return do_keys_to_tuple
