# -*- coding: utf-8 -*-

import unittest
from ddt import ddt, data, unpack

from infrastructure import context
from infrastructure.facilities import *  # noqa

from infrastructure.operations.transformers import keep_keys, dicts_to_tuples


@ddt
class TestKeepKeys(unittest.TestCase):
    transformer = staticmethod(keep_keys)

    @data(
        # No input
        (['a', 'b'], [], []),
        # Empty keys and input
        ([], [{}], [{}]),
        # Empty keys
        ([], [{'a': 'b'}], [{}]),
        # Empty input
        (['a', 'b'], [{}], [{}]),
        # Same keys
        (['a', 'b'], [{'a': 1, 'b': 2}], [{'a': 1, 'b': 2}]),
        # More keys
        (['a', 'b', 'c'], [{'a': 1, 'b': 2}], [{'a': 1, 'b': 2}]),
        # Less keys
        (['a'], [{'a': 1, 'b': 2}], [{'a': 1}]),
        # Less and more keys
        (['a', 'c'], [{'a': 1, 'b': 2}], [{'a': 1}]),
        # Less and more keys, heterogenous
        (['a', 'c'], [{'a': 1, 'b': 2}, {'b': 3, 'c': 4}, {'a': 5, 'c': 6}, {'d': 7}], [{'a': 1}, {'c': 4}, {'a': 5, 'c': 6}, {}]),
    )
    @unpack
    @context.create_for_job
    def test_transformer_output(self, keys, inputs, expected):
        transformer = self.transformer(keys)
        result = list(transformer(inputs))

        self.assertEquals(result, expected)


@ddt
class TestDictsToTuples(unittest.TestCase):
    transformer = staticmethod(dicts_to_tuples)

    @data(
        # No input
        (['a', 'b'], [], [], None),
        # Empty keys and input
        ([], [{}], [tuple()], None),
        # Empty keys
        ([], [{'a': 'b'}], [tuple()], None),
        # Empty input
        (['a', 'b'], [{}], None, (KeyError,)),
        # Same keys
        (['a', 'b'], [{'a': 1, 'b': 2}], [(1, 2)], None),
        # More keys
        (['a', 'b', 'c'], [{'a': 1, 'b': 2}], None, (KeyError,)),
        # Less keys
        (['a'], [{'a': 1, 'b': 2}], [(1,)], None),
        # Less and more keys
        (['a', 'c'], [{'a': 1, 'b': 2}], None, (KeyError,)),
        # Less and more keys, heterogenous
        (['a', 'c'], [
            {'a': 1, 'b': 2},
            {'b': 3, 'c': 4},
            {'a': 5, 'c': 6},
            {'d': 7}
        ], None, (KeyError,)),
    )
    @unpack
    @context.create_for_job
    def test_transformer_output(self, keys, inputs, expected, raises):
        transformer = self.transformer(keys)

        if raises:
            with self.assertRaises(*raises):
                list(transformer(inputs))
        else:
            result = list(transformer(inputs))
            self.assertEquals(result, expected)
