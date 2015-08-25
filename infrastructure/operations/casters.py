# -*- coding: utf-8 -*-

import time


def to_date(*date_formats):
    date_formats_str = ', '.join(
        "'%s'" % date_format.replace('%', '%%')
        for date_format in date_formats
    )
    date_formats_value_error = \
        "time data '%%s' does not match any of the formats %s" % date_formats_str

    def do_to_date(value):
        for date_format in date_formats:
            try:
                return time.strptime(value, date_format)
            except ValueError:
                pass

        raise ValueError(date_formats_value_error % value)

    return do_to_date


def from_gbp():
    def do_from_gbp(value):
        if isinstance(value, (str, unicode)):
            value = value.replace(u'£', '')
            value = value.replace(',', '')

        return float(value)

    return do_from_gbp
