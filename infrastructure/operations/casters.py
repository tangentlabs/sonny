import time


def to_date(date_format):
    def do_to_date(value):
        return time.strptime(value, date_format)

    return do_to_date
