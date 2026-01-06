from typing import Optional

import requests
from requests import Response

from quick_qa.api.core import BaseEndpoint


class BaseEndpointContainer:
    """Base class for holding info every endpoint should share"""

    def __init__(self, base_endpoint: BaseEndpoint):
        self.endpoint_url = base_endpoint.endpoint_url


class Get(BaseEndpointContainer):
    def get(self, params: Optional[dict] = None) -> Response:
        """returns a get request response

        Args:
            params (Optional[dict], optional): Defaults to None.

        Returns:
            Response:
        """
        res = requests.get(url=self.endpoint_url, params=params)
        return res


class Post(BaseEndpointContainer):
    def post(self, data: Optional[dict] = None, json: Optional[str] = None) -> Response:
        """returns a post request response

        Args:
            data (Optional[dict], optional): Defaults to None.
            json (Optional[str], optional): Defaults to None.

        Returns:
            Response:
        """
        res = requests.post(url=self.endpoint_url, data=data, json=json)
        return res


class Put(BaseEndpointContainer):
    def put(self, data: Optional[dict] = None, json: Optional[str] = None) -> Response:
        """returns a put request response

        Args:
            data (Optional[dict], optional): Defaults to None.
            json (Optional[str], optional): Defaults to None.

        Returns:
            Response:
        """
        res = requests.put(url=self.endpoint_url, data=data, json=json)
        return res


class Delete(BaseEndpointContainer):
    def delete(self, data: Optional[dict] = None) -> Response:
        """returns a delete request response

        Args:
            data (Optional[dict], optional): Defaults to None.

        Returns:
            Response:
        """
        res = requests.delete(url=self.endpoint_url, data=data)
        return res
