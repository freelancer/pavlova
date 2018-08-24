# pylint: disable=missing-docstring

from datetime import datetime
from decimal import Decimal
from enum import Enum, auto
import unittest
from typing import List, Dict, Union, Optional

from pavlova import Pavlova
import pavlova.parsers
from pavlova.parsers import PavlovaParser


class TestBoolParser(unittest.TestCase):
    def test_truthy_string_values(self) -> None:
        parser: PavlovaParser = pavlova.parsers.BoolParser(Pavlova())

        input_values = ('yes', 'true', '1')
        self.assertTrue(all(
            parser.parse_input(v, bool, tuple()) for v in input_values
        ))

    def test_falsy_string_values(self) -> None:
        parser: PavlovaParser = pavlova.parsers.BoolParser(Pavlova())

        input_values = ('no', 'false', '0')
        self.assertFalse(any(
            parser.parse_input(v, bool, tuple()) for v in input_values
        ))

    def test_non_boolean_string_raise_typeerror(self) -> None:
        parser: PavlovaParser = pavlova.parsers.BoolParser(Pavlova())

        with self.assertRaises(TypeError):
            parser.parse_input('aaa', bool, tuple())

    def test_non_string_truthy_values(self) -> None:
        parser: PavlovaParser = pavlova.parsers.BoolParser(Pavlova())

        input_values = (1, True, 1.0)
        self.assertTrue(all(
            parser.parse_input(v, bool, tuple()) for v in input_values
        ))

    def test_non_string_falsy_values(self) -> None:
        parser: PavlovaParser = pavlova.parsers.BoolParser(Pavlova())

        input_values = (0, None, False)
        self.assertFalse(any(
            parser.parse_input(v, bool, tuple()) for v in input_values
        ))


class TestListParser(unittest.TestCase):
    def test_non_list_input_raises_typeerror(self) -> None:
        parser: PavlovaParser = pavlova.parsers.ListParser(Pavlova())

        with self.assertRaises(TypeError):
            parser.parse_input('', List[int], tuple())

    def test_returns_correct_values(self) -> None:
        parser: PavlovaParser = pavlova.parsers.ListParser(Pavlova())
        values = parser.parse_input([0, 1, 2], List[bool], tuple())

        self.assertEqual(values, [False, True, True])

    def test_raises_typeerror_for_different_types(self) -> None:
        parser: PavlovaParser = pavlova.parsers.ListParser(Pavlova())

        with self.assertRaises(TypeError):
            parser.parse_input([0, 1, 'a'], List[bool], tuple())


class TestStringParser(unittest.TestCase):
    def test_returns_string(self) -> None:
        parser: PavlovaParser = pavlova.parsers.StringParser(Pavlova())

        value = parser.parse_input(False, str, tuple())
        self.assertEqual(type(value), str)
        self.assertEqual(value, 'False')


class TestDictParser(unittest.TestCase):
    def test_raises_typeerror_for_different_types(self) -> None:
        parser: PavlovaParser = pavlova.parsers.DictParser(Pavlova())

        with self.assertRaises(TypeError):
            parser.parse_input('', Dict[str, bool], tuple())

    def test_returns_correct_dictionary(self) -> None:
        parser: PavlovaParser = pavlova.parsers.DictParser(Pavlova())

        value = parser.parse_input({1: 'yes'}, Dict[str, bool], tuple())
        self.assertEqual(value, {'1': True})


class TestDatetimeParser(unittest.TestCase):
    def test_parses_datetime(self) -> None:
        parser: PavlovaParser = pavlova.parsers.DatetimeParser(Pavlova())

        value = parser.parse_input(
            '2018-01-02T03:10:11+03:00', datetime, tuple()
        )
        self.assertEqual(value.year, 2018)
        self.assertEqual(value.month, 1)
        self.assertEqual(value.day, 2)
        self.assertEqual(value.hour, 3)
        self.assertEqual(value.minute, 10)
        self.assertEqual(value.second, 11)
        self.assertEqual(value.strftime('%z'), '+0300')


