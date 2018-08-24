# pylint: disable=missing-docstring

from datetime import datetime
from decimal import Decimal
from enum import Enum, auto
import unittest
from typing import Dict, List, Optional

from dataclasses import dataclass

from pavlova import Pavlova, PavlovaParsingError
from pavlova.parsers import GenericParser
from tests import Email


class SampleEnum(Enum):
    RED = auto()
    GREEN = auto()
    BLUE = auto()

@dataclass
class NestedSample:
    key: str

@dataclass
class Sample:
    enabled: bool
    date: datetime
    portion: float
    count: int
    name: str
    price: Decimal
    data: Dict[str, str]
    color: SampleEnum
    locations: List[str]
    country: Optional[str]
    nested: Optional[NestedSample] = None


@dataclass
class SimpleSample:
    value: List[int]
    test: Optional[str] = None


class TestPavlova(unittest.TestCase):
    def test_parses_dataclass(self) -> None:
        pavlova = Pavlova()
        parsed = pavlova.from_mapping({
            'enabled': False,
            'date': '2018-01-01',
            'portion': 0.1,
            'count': 10,
            'name': 'Bob',
            'price': '10.01',
            'data': {'extra': 'args'},
            'color': 'red',
            'locations': ['Sydney', 'Melbourne'],
            'country': 'Australia',
        }, Sample)

        self.assertTrue(isinstance(parsed, Sample))
        self.assertEqual(parsed.enabled, False)
        self.assertEqual(parsed.date, datetime(year=2018, month=1, day=1))
        self.assertTrue(0.09 < parsed.portion < 0.11)
        self.assertEqual(parsed.count, 10)
        self.assertEqual(parsed.name, 'Bob')
        self.assertEqual(parsed.price, Decimal('10.01'))
        self.assertEqual(parsed.data, {'extra': 'args'})
        self.assertEqual(parsed.color, SampleEnum.RED)
        self.assertEqual(parsed.locations, ['Sydney', 'Melbourne'])
        self.assertEqual(parsed.country, 'Australia')
        self.assertTrue(parsed.nested is None)

    def test_nested_parsing(self) -> None:
        @dataclass
        class Nested:
            nested: NestedSample

        pavlova = Pavlova()
        parsed = pavlova.from_mapping({'nested': {'key': 'locked'}}, Nested)

        self.assertTrue(isinstance(parsed, Nested))
        self.assertTrue(isinstance(parsed.nested, NestedSample))
        self.assertEqual(parsed.nested.key, 'locked')

    def test_value_error_causes_error(self) -> None:
        pavlova = Pavlova()
        with self.assertRaises(PavlovaParsingError) as raised:
            pavlova.from_mapping({
                'value': ['bob'],
            }, SimpleSample)

        exc = raised.exception
        self.assertTrue(isinstance(exc.original_exception, ValueError))
        self.assertEqual(exc.path, ('value',))

    def test_type_error_causes_error(self) -> None:
        pavlova = Pavlova()
        with self.assertRaises(PavlovaParsingError) as raised:
            pavlova.from_mapping({
                'value': 'bob',
            }, SimpleSample)

        exc = raised.exception
        self.assertTrue(isinstance(exc.original_exception, TypeError))
        self.assertEqual(exc.path, ('value',))

    def test_missing_value_causes_error(self) -> None:
        pavlova = Pavlova()
        with self.assertRaises(PavlovaParsingError) as raised:
            pavlova.from_mapping({}, SimpleSample)

        exc = raised.exception
        self.assertTrue(isinstance(exc.original_exception, TypeError))
        self.assertEqual(exc.path, ('value',))

    def test_with_generic_parser(self) -> None:
        @dataclass
        class Example:
            email: Email

        pavlova = Pavlova()
        pavlova.register_parser(Email, GenericParser(pavlova, Email))
        pavlova.from_mapping({'email': 'chris@chris.com'}, Example)

        with self.assertRaises(PavlovaParsingError):
            pavlova.from_mapping({'email': 'chris'}, Example)

        with self.assertRaises(PavlovaParsingError):
            pavlova.from_mapping({'email': 123}, Example)
