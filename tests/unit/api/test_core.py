import pytest
from pytest_mock.plugin import MockerFixture

from quick_qa.api.core import BaseEndpoint, Response, Session


@pytest.fixture(autouse=True)
def run_after_each_test():
    yield
    BaseEndpoint.path_url = None


@pytest.fixture
def base_url():
    url = "http://www.mybaseurl.com"
    yield url


@pytest.fixture
def base_endpoint(base_url):
    BaseEndpoint.path_url = "/mypath"
    be = BaseEndpoint(base_url)
    yield be
    BaseEndpoint.path_url = None


class TestBaseEndpoint:
    def test_base_endpoint_init(self, base_url):
        path_url = "/myPath"
        BaseEndpoint.path_url = path_url
        be = BaseEndpoint(base_url=base_url)

        assert isinstance(be._session, Session)
        assert be.base_url == base_url
        assert be.path_url == path_url
        assert be.endpoint_url == base_url + path_url
        assert be.expected_schema == {}

    def test_base_endpoint_init_error(self, base_url):
        with pytest.raises(TypeError, match="no path_url set"):
            BaseEndpoint(base_url)

    @pytest.mark.parametrize(
        "side_effect, result",
        [(TypeError("my error"), TypeError("my error")), (None, True)],
    )
    def test_valid_schema(
        self, side_effect, result, mocker: MockerFixture, base_endpoint
    ):
        mock_jsonschema = mocker.patch("quick_qa.api.core.jsonschema")
        mock_jsonschema.validate.return_value = None
        mock_jsonschema.validate.side_effect = side_effect
        mock_response = mocker.Mock(spec=Response)

        result = base_endpoint.valid_schema(mock_response)

        mock_jsonschema.validate.assert_called_once_with(
            instance=mock_response.json(), schema=BaseEndpoint.expected_schema
        )
        assert result is result

    @pytest.mark.parametrize("code, expected_ping_result", [(200, True), (404, False)])
    def test_ping(
        self, code, expected_ping_result, mocker: MockerFixture, base_endpoint
    ):
        mock_optionscall = mocker.patch("quick_qa.api.core.requests.options")
        mock_response = mocker.Mock(spec=Response)
        mock_optionscall.return_value = mock_response

        mock_response.status_code = code
        up = base_endpoint.ping()

        mock_optionscall.assert_called_once_with(base_endpoint.endpoint_url)
        assert up is expected_ping_result

    def test_allowed_methods(self, mocker: MockerFixture, base_endpoint):
        expected_methods = ["options", "get", "post"]
        mock_response = mocker.Mock(spec=Response)
        mock_response.headers = {"Allow": "options,get,post"}
        mock_optionscall = mocker.patch("quick_qa.api.core.requests.options")
        mock_optionscall.return_value = mock_response

        methods = base_endpoint.allowed_methods()

        assert methods.sort() == expected_methods.sort()
