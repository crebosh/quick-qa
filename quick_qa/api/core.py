"""Module that holds api core"""

from __future__ import annotations

from enum import Enum
from typing import Optional, Union

import jsonschema
import requests
from requests import PreparedRequest, Response, Session


class Method(Enum):
    POST = "POST"
    PATCH = "PATCH"
    UPDATE = "UPDATE"
    GET = "GET"
    DELETE = "DELETE"


class BaseEndpoint:
    """Class that holds functionality for working with endpoints"""

    _session: Session = Session()  # shared connection pool

    expected_schema = {}
    """Schema to compare against results. Overide in Concrete.

    Example:

    {
        "type": "object",
        "required": ["name", "age"],
        "properties": {
            "name": {"type": "string"},
            "age":  {"type": "integer", "minimum": 0}
        },
        "additionalProperties": False   # no extra fields allowed
    } 
    """

    def __init__(self, method: Method, url: str):
        self.method = method
        self.url = url

    def _build_request(
        self, data: Optional[dict] = None, json: Optional[str] = None
    ) -> PreparedRequest:
        if data is not None and json is not None:
            raise ValueError("Supply either `data` or `json`, not both")
        if data:
            req = requests.Request(method=self.method.value, url=self.url, data=data)
        elif json:
            req = requests.Request(method=self.method.value, url=self.url, json=json)
        else:
            req = requests.Request(method=self.method.value, url=self.url)

        prepared = req.prepare()
        return prepared

    def _send(self, prepared_request: PreparedRequest) -> Response:
        respose = self._session.send(request=prepared_request)
        return respose

    def execute(self, payload: Optional[Union[dict, str]] = None) -> Response:
        """executes your api calls\n
           dictionary payloads will use data and string will use json

        Args:
            payload (Optional[Union[dict, str]], optional): . Defaults to None.

        Returns:
            Response: _description_
        """
        match payload:
            case dict():
                prepared_request = self._build_request(data=payload)
            case str():
                prepared_request = self._build_request(json=payload)
            case _:
                prepared_request = self._build_request()

        res = self._send(prepared_request)
        return res

    def valid_schema(self, response: Response):
        """Validates the schema

        Args:
            response (Response): use the output from execute method

        Returns:
            bool: errors are thrown if schema is invalidated
        """
        jsonschema.validate(instance=response.json(), schema=self.expected_schema)
        return True
