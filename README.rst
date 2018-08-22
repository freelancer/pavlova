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

Requirements
############

Pavlova is only supported on Python 3.6 and higher. With Python 3.6, it will
install the `dataclasses <https://github.com/ericvsmith/dataclasses>` module.
With Python 3.7 and higher, it will use the built-in dataclasses module.

License
~~~~~~~

GNU LGPLv3. Please see `LICENSE <LICENSE>`__ and
`COPYING.LESSER <COPYING.LESSER>`__.
