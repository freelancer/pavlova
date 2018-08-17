"The abstract class for the Pavlova class"

from abc import ABC, abstractmethod
from typing import Any, Dict, Type, TypeVar

T = TypeVar('T')  # pylint: disable=invalid-name


class BasePavlova(ABC):
    "The base pavlova class. Use the pavlova.Pavlova class instead"
    @abstractmethod
    def from_mapping(self,
                     input_mapping: Dict[Any, Any],
                     model_class: Type[T]) -> T:
        "Parse from a Mapping and return a model_class"
        pass

    @abstractmethod
    def parse_field(self, input_value: Any, field_type: Type) -> Any:
        "Parse a particular field with type field_type"
        pass
