# -*- coding: utf-8 -*-

import unittest
from ddt import ddt, data, unpack

from tangent_importer.infrastructure.context import helpers
from tangent_importer.infrastructure.facilities import *  # noqa

from tangent_importer.infrastructure.operations import aggregators


@ddt
class TestMultiLevelGroupBy(unittest.TestCase):
    transformer = staticmethod(aggregators.multilevel_group_by)

    FIXTURES = (
        # 1 level
        # Empty input
        ([['a']], False, [], {}),
        # 1 item
        ([['a']], False, [{'a': 1}], {(1,): [{'a': 1}]}),
        # 1 item, flat
        ([['a']], True, [{'a': 1}], {1: [{'a': 1}]}),
        # 2 items, same key
        ([['a']], False, [{'a': 1}, {'a': 1}], {(1,): [{'a': 1}, {'a': 1}]}),
        # 2 items, same key, flat
        ([['a']], True, [{'a': 1}, {'a': 1}], {1: [{'a': 1}, {'a': 1}]}),
        # 2 items, different keys
        ([['a']], False, [{'a': 1}, {'a': 2}], {(1,): [{'a': 1}], (2,): [{'a': 2}]}),
        # 2 levels
        # Empty input
        ([['a'], ['b']], False, [], {}),
        # 1 item
        ([['a'], ['b']], False,
         [{'a': 1, 'b': 1}],
         {(1,): {(1,): [{'a': 1, 'b': 1}]}}),
        # 1 item, flat
        ([['a'], ['b']], True,
         [{'a': 1, 'b': 1}],
         {1: {1: [{'a': 1, 'b': 1}]}}),
        # 2 items, same key
        ([['a'], ['b']], False,
         [{'a': 1, 'b': 1}, {'a': 1, 'b': 1}],
         {(1,): {(1,): [{'a': 1, 'b': 1}, {'a': 1, 'b': 1}]}}),
        # 2 items, same key, flat
        ([['a'], ['b']], True,
         [{'a': 1, 'b': 1}, {'a': 1, 'b': 1}],
         {1: {1: [{'a': 1, 'b': 1}, {'a': 1, 'b': 1}]}}),
        # 2 items, different keys 1st level, flat
        ([['a'], ['b']], True,
         [{'a': 1, 'b': 1}, {'a': 2, 'b': 1}],
         {1: {1: [{'a': 1, 'b': 1}]}, 2: {1: [{'a': 2, 'b': 1}]}}),
        # 2 items, different keys 2nd level, flat
        ([['a'], ['b']], True,
         [{'a': 1, 'b': 1}, {'a': 1, 'b': 2}],
         {1: {1: [{'a': 1, 'b': 1}], 2: [{'a': 1, 'b': 2}]}}),
        # 2 items, different keys both levels, flat
        ([['a'], ['b']], True,
         [{'a': 1, 'b': 1}, {'a': 2, 'b': 2}],
         {1: {1: [{'a': 1, 'b': 1}]}, 2: {2: [{'a': 2, 'b': 2}]}}),
        # 3 levels
        # Different keys on all levels
        ([['a'], ['b'], ['c']], True,
         [{'a': a, 'b': b, 'c': c}
         for a in (1, 2) for b in (1, 2) for c in (1, 2)],
         {
            1: {
                1: {
                    1: [{'a': 1, 'b': 1, 'c': 1}],
                    2: [{'a': 1, 'b': 1, 'c': 2}],
                },
                2: {
                    1: [{'a': 1, 'b': 2, 'c': 1}],
                    2: [{'a': 1, 'b': 2, 'c': 2}],
                },
            },
            2: {
                1: {
                    1: [{'a': 2, 'b': 1, 'c': 1}],
                    2: [{'a': 2, 'b': 1, 'c': 2}],
                },
                2: {
                    1: [{'a': 2, 'b': 2, 'c': 1}],
                    2: [{'a': 2, 'b': 2, 'c': 2}],
                },
            },
        }),

        # Composite keys
        # 1 Level
        ([['a', 'b']], False,
         [{'a': a, 'b': b}
         for a in (1, 2) for b in (1, 2)],
         {
            (1, 1): [{'a': 1, 'b': 1}],
            (1, 2,): [{'a': 1, 'b': 2}],
            (2, 1): [{'a': 2, 'b': 1}],
            (2, 2,): [{'a': 2, 'b': 2}],
        }),
        # 2 Levels
        ([['a', 'b'], ['c', 'd']], False,
         [{'a': a, 'b': b, 'c': c, 'd': d}
         for a in (1, 2) for b in (1, 2)
         for c in (1, 2) for d in (1, 2)],
         {
            (1, 1): {
                (1, 1): [{'a': 1, 'b': 1, 'c': 1, 'd': 1}],
                (2, 1): [{'a': 1, 'b': 1, 'c': 2, 'd': 1}],
                (1, 2): [{'a': 1, 'b': 1, 'c': 1, 'd': 2}],
                (2, 2): [{'a': 1, 'b': 1, 'c': 2, 'd': 2}],
            },
            (2, 1): {
                (1, 1): [{'a': 2, 'b': 1, 'c': 1, 'd': 1}],
                (2, 1): [{'a': 2, 'b': 1, 'c': 2, 'd': 1}],
                (1, 2): [{'a': 2, 'b': 1, 'c': 1, 'd': 2}],
                (2, 2): [{'a': 2, 'b': 1, 'c': 2, 'd': 2}],
            },
            (1, 2): {
                (1, 1): [{'a': 1, 'b': 2, 'c': 1, 'd': 1}],
                (2, 1): [{'a': 1, 'b': 2, 'c': 2, 'd': 1}],
                (1, 2): [{'a': 1, 'b': 2, 'c': 1, 'd': 2}],
                (2, 2): [{'a': 1, 'b': 2, 'c': 2, 'd': 2}],
            },
            (2, 2): {
                (1, 1): [{'a': 2, 'b': 2, 'c': 1, 'd': 1}],
                (2, 1): [{'a': 2, 'b': 2, 'c': 2, 'd': 1}],
                (1, 2): [{'a': 2, 'b': 2, 'c': 1, 'd': 2}],
                (2, 2): [{'a': 2, 'b': 2, 'c': 2, 'd': 2}],
            },
        }),
        # 3 Levels
        ([['a', 'b'], ['c', 'd'], ['e', 'f']], False,
         [{'a': a, 'b': b, 'c': c, 'd': d, 'e': e, 'f': f}
         for a in (1, 2) for b in (1, 2)
         for c in (1, 2) for d in (1, 2)
         for e in (1, 2) for f in (1, 2)],
         {
            (a, b): {
                (c, d): {
                    (e, f): [{'a': a, 'b': b, 'c': c, 'd': d, 'e': e, 'f': f}]
                    for e in (1, 2) for f in (1, 2)
                }
                for c in (1, 2) for d in (1, 2)
            }
            for a in (1, 2) for b in (1, 2)
        }),
    )

    @data(*FIXTURES)
    @unpack
    @helpers.job
    def test_transformer_output(self, columns, flat, inputs, expected, job):
        transformer = self.transformer(columns, flat=flat)
        result = transformer(inputs)

        self.assertEquals(result, expected)


@ddt
class TestUngroup(unittest.TestCase):
    transformer = staticmethod(aggregators.ungroup)

    # The opposite operation of group_by, for 1 level only
    FIXTURES = tuple(
        (columns[0], flat, expected, inputs)
        for columns, flat, inputs, expected
        in TestMultiLevelGroupBy.FIXTURES
        if len(columns) == 1
    )

    @data(*FIXTURES)
    @unpack
    @helpers.job
    def test_transformer_output(self, columns, flat, inputs, expected, job):
        transformer = self.transformer(columns, flat=flat)
        result = transformer(inputs)

        self.assertEquals(sorted(result), sorted(expected))
