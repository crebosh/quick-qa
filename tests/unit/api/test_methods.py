import pytest
from pytest_mock.plugin import MockerFixture
from requests import Response

from quick_qa.api.core import BaseEndpoint
from quick_qa.api.methods import Delete, Get, Post, Put


@pytest.fixture
def base_endpoint_obj():
    BaseEndpoint.path_url = "/mypath"
    be = BaseEndpoint("http://www.myurl.com")
    yield be
    BaseEndpoint.path_url = None


@pytest.fixture
def get_obj(base_endpoint_obj):
    get = Get(base_endpoint_obj)
    yield get


@pytest.fixture
def post_obj(base_endpoint_obj):
    post = Post(base_endpoint_obj)
    yield post


@pytest.fixture
def mock_requests(mocker: MockerFixture):
    mr = mocker.patch("quick_qa.api.methods.requests")
    yield mr


@pytest.fixture
def mock_response(mocker: MockerFixture):
    mr = mocker.Mock(spec=Response)
    yield mr


class TestGet:
    def test_get_init(self, base_endpoint_obj):
        get = Get(base_endpoint_obj)

        assert get.endpoint_url == base_endpoint_obj.endpoint_url

    @pytest.mark.parametrize(
        "params", [(None), ({"email": "e@mail.com", "name": "myname"})]
    )
    def test_get(self, params, get_obj: Get, mock_requests, mock_response):
        mock_requests.get.return_value = mock_response

        res = get_obj.get(params)

        mock_requests.get.assert_called_once_with(
            url=get_obj.endpoint_url, params=params
        )
        assert res == mock_response


class TestPost:
    def test_post_init(self, base_endpoint_obj):
        post = Post(base_endpoint_obj)

        assert post.endpoint_url == base_endpoint_obj.endpoint_url

    def test_post(self, post_obj: Post, mock_requests, mock_response):
        mock_requests.post.return_value = mock_response

        res = post_obj.post(data={}, json="")

        mock_requests.post.assert_called_once_with(
            url=post_obj.endpoint_url, data={}, json=""
        )
        assert res == mock_response


class TestPut:
    def test_put_init(self, base_endpoint_obj):
        put = Put(base_endpoint_obj)

        assert put.endpoint_url == base_endpoint_obj.endpoint_url

    def test_put(self, base_endpoint_obj, mock_requests, mock_response):
        mock_requests.put.return_value = mock_response
        put = Put(base_endpoint_obj)

        res = put.put(data={}, json="")

        mock_requests.put.assert_called_once_with(
            url=put.endpoint_url, data={}, json=""
        )
        assert res == mock_response


class TestDelete:
    def test_delete_init(self, base_endpoint_obj):
        delete = Delete(base_endpoint_obj)

        assert delete.endpoint_url == base_endpoint_obj.endpoint_url

    def test_delete(self, base_endpoint_obj, mock_requests, mock_response):
        mock_requests.delete.return_value = mock_response
        delete = Delete(base_endpoint_obj)

        res = delete.delete(data={})

        mock_requests.delete.assert_called_once_with(url=delete.endpoint_url, data={})
        assert res == mock_response
