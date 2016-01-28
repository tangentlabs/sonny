# -*- coding: utf-8 -*-

import unittest
from ddt import ddt, data, unpack

from infrastructure.context import helpers
from infrastructure.facilities import *  # noqa

from infrastructure.operations import transformers


@ddt
class TestKeepKeys(unittest.TestCase):
    transformer = staticmethod(transformers.keep_keys)

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
    @helpers.job
    def test_transformer_output(self, keys, inputs, expected, job):
        transformer = self.transformer(keys)
        result = list(transformer(inputs))

        self.assertEquals(result, expected)


@ddt
class TestDictsToTuples(unittest.TestCase):
    transformer = staticmethod(transformers.dicts_to_tuples)

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
    @helpers.job
    def test_transformer_output(self, keys, inputs, expected, raises, job):
        transformer = self.transformer(keys)

        if raises:
            with self.assertRaises(*raises):
                list(transformer(inputs))
        else:
            result = list(transformer(inputs))
            self.assertEquals(result, expected)


@ddt
class TestCastDictValues(unittest.TestCase):
    transformer = staticmethod(transformers.cast_dicts_values)

    doubler = lambda x: 2 * x

    @data(
        # No input
        ({'a': doubler}, [], []),
        # Empty keys and input
        ({}, [{}], [{}]),
        # Empty keys
        ({}, [{'a': 'b'}], [{'a': 'b'}]),
        # Empty input
        ({'a': doubler}, [{}], [{}]),
        # Same keys
        ({'a': doubler, 'b': doubler}, [{'a': 1, 'b': 2}], [{'a': 2, 'b': 4}]),
        # More keys
        ({'a': doubler, 'b': doubler}, [{'a': 1}], [{'a': 2}]),
        # Less keys
        ({'a': doubler}, [{'a': 1, 'b': 2}], [{'a': 2, 'b': 2}]),
        # Less and more keys
        ({'a': doubler, 'c': doubler}, [{'a': 1, 'b': 2}], [{'a': 2, 'b': 2}]),
        # Less and more keys, heterogenous
        ({'a': doubler, 'c': doubler}, [
            {'a': 1, 'b': 2},
            {'b': 3, 'c': 4},
            {'a': 5, 'c': 6},
            {'d': 7}
        ], [
            {'a': 2, 'b': 2},
            {'b': 3, 'c': 8},
            {'a': 10, 'c': 12},
            {'d': 7}
        ]),
    )
    @unpack
    @helpers.job
    def test_transformer_output(self, casts, inputs, expected, job):
        transformer = self.transformer(casts)

        result = list(transformer(inputs))
        self.assertEquals(result, expected)


@ddt
class TestGenericMap(unittest.TestCase):
    transformer = staticmethod(transformers.generic_map)

    nuller = lambda x: None

    @data(
        # No input
        (nuller, [], []),
        # Keys
        (nuller, [{'a': 1}, {'b': 2}], [None, None]),
        # Tuples
        (nuller, [(1, 2), (3, 4)], [None, None]),
    )
    @unpack
    @helpers.job
    def test_transformer_output(self, casts, inputs, expected, job):
        transformer = self.transformer(casts)

        result = list(transformer(inputs))
        self.assertEquals(result, expected)


@ddt
class TestUpdateWithStaticValues(unittest.TestCase):
    transformer = staticmethod(transformers.update_with_static_values)

    static_values = {'a': 1, 'b': 2}

    @data(
        # No input
        (static_values, [], []),
        # Less keys
        (static_values, [{'a': 3}, {'b': 4}], [{'a': 1, 'b': 2}, {'a': 1, 'b': 2}]),
        # Same keys
        (static_values, [{'a': 3, 'b': 4}], [{'a': 1, 'b': 2}]),
        # More keys
        (static_values, [{'a': 3, 'b': 4, 'c': 5}], [{'a': 1, 'b': 2, 'c': 5}]),
        # Less and more keys
        (static_values, [{'a': 3, 'c': 5}], [{'a': 1, 'b': 2, 'c': 5}]),
    )
    @unpack
    @helpers.job
    def test_transformer_output(self, casts, inputs, expected, job):
        transformer = self.transformer(casts)

        result = list(transformer(inputs))
        self.assertEquals(result, expected)


@ddt
class TestUpdateWithDynamicValues(unittest.TestCase):
    transformer = staticmethod(transformers.update_with_dynamic_values)

    dynamic_values = {'a': lambda x: x.get('a', 1), 'b': lambda x: 2}

    @data(
        # No input
        (dynamic_values, [], []),
        # Less keys
        (dynamic_values, [{'a': 3}, {'b': 4}], [{'a': 3, 'b': 2}, {'a': 1, 'b': 2}]),
        # Same keys
        (dynamic_values, [{'a': 3, 'b': 4}], [{'a': 3, 'b': 2}]),
        # More keys
        (dynamic_values, [{'a': 3, 'b': 4, 'c': 5}], [{'a': 3, 'b': 2, 'c': 5}]),
        # Less and more keys
        (dynamic_values, [{'a': 3, 'c': 5}], [{'a': 3, 'b': 2, 'c': 5}]),
    )
    @unpack
    @helpers.job
    def test_transformer_output(self, casts, inputs, expected, job):
        transformer = self.transformer(casts)

        result = list(transformer(inputs))
        self.assertEquals(result, expected)
