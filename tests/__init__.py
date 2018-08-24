# pylint: disable=missing-docstring

from typing import Any


class Email(str):
    def __new__(cls, input_value: Any) -> str:
        if isinstance(input_value, str):
            if '@' in input_value:
                return str(input_value)
            raise ValueError()
        raise TypeError()
