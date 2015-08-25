# -*- coding: utf-8 -*-

from datetime import datetime
import unittest
from ddt import ddt, data, unpack

from infrastructure.facilities import *  # noqa

from infrastructure.operations import casters


@ddt
class TestToDate(unittest.TestCase):
    caster = staticmethod(casters.to_date)

    expected_date = datetime(day=15, month=8, year=2015)

    date_str_a, date_fmt_a = '15-08-2015', '%d-%m-%Y'
    date_str_b, date_fmt_b = '15/08/2015', '%d/%m/%Y'
    date_str_c, date_fmt_c = '15/Aug/2015', '%d/%b/%Y'

    @data(
        # One pattern, correct
        (date_str_a, [date_fmt_a], expected_date),
        (date_str_b, [date_fmt_b], expected_date),
        (date_str_c, [date_fmt_c], expected_date),
        # One pattern, wrong
        (date_str_a, [date_fmt_b], None),
        (date_str_a, [date_fmt_c], None),
        (date_str_b, [date_fmt_a], None),
        (date_str_b, [date_fmt_c], None),
        (date_str_c, [date_fmt_a], None),
        (date_str_c, [date_fmt_b], None),
        # Multiple patterns, correct
        (date_str_a, [date_fmt_a, date_fmt_b, date_fmt_c], expected_date),
        (date_str_b, [date_fmt_a, date_fmt_b, date_fmt_c], expected_date),
        (date_str_c, [date_fmt_a, date_fmt_b, date_fmt_c], expected_date),
        # Multiple patterns, wrong
        (date_str_a, [date_fmt_b, date_fmt_c], None),
        (date_str_b, [date_fmt_a, date_fmt_c], None),
        (date_str_c, [date_fmt_a, date_fmt_b], None),
    )
    @unpack
    def test_transformer_output(self, date_str, date_formats, expected_date):
        caster = self.caster(*date_formats)

        if expected_date is not None:
            result = caster(date_str)

            expected = expected_date.timetuple()
            self.assertEquals(result, expected)
        else:
            with self.assertRaises(ValueError):
                result = caster(date_str)


@ddt
class TestFromGbp(unittest.TestCase):
    caster = staticmethod(casters.from_gbp)

    @data(
        # With pound sign
        (u'£1', 1.),
        (u'1£', 1.),
        (u'£10', 10.),
        (u'£10.32', 10.32),
        (u'£1,000.32', 1000.32),
        (u'£1,000,000.32', 1000000.32),
        # Without pound sign
        (u'1', 1.),
        (u'1', 1.),
        (u'10', 10.),
        (u'10.32', 10.32),
        (u'1,000.32', 1000.32),
        (u'1,000,000.32', 1000000.32),
        # With dollar sign
        (u'$1', None),
        (u'1$', None),
        (u'$10', None),
        (u'$10.32', None),
        (u'$1,000.32', None),
        (u'$1,000,000.32', None),
        # Integer
        (1, 1.),
        (10, 10.),
        # Float
        (1., 1.),
        (10.32, 10.32),
        (1000.32, 1000.32),
        (1000000.32, 1000000.32),
    )
    @unpack
    def test_transformer_output(self, gbp, expected):
        caster = self.caster()

        if expected is not None:
            result = caster(gbp)
            self.assertEquals(result, expected)
        else:
            with self.assertRaises(ValueError):
                result = caster(gbp)


@ddt
class TestFixAccountNumber(unittest.TestCase):
    caster = staticmethod(casters.fix_account_number)

    @data(
        # Unscramblable account numbers
        ('1234567', '1234567'),
        ('1234A67', '1234A67'),
        ('E234A67', 'E234A67'),
        # Unscrabled account numbers
        ('1234E67', '1234E67'),
        # Scrambled account numbers
        ('1.234e+67', '1234E64'),
        ('1.234E+67', '1234E64'),
        # Future scrambled account numbers
        ('1.2345E+78', None),
    )
    @unpack
    def test_transformer_output(self, gbp, expected):
        caster = self.caster

        if expected is not None:
            result = caster(gbp)
            self.assertEquals(result, expected)
        else:
            with self.assertRaises(AssertionError):
                result = caster(gbp)
