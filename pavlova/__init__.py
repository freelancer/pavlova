"Pavlova"

import datetime
from decimal import Decimal
from enum import Enum
import inspect
import typing
from typing import Any, Dict, Type, TypeVar, Union, Generic, List, Mapping
from typing import _GenericAlias as GenericAlias  # type: ignore
import sys

import dataclasses

from pavlova.base import BasePavlova
from pavlova.parsers import PavlovaParser
import pavlova.parsers

T = TypeVar('T')  # pylint: disable=invalid-name


class Pavlova(BasePavlova):
    "The main Pavlova class that handles parsing dictionaries"

    parsers: Dict[Union[GenericAlias, Type[Any]], PavlovaParser] = {}

    def __init__(self) -> None:
        self.parsers = {
            bool: pavlova.parsers.BoolParser(self),
            datetime.datetime: pavlova.parsers.DatetimeParser(self),
            float: pavlova.parsers.FloatParser(self),
            int: pavlova.parsers.IntParser(self),
            str: pavlova.parsers.StringParser(self),
            Decimal: pavlova.parsers.DecimalParser(self),
            Dict: pavlova.parsers.DictParser(self),
            Enum: pavlova.parsers.EnumParser(self),
            List: pavlova.parsers.ListParser(self),
            Union: pavlova.parsers.UnionParser(self),
        }

    def register_parser(
            self,
            parser_type: Union[GenericAlias, Type[Any]],
            parser: pavlova.parsers.PavlovaParser,
    ) -> None:
        """Adds a PavlovaParser for a particular type, this is in addition to
        the built in parsers. If you pass in a type that is already handled by
        Pavlova, it will overwrite the built in parser.
        """
        self.parsers[parser_type] = parser

    def from_mapping(self,
                     input_mapping: Mapping[Any, Any],
                     model_class: Type[T]) -> T:
        """Given a dictionary and a dataclass, return an instance of the
        dataclass"""
        if not dataclasses.is_dataclass(model_class):
            raise TypeError()

        data = dict()
        for field in dataclasses.fields(model_class):
            if field.name not in input_mapping:
                continue

            data[field.name] = self.parse_field(
                input_mapping[field.name], field.type,
            )

            if field.metadata and 'validator' in field.metadata:
                if not field.metadata['validator'](data[field.name]):
                    raise ValueError(
                        f'{data[field.name]} is not a '
                        f' valid value for {field.type}'
                    )

        return model_class(**data)  # type: ignore

    def parse_field(self, input_value: Any, field_type: Type) -> Any:
        # pylint: disable=protected-access

        if field_type in self.parsers:
            return self.parsers[field_type].parse_input(
                input_value, field_type,
            )

        # If the type is a dataclass, go ahead and call from_mapping
        # recursively.
        if dataclasses.is_dataclass(field_type):
            return self.from_mapping(
                input_value, field_type,
            )

        # Some types, such as List, Dict, Union etc show up as type
        # '_GenericAlias'. As such, it is very hacky to track what their types
        # actually are, and what the calling party is intending.
        if isinstance(field_type, GenericAlias):
            if getattr(field_type, '_name', None):
                base_type = getattr(
                    sys.modules.get(field_type.__module__),
                    field_type._name,
                )
            elif hasattr(field_type, '__origin__'):
                base_type = field_type.__origin__

            return self.parsers[base_type].parse_input(
                input_value, field_type,
            )

        # Check to see if any of the type's parent types is something we can
        # parse. This happens after the generic type checking, as those types
        # do not have a class, and therefore don't have a module resolution
        # order.
        candidate_types = [
            t for t in inspect.getmro(field_type) if t in self.parsers
        ]
        # if there is something we can use, use the most specific type, which
        # will be the first item in the list
        if candidate_types:
            return self.parsers[candidate_types[0]].parse_input(
                input_value, field_type
            )

        raise TypeError(f'Type {field_type} is not supported')
