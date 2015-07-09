def date_format(_format):
    def do_date_format(_date):
        return _date.strftime(_format)

    return do_date_format


def register_date_format(name):
    """
    Helper decorator to register date formatters
    """
    def decorator(func):
        setattr(date_format, name, func)

        return func

    return decorator


register_date_format("rfc_2822")(date_format("%d %b %Y"))
