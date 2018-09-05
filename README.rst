*****************************************************
pavlova: simplified deserialization using dataclasses
*****************************************************

**pavlova** is a library that assists in mapping an unknown input into a
dataclass.

.. code-block:: python

    from datetime import datetime
    from dataclasses import dataclass

    from pavlova import Pavlova


    @dataclass
    class Input:
        id: int
        name: str
        date: datetime


    Pavlova().from_mapping({
        'id': 10,
        'name': 100
        'date': '2018-08-10',
    }, Input)
    # Input(id=10, name='100', date=datetime.datetime(2018, 8, 10, 0, 0))


Pavlova was born out of frustration with the lack of typing support for
existing deserialization libraries. With the introduction of dataclasses in
Python 3.7, they seemed like the perfect use for defining a deserialization
schema.


Supported functionality
#######################

Parsing of booleans, datetimes, floats, ints, strings, decimals, dictionaries,
enums, lists are currently supported.

There are more parsers to come, however to implement your own custom parser,
simply implement `PavlovaParser` in `pavlova.parsers`, and register it with the
Pavlova object with the `register_parser` method.

Installation
############

.. code-block:: shell

    pip install pavlova

Usage with Flask
################

.. code-block:: python

    from dataclasses import dataclass, asdict

    from flask import Flask, jsonify
    from pavlova.flask import FlaskPavlova

    pavlova = FlaskPavlova()
    app = Flask(__name__)

    @dataclass
    class SampleInput:
        id: int
        name: str

    @app.route('/post', methods=['POST'])
    @pavlova.use(SampleInput)
    def data(data: SampleInput):
        data.id = data.id * len(data.name)
        return jsonify(asdict(data))


    app.run()

Adding Custom Types
###################

There are a couple of different ways to implement new types for parsing in
pavlova. In general, the process is to add a parser a specific type. For
validation you should raise a TypeError or ValueError.

The first one, is creating a new type that extends an existing base type. Here
is an example on how to implement an Email type, which is a string but performs
validation.

.. code-block:: python

    from pavlova import Pavlova
    from pavlova.parsers import GenericParser

    class Email(str):
        def __new__(cls, input_value: typing.Any) -> str:
            if isinstance(input_value, str):
                if '@' in input_value:
                    return str(input_value)
                raise ValueError()
            raise TypeError()

    pavlova = Pavlova()
    pavlova.register_parser(Email, GenericParser(pavlova, Email))

Another way, is to implement your own pavlova parser, rather than using your
the built in `GenericParser` parser.

.. code-block:: python

    import datetime
    from typing import Any, Tuple

    import dateparser
    from pavlova import Pavlova
    from pavlova.parsers import PavlovaParser

    class DatetimeParser(PavlovaParser[datetime.datetime]):
        "Parses a datetime"

        def parse_input(self,
                        input_value: Any,
                        field_type: Type,
                        path: Tuple[str, ...]) -> datetime.datetime:
            return dateparser.parse(input_value)

    pavlova = Pavlova()
    pavlova.register_parser(datetime.DateTime, DatetimeParser(pavlova))

Requirements
############

Pavlova is only supported on Python 3.6 and higher. With Python 3.6, it will
install the `dataclasses <https://github.com/ericvsmith/dataclasses>`__ module.
With Python 3.7 and higher, it will use the built-in dataclasses module.

License
~~~~~~~

GNU LGPLv3. Please see `LICENSE <LICENSE>`__ and
`COPYING.LESSER <COPYING.LESSER>`__.
