#pylint: disable=too-few-public-methods,missing-docstring
#pylint: disable=unused-argument,no-self-use
"This module contains all of the built in parsers for Pavlova"

from abc import ABC, abstractmethod
import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, List, Dict, Union, Type, TypeVar, Generic, Tuple

import dateparser

from pavlova.base import BasePavlova


T = TypeVar('T')  # pylint: disable=invalid-name


class PavlovaParser(Generic[T], ABC):
    "The base pavlova parser for types"

    def __init__(self, pavlova_instance: BasePavlova) -> None:
        self.pavlova = pavlova_instance

    @abstractmethod
    def parse_input(self,
                    input_value: Any,
                    field_type: Type,
                    path: Tuple[str, ...]) -> T:
        "Given an input, return it's typed value"
        pass


class BoolParser(PavlovaParser[bool]):
    "Parses a Boolean"

    def parse_input(self,
                    input_value: Any,
                    field_type: Type,
                    path: Tuple[str, ...]) -> bool:
        if isinstance(input_value, str):
            input_string = input_value.lower()
            if input_string in ('yes', 'true', '1'):
                return True
            if input_string in ('no', 'false', '0'):
                return False

            raise TypeError(f'{input_string} is not a valid boolean value')

        return bool(input_value)


class ListParser(PavlovaParser[List[T]]):
    "Parses a List"

    def parse_input(self,
                    input_value: Any,
                    field_type: Type,
                    path: Tuple[str, ...]) -> List[T]:
        if not isinstance(input_value, list):
            raise TypeError(f'Input value: {input_value} is not a list')

        sub_type = field_type.__args__[0]
        return [
            self.pavlova.parse_field(f, sub_type, path + (f'[{i}]',))
            for i, f in enumerate(input_value)
        ]


class IntParser(PavlovaParser[int]):
    "Parses ints"

    def parse_input(self,
                    input_value: Any,
                    field_type: Type,
                    path: Tuple[str, ...]) -> int:
        return int(input_value)


class FloatParser(PavlovaParser[float]):
    "Parses floats"

    def parse_input(self,
                    input_value: Any,
                    field_type: Type,
                    path: Tuple[str, ...]) -> float:
        return float(input_value)


class DecimalParser(PavlovaParser[Decimal]):
    "Parses floats"

    def parse_input(self,
                    input_value: Any,
                    field_type: Type,
                    path: Tuple[str, ...]) -> Decimal:
        return Decimal(input_value)


class StringParser(PavlovaParser[str]):
    "Parses a String"

    def parse_input(self,
                    input_value: Any,
                    field_type: Type,
                    path: Tuple[str, ...]) -> str:
        return str(input_value)


class DictParser(PavlovaParser[Dict]):
    "Parses a dictionary"

    def parse_input(self,
                    input_value: Any,
                    field_type: Type,
                    path: Tuple[str, ...]) -> Dict:
        'Parses a dictionary into a typed structure'
        if not isinstance(input_value, dict):
            raise TypeError(f'Input value: {input_value} is not a dict')

        key_type = field_type.__args__[0]
        value_type = field_type.__args__[1]
        return {
            self.pavlova.parse_field(k, key_type, path):
            self.pavlova.parse_field(v, value_type, path + (k,))
            for k, v in input_value.items()
        }


class DatetimeParser(PavlovaParser[datetime.datetime]):
    "Parses a datetime"

    def parse_input(self,
                    input_value: Any,
                    field_type: Type,
                    path: Tuple[str, ...]) -> datetime.datetime:
        return dateparser.parse(input_value)


class UnionParser(PavlovaParser[Union[T]]):
    "Parses an Union"

    @staticmethod
    def _is_from_optional(field_type: Type) -> bool:
        if not hasattr(field_type, '__args__'):
            return False

        if len(field_type.__args__) != 2:
            return False

        none_type: Any = type(None)
        if not field_type.__args__[1] is none_type:
            return False

        return True

    def parse_input(self,
                    input_value: Any,
                    field_type: Type,
                    path: Tuple[str, ...]) -> T:
        if not self._is_from_optional(field_type):
            raise TypeError('Unions of this type are not allowed')

        real_field_type = field_type.__args__[0]
        # fast exit when field_type is Optional and input_value is None
        if input_value is None:
            return field_type.__args__[1]()
        return self.pavlova.parse_field(input_value, real_field_type, path)


class EnumParser(PavlovaParser[Enum]):
    "Parses enums"

    def parse_input(self,
                    input_value: Any,
                    field_type: Type,
                    path: Tuple[str, ...]) -> Enum:
        # If the input is a string, try matching it against the names of the
        # enum members. For consistency, we will lower case both values first.
        if isinstance(input_value, str):
            enum_name = input_value.lower()
            enum_values = [
                m for m in field_type if m.name.lower() == enum_name
            ]
            if enum_values:
                return enum_values[0]

        # Try instantiating the enum with our value
        return field_type(input_value)


class GenericParser(PavlovaParser[T]):
    def __init__(self, pavlova: BasePavlova, parser_type: T) -> None:
        super().__init__(pavlova)
        self.parser_type = parser_type

    def parse_input(self,
                    input_value: Any,
                    field_type: Type,
                    path: Tuple[str, ...]) -> T:
        return self.parser_type(input_value)  # type: ignore
