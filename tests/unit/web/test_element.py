import pytest
from pytest_mock import MockerFixture
from selenium.webdriver.remote.webelement import WebElement

from quick_qa.web.element import Element


@pytest.fixture
def element_obj(mocker: MockerFixture):
    mock_webelement = mocker.Mock(spec=WebElement)
    name = "myelement"
    element = Element(web_element=mock_webelement, name=name)
    yield element


class TestElement:
    def test_init(self, mocker: MockerFixture):
        mock_webelement = mocker.Mock(spec=WebElement)
        name = "myelement"
        result = Element(web_element=mock_webelement, name=name)

        assert result._parent == mock_webelement
        assert result.name == name

    def test_click(self, mocker, element_obj):
        mock_wait = mocker.patch("quick_qa.web.element.wait")

        element_obj.click()

        mock_wait.assert_called_once()
        element_obj._parent.click.assert_called_once()

    def test_send_keys(self, element_obj, mocker):
        mock_wait = mocker.patch("quick_qa.web.element.wait")

        text = "mytext"

        element_obj.send_keys(text=text)

        mock_wait.assert_called_once()
        element_obj._parent.send_keys.assert_called_once_with(text)
