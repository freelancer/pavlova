# pylint: disable=missing-docstring

import unittest
from typing import Optional

from flask import Flask
from dataclasses import dataclass

from pavlova.flask import FlaskPavlova


@dataclass
class InputSample:
    id: int


class TestFlaskPavlova(unittest.TestCase):
    input_sample: Optional[InputSample] = None

    def setUp(self) -> None:
        self.app = Flask(__name__)
        self.pavlova = FlaskPavlova()

        @self.pavlova.use(InputSample)
        def index(input_sample: InputSample) -> str:
            self.input_sample = input_sample
            return 'index'

        self.app.route('/', methods=['POST'])(index)

    def test_post_with_json(self) -> None:
        with self.app.test_client() as client:
            client.post('/', json={'id': 10})

        assert self.input_sample is not None
        self.assertTrue(isinstance(self.input_sample, InputSample))
        self.assertEqual(self.input_sample.id, 10)

    def test_post_with_args(self) -> None:
        with self.app.test_client() as client:
            client.post('/?id=10')

        assert self.input_sample is not None
        self.assertTrue(isinstance(self.input_sample, InputSample))
        self.assertEqual(self.input_sample.id, 10)

    def test_post_with_form_data(self) -> None:
        with self.app.test_client() as client:
            client.post('/', data={'id': 10})

        assert self.input_sample is not None
        self.assertTrue(isinstance(self.input_sample, InputSample))
        self.assertEqual(self.input_sample.id, 10)