class TestUnionParser(unittest.TestCase):
    def test_raises_typeerror_for_unions(self) -> None:
        parser: PavlovaParser = pavlova.parsers.UnionParser(Pavlova())

        with self.assertRaises(TypeError):
            parser.parse_input('', Union[str], tuple())

        with self.assertRaises(TypeError):
            parser.parse_input('', Union[str, int], tuple())

    def test_returns_correct_values(self) -> None:
        parser: PavlovaParser = pavlova.parsers.UnionParser(Pavlova())

        self.assertEqual(
            parser.parse_input('yes', Optional[bool], tuple()),
            True,
        )


class TestIntParser(unittest.TestCase):
    def test_parses_int(self) -> None:
        parser: PavlovaParser = pavlova.parsers.IntParser(Pavlova())

        self.assertEqual(
            parser.parse_input('10', int, tuple()), 10
        )
        self.assertEqual(
            parser.parse_input(10, int, tuple()), 10
        )
        self.assertEqual(
            parser.parse_input(10.1, int, tuple()), 10
        )
        self.assertEqual(
            parser.parse_input(-10.1, int, tuple()), -10
        )
        self.assertEqual(parser.parse_input('-10', int, tuple()), -10)

    def test_doesnt_parse_string_float(self) -> None:
        parser: PavlovaParser = pavlova.parsers.IntParser(Pavlova())

        with self.assertRaises(Exception):
            self.assertEqual(
                parser.parse_input('10.1', int, tuple()), 10
            )


class TestFloatParser(unittest.TestCase):
    def test_parses_int(self) -> None:
        parser: PavlovaParser = pavlova.parsers.FloatParser(Pavlova())

        self.assertEqual(
            parser.parse_input('10', float, tuple()), 10.0
        )
        self.assertEqual(
            parser.parse_input(10, float, tuple()), 10.0
        )
        self.assertEqual(
            parser.parse_input(10.1, float, tuple()), 10.1
        )
        self.assertEqual(
            parser.parse_input(-10.1, float, tuple()), -10.1
        )
        self.assertEqual(
            parser.parse_input('-10', float, tuple()), -10
        )
        self.assertEqual(
            parser.parse_input('-10.1', float, tuple()), -10.1
        )


class TestDecimalParser(unittest.TestCase):
    def test_parses_int(self) -> None:
        parser: PavlovaParser = pavlova.parsers.DecimalParser(Pavlova())

        self.assertEqual(
            parser.parse_input('10', Decimal, tuple()), Decimal('10')
        )
        self.assertEqual(
            parser.parse_input(10, Decimal, tuple()), Decimal('10.0')
        )
        self.assertTrue(
            Decimal('10') <
            parser.parse_input(10.1, Decimal, tuple()) <
            Decimal('10.2')
        )
        self.assertEqual(
            parser.parse_input('-10', Decimal, tuple()), Decimal('-10')
        )
        self.assertEqual(
            parser.parse_input('-10.1', Decimal, tuple()), Decimal('-10.1')
        )


class SampleEnum(Enum):
    RED = auto()
    GREEN = auto()
    BLUE = auto()


class TestEnumParser(unittest.TestCase):
    def test_parses_string(self) -> None:
        parser: PavlovaParser = pavlova.parsers.EnumParser(Pavlova())

        self.assertEqual(
            parser.parse_input('red', SampleEnum, tuple()), SampleEnum.RED
        )
        self.assertEqual(
            parser.parse_input('RED', SampleEnum, tuple()), SampleEnum.RED
        )
        self.assertEqual(
            parser.parse_input('gReEn', SampleEnum, tuple()), SampleEnum.GREEN
        )

    def test_parses_enum_value(self) -> None:
        parser: PavlovaParser = pavlova.parsers.EnumParser(Pavlova())

        self.assertEqual(
            parser.parse_input(1, SampleEnum, tuple()), SampleEnum.RED
        )
        self.assertEqual(
            parser.parse_input(2, SampleEnum, tuple()), SampleEnum.GREEN
        )
