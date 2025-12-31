import pytest
from pytest_mock.plugin import MockerFixture

from quick_qa.api.core import BaseEndpoint, Method, PreparedRequest, Response


@pytest.fixture
def endpoint_url():
    url = "http://www.demo_url.com/"
    yield url


@pytest.mark.parametrize(
    "payload, expected_body",
    [
        ({"name": "john", "age": 32}, "name=john&age=32"),
        ('{"name":"john","age":32}', b'"{\\"name\\":\\"john\\",\\"age\\":32}"'),
        (None, None),
    ],
)
def test_build_request(payload, expected_body, endpoint_url):
    be = BaseEndpoint(Method.POST, endpoint_url)
    if isinstance(payload, dict):
        pr = be._build_request(data=payload)
    elif isinstance(payload, str):
        pr = be._build_request(json=payload)
    else:
        pr = be._build_request()

    assert isinstance(pr, PreparedRequest)
    assert pr.method == Method.POST.value
    assert pr.url == endpoint_url
    assert pr.body == expected_body


def test_build_request_throws_error(endpoint_url):
    data = {"name": "john", "age": 32}
    json = '{"name":"john","age":32}'
    be = BaseEndpoint(Method.POST, endpoint_url)

    with pytest.raises(ValueError, match="Supply either `data` or `json`, not both"):
        be._build_request(data=data, json=json)


def test_send(mocker: MockerFixture, endpoint_url):
    mock_prepared_request = mocker.Mock(spec=PreparedRequest)
    mock_session = mocker.patch("quick_qa.api.core.BaseEndpoint._session")
    mock_session.send.return_value = Response()

    be = BaseEndpoint(method=Method.GET, url=endpoint_url)
    response = be._send(mock_prepared_request)

    mock_session.send.assert_called_once_with(request=mock_prepared_request)
    assert isinstance(response, Response)


def test_valid_schema(mocker: MockerFixture, endpoint_url):
    mock_jsonschema = mocker.patch("quick_qa.api.core.jsonschema")
    mock_jsonschema.validate.return_value = None
    mock_response = mocker.Mock(spec=Response)

    be = BaseEndpoint(Method.POST, endpoint_url)

    result = be.valid_schema(mock_response)

    mock_jsonschema.validate.assert_called_once_with(
        instance=mock_response.json(), schema=BaseEndpoint.expected_schema
    )
    assert result is True


def test_execute(mocker: MockerFixture, endpoint_url):
    mock_build = mocker.patch.object(BaseEndpoint, "_build_request")
    mock_send = mocker.patch.object(BaseEndpoint, "_send")
    mock_prepared_req = mocker.Mock(spec=PreparedRequest)
    mock_res = mocker.Mock(spec=Response)
    mock_build.return_value = mock_prepared_req
    mock_send.return_value = mock_res

    be = BaseEndpoint(Method.PATCH, endpoint_url)
    res = be.execute(payload={"name": "john", "age": 32})

    mock_build.assert_called_once_with(data={"name": "john", "age": 32})
    mock_send.assert_called_once_with(mock_prepared_req)
    assert res == mock_res
    assert isinstance(res, Response), f"Expected type: Response but got ({type(res)})"
