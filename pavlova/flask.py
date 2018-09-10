"Allows you to use Pavlova effortlessly from Flask"

from functools import wraps
from typing import Any, Callable, Dict, Type, TypeVar

import flask

from pavlova import Pavlova


T = TypeVar('T')  # pylint: disable=invalid-name


class FlaskPavlova(Pavlova):
    "The flask adaptor for Pavlova"

    def use(self, model_class: Type[T]) -> Callable:
        """Wraps a flask endpoint, parses the data coming in via json or form
        data, then passes it to the function as an argument.
        """
        def _wrapper(func: Callable) -> Callable:
            @wraps(func)
            def wrap(*args: Any, **kwargs: Dict[Any, Any]) -> Any:
                new_args = list(args)
                new_args.append(self._from_flask_request(model_class))
                return func(*new_args, **kwargs)
            return wrap
        return _wrapper

    def _from_flask_request(self, model_class: Type[T]) -> T:
        json_body: Dict[str, Any] = {}
        if flask.request.is_json:
            json_body = flask.request.get_json()

        return self.from_mapping(
            {
                **json_body,
                **flask.request.values.to_dict()
            },
            model_class
        )
