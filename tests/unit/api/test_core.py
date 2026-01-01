import pytest
from pytest_mock.plugin import MockerFixture

from quick_qa.api.core import BaseEndpoint, PreparedRequest, Response, Session


@pytest.fixture
def base_url():
    url = "http://www.myvaseurl.com"
    yield url


@pytest.fixture
def base_endpoint(base_url):
    be = BaseEndpoint(base_url)
    yield be


def test_base_endpoint_class(base_url):
    be = BaseEndpoint(base_url)

    assert be.base_url == base_url
    assert be.path_url == BaseEndpoint.path_url
    assert be.url == base_url + BaseEndpoint.path_url
    assert be.expected_schema == {}
    assert isinstance(be._session, Session)


@pytest.mark.parametrize(
    "payload, expected_body",
    [
        ({"name": "john", "age": 32}, "name=john&age=32"),
        ('{"name":"john","age":32}', b'"{\\"name\\":\\"john\\",\\"age\\":32}"'),
        (None, None),
    ],
)
def test_build_request(payload, expected_body, base_endpoint):
    if isinstance(payload, dict):
        pr = base_endpoint._build_request(data=payload)
    elif isinstance(payload, str):
        pr = base_endpoint._build_request(json=payload)
    else:
        pr = base_endpoint._build_request()

    assert isinstance(pr, PreparedRequest)
    assert pr.method == "GET"
    assert pr.url == base_endpoint.url
    assert pr.body == expected_body


def test_build_request_throws_error(base_endpoint):
    data = {"name": "john", "age": 32}
    json = '{"name":"john","age":32}'

    with pytest.raises(ValueError, match="Supply either `data` or `json`, not both"):
        base_endpoint._build_request(data=data, json=json)


def test_send(mocker: MockerFixture, base_endpoint):
    mock_prepared_request = mocker.Mock(spec=PreparedRequest)
    mock_session = mocker.patch("quick_qa.api.core.BaseEndpoint._session")
    mock_session.send.return_value = Response()

    response = base_endpoint._send(mock_prepared_request)

    mock_session.send.assert_called_once_with(request=mock_prepared_request)
    assert isinstance(response, Response)


def test_valid_schema(mocker: MockerFixture, endpoint_url, base_endpoint):
    mock_jsonschema = mocker.patch("quick_qa.api.core.jsonschema")
    mock_jsonschema.validate.return_value = None
    mock_response = mocker.Mock(spec=Response)

    result = base_endpoint.valid_schema(mock_response)

    mock_jsonschema.validate.assert_called_once_with(
        instance=mock_response.json(), schema=BaseEndpoint.expected_schema
    )
    assert result is True


def test_execute(mocker: MockerFixture, endpoint_url, base_endpoint):
    mock_build = mocker.patch.object(BaseEndpoint, "_build_request")
    mock_send = mocker.patch.object(BaseEndpoint, "_send")
    mock_prepared_req = mocker.Mock(spec=PreparedRequest)
    mock_res = mocker.Mock(spec=Response)
    mock_build.return_value = mock_prepared_req
    mock_send.return_value = mock_res

    res = base_endpoint.execute(payload={"name": "john", "age": 32})

    mock_build.assert_called_once_with(data={"name": "john", "age": 32})
    mock_send.assert_called_once_with(mock_prepared_req)
    assert res == mock_res
    assert isinstance(res, Response), f"Expected type: Response but got ({type(res)})"


def test_ping(mocker: MockerFixture, base_endpoint):
    mock_requests = mocker.patch("quick_qa.api.core.requests")
    mock_response = mocker.Mock(spec=Response)
    mock_requests.options.return_value = mock_response
    mock_response.status_code = 200

    up1 = base_endpoint.ping()
    mock_response.status_code = 404
    up2 = False

    mock_requests.options.assert_called_once_with(base_endpoint.url)
    assert up1 is True
    assert up2 is False
