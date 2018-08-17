# pylint: disable=missing-docstring

from datetime import datetime
from decimal import Decimal
from enum import Enum, auto
import unittest
from typing import Dict, List, Optional

from dataclasses import dataclass

from pavlova import Pavlova


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
