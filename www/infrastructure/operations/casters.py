# -*- coding: utf-8 -*-

import time
import math


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


def from_date(date_format):
    def do_from_date(_date):
        return _date.strftime(date_format)

    return do_from_date


def cast_if_not_none(func):
     def do_cast_if_not_none(arg):
         if not arg:
            return arg
         return func(arg)

     return do_cast_if_not_none

def none_if_not_isinstance(*types):
    def do_none_if_not_isinstance(value):
        if not isinstance(value, types):
            return None
        return value
    return do_none_if_not_isinstance

def from_gbp(value):
    if isinstance(value, (str, unicode)):
        value = value.replace(u'£', '')
        value = value.replace(',', '')

    return float(value)


def fix_account_number(value):
    """
    Fix account numbers which have converted to 'E-Notation'. This happens when
    Excel sees a number like 3142E24 and assumes it's a number in scientific
    notation. It renders them as 3.142e+27.

    To revert them, we multiply the  first bit by a thousand, capitalise the
    'e', remove the '+' and subtract 3 from the last bit.
    """

    if 'e+' not in value.lower():
        return value

    base, exponent = value.lower().split('e+')

    first_part = float(base) * 1000
    second_part = int(exponent) - 3

    assert math.floor(first_part) == first_part, \
        "Scientic notation account number was not originally 7 digits long"
    assert second_part >= 10, \
        "Scientic notation account number was not originally 7 digits long"

    fixed = '%.0fE%s' % (first_part, second_part)
    return fixed
