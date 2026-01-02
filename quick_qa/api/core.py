"""Module that holds api core"""

from __future__ import annotations

from typing import Union

import jsonschema
import requests
from requests import Response, Session


class BaseEndpoint:
    """Class that holds functionality for working with endpoints"""

    _session: Session = Session()  # shared connection pool

    path_url: Union[str, None] = None

    expected_schema: dict = {}
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

    def __init__(self, base_url: str):
        self.base_url = base_url
        if self.path_url is None:
            raise TypeError("no path_url set")
        self.endpoint_url: str = base_url + self.path_url

    def valid_schema(self, response: Response) -> Union[bool, Exception]:
        """Validates the schema

        Args:
            response (Response): enter a Response Object

        Returns:
            bool: errors are thrown if schema is invalidated
            Exception: if validation raises an error the error is caught and passed as a return
        """
        try:
            jsonschema.validate(instance=response.json(), schema=self.expected_schema)
            return True
        except Exception as e:
            return e

    def ping(self) -> bool:
        """runs an options call and checks for 200

        Returns:
            bool: True if 200 status code
        """
        acceptable_status_codes = [200, 204]
        res = requests.options(self.endpoint_url)
        return res.status_code in acceptable_status_codes

    def allowed_methods(self) -> Union[list, None]:
        """returns a list of allowed mehods unless the api.
        returns None if the api does not include the header in the response

        Returns:
            Union[list, None]
        """
        res = requests.options(self.endpoint_url)
        headers = res.headers
        allowed_string = headers.get("Allow")
        if allowed_string:
            return allowed_string.split()
        return None
