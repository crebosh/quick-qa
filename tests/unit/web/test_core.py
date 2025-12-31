import pytest
from pytest_mock.plugin import MockerFixture

from quick_qa.web import By
from quick_qa.web.core import (
    Component,
    DriverContainer,
    Element,
    Elements,
    PageComponent,
    WebDriver,
    WebDriverWait,
    WebElement,
)


class DemoComponent(PageComponent):
    pass


class DemoPage(DriverContainer):
    element = Element((By.ID, "id1"), 1.0)
    elements = Elements((By.ID, "id2"), 2.0)
    component = Component(DemoComponent, (By.ID, "id3"), 3.0)


@pytest.fixture
def mock_web_driver(mocker: MockerFixture):
    mock_web_driver = mocker.Mock(spec=WebDriver)
    yield mock_web_driver


@pytest.fixture
def mock_element(mocker: MockerFixture):
    mock_element = mocker.Mock(spec=WebElement)
    yield mock_element


@pytest.fixture
def mock_wait_cls(mocker: MockerFixture):
    mock_wait_cls = mocker.patch("quick_qa.web.core.WebDriverWait")
    yield mock_wait_cls


@pytest.fixture
def mock_wait(mocker: MockerFixture):
    mock_wait = mocker.Mock(spec=WebDriverWait)
    yield mock_wait


@pytest.fixture
def mock_ec(mocker: MockerFixture):
    mock_ec = mocker.patch("quick_qa.web.core.EC")
    yield mock_ec


@pytest.fixture
def locator():
    locator = (By.ID, "id1")
    yield locator


@pytest.fixture
def page_object(mock_web_driver):
    dp = DemoPage(mock_web_driver)
    yield dp


@pytest.fixture
def mock_element_list(mocker: MockerFixture):
    mock_element1 = mocker.Mock(spec=WebElement)
    mock_element2 = mocker.Mock(spec=WebElement)
    mock_element3 = mocker.Mock(spec=WebElement)
    yield [mock_element1, mock_element2, mock_element3]


class TestDriverContainer:
    def test_find(
        self, mock_web_driver, mock_element, mock_wait_cls, mock_wait, mock_ec, locator
    ):
        mock_wait_cls.return_value = mock_wait
        mock_wait.until.return_value = mock_element

        dc = DriverContainer(driver=mock_web_driver)
        element = dc.find(locator=locator, timeout=2.0)

        mock_wait.until.assert_called_once_with(
            mock_ec.presence_of_element_located(locator)
        )
        assert isinstance(element, WebElement)

    def test_find_all(
        self,
        mock_web_driver,
        mock_element_list,
        mock_wait_cls,
        mock_wait,
        mock_ec,
        locator,
    ):
        mock_wait_cls.return_value = mock_wait
        mock_wait.until.return_value = mock_element_list

        dc = DriverContainer(driver=mock_web_driver)
        elements = dc.find_all(locator=locator, timeout=2.0)

        mock_wait.until.assert_called_once_with(
            mock_ec.presence_of_all_elements_located(locator)
        )
        assert isinstance(elements, list)
        for e in elements:
            assert isinstance(e, WebElement)


class TestElement:
    def test_get_dunder_obstantiated(
        self, mocker: MockerFixture, mock_element, page_object
    ):
        mock_find = mocker.patch.object(page_object, "find")
        mock_find.return_value = mock_element

        returned_element = page_object.element

        assert isinstance(returned_element, WebElement)
        assert returned_element == mock_element

    def test_get_dunder_self(self):
        assert isinstance(DemoPage.element, Element)


class TestElements:
    def test_get_dunder_obstantiated(
        self, mocker: MockerFixture, mock_element_list, page_object
    ):
        mock_find = mocker.patch.object(page_object, "find_all")
        mock_find.return_value = mock_element_list

        returned_elements = page_object.elements

        assert isinstance(returned_elements, list)
        assert returned_elements == mock_element_list

    def test_get_dunder_self(self):
        assert isinstance(DemoPage.elements, Elements)


class TestComponent:
    def test_get_dunder_obstantiated(self, page_object):
        component = page_object.component
        assert isinstance(component, DemoComponent)

    def test_get_dunder_self(self):
        assert isinstance(DemoPage.component, Component)
