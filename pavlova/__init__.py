"Pavlova"

#pylint: disable=no-name-in-module,ungrouped-imports

import datetime
from decimal import Decimal
from enum import Enum
import inspect
import typing
from typing import (
    Any, Dict, Type, TypeVar, Union, Generic, List, Mapping, Optional, Tuple
)
import sys

import dataclasses

from pavlova.base import BasePavlova
from pavlova.parsers import PavlovaParser
import pavlova.parsers


if sys.version_info < (3, 7):
    from typing import GenericMeta as GenericAlias  # type: ignore
else:
    from typing import _GenericAlias as GenericAlias  # type: ignore

T = TypeVar('T')  # pylint: disable=invalid-name


class PavlovaParsingError(Exception):
    """The exception that will be thrown if there is a ValueError or TypeError
    encountered when parsing a mapping."""
    def __init__(self,
                 message: str,
                 original_exception: Exception,
                 path: Tuple[str, ...],
                 expected_type: Type) -> None:
        super().__init__(message)

        self.original_exception = original_exception
        self.path = path
        self.expected_type = expected_type


class Pavlova(BasePavlova):
    "The main Pavlova class that handles parsing dictionaries"

    parsers: Dict[Any, PavlovaParser] = {}

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
            parser_type: Type[Any],
            parser: pavlova.parsers.PavlovaParser,
    ) -> None:
        """Adds a PavlovaParser for a particular type, this is in addition to
        the built in parsers. If you pass in a type that is already handled by
        Pavlova, it will overwrite the built in parser.
        """
        self.parsers[parser_type] = parser

    def from_mapping(self,
                     input_mapping: Mapping[Any, Any],
                     model_class: Type[T],
                     path: Optional[Tuple[str, ...]] = None) -> T:
        """Given a dictionary and a dataclass, return an instance of the
        dataclass"""
        if path is None:
            path = tuple()

        if not dataclasses.is_dataclass(model_class):
            raise TypeError("The root class must be a dataclass")

        data = dict()
        for field in dataclasses.fields(model_class):
            if field.name not in input_mapping:
                # Check if there is a default value set. If there isn't, raise
                # an error, else continue parsing.
                if not hasattr(model_class, field.name):
                    raise PavlovaParsingError(
                        f'Field: {field.name} missing',
                        TypeError(),
                        path + (field.name,),
                        field.type,
                    )
                continue

            try:
                data[field.name] = self.parse_field(
                    input_mapping[field.name],
                    field.type,
                    path + (field.name,),
                )
            except (ValueError, TypeError) as exc:
                raise PavlovaParsingError(
                    str(exc),
                    exc,
                    path + (field.name,),
                    field.type,
                )

        return model_class(**data)  # type: ignore

    def parse_field(self,
                    input_value: Any,
                    field_type: Type,
                    path: Tuple[str, ...]) -> Any:
        # pylint: disable=protected-access

        if field_type in self.parsers:
            return self.parsers[field_type].parse_input(
                input_value, field_type, path
            )

        # If the type is a dataclass, go ahead and call from_mapping
        # recursively.
        if dataclasses.is_dataclass(field_type):
            return self.from_mapping(
                input_value, field_type, path
            )

        # In Python 3.7, some types, such as List, Dict, Union etc show up as
        # type '_GenericAlias'. As such, it is very hacky to track what their
        # types actually are, and what the calling party is intending.
        # In Python 3.6, the types aren't _GenericAlias, but are sometimes
        # GenericMeta, or some weird type that appears to be the same thing,
        # but isn't (Looking at you, Union)
        if field_type.__module__ == 'typing':
            if getattr(field_type, '_name', None):
                base_type = getattr(
                    sys.modules.get(field_type.__module__),
                    field_type._name,
                )
            elif hasattr(field_type, '__origin__'):
                base_type = field_type.__origin__

            return self.parsers[base_type].parse_input(
                input_value, field_type, path
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
                input_value, field_type, path
            )

        raise TypeError(f'Type {field_type} is not supported')
