# -*- coding: utf-8 -*-

import time


def to_date(date_format):
    def do_to_date(value):
        return time.strptime(value, date_format)

    return do_to_date


def from_gbp():
    def do_from_gbp(value):
        if isinstance(value, (str, unicode)):
            value = value.replace(u'£', '')

        return float(value)

    return do_from_gbp
