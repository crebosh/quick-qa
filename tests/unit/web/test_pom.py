import pytest
from pytest_mock import MockerFixture
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement

from quick_qa.web.pom import Component, Page


class MyPage(Page):
    url = "http://www.myurl.com"


@pytest.fixture
def mock_element(mocker: MockerFixture):
    m_element = mocker.Mock(spec=WebElement)
    yield m_element


@pytest.fixture
def mock_driver(mock_element, mocker: MockerFixture):
    m_driver = mocker.Mock(spec=WebDriver)
    yield m_driver


@pytest.fixture
def mock_driverstore(mock_driver, mocker: MockerFixture):
    m_driverstore = mocker.patch("quick_qa.web.pom.driver_store.get_driver")
    yield m_driverstore


class TestPage:
    def test_required_url(self):
        with pytest.raises(TypeError):

            class NewPage(Page):
                pass

    def test_find(self, mock_driverstore, mock_driver, mock_element):
        mock_driver.find_element.return_value = mock_element
        mock_driverstore.return_value = mock_driver
        locator = (By.ID, "myid")

        my_page = MyPage()
        result = my_page.find(locator=locator, timeout=None)

        mock_driver.find_element.assert_called_once_with(*locator)
        assert result == mock_element

    def test_navigate_to(self, mocker: MockerFixture, mock_driverstore, mock_driver):
        mock_driverstore.return_value = mock_driver

        mp = MyPage()
        mp.navigate_to()

        mock_driver.get.assert_called_once_with(mp.url)


class TestComponent:
    def test_init(self):
        locator = (By.ID, "myid")
        timeout = 3.0

        c = Component(locator=locator, timeout=timeout)
        assert c._root_locator == locator
        assert c._timeout == timeout

    def test_find(self, mocker, mock_driverstore, mock_driver, mock_element):
        locator = (By.ID, "mycomponentid")
        timeout = 3.0
        element_locator = (By.ID, "myid2")
        new_mock_element = mocker.Mock(spec=WebElement)

        mock_driverstore.return_value = mock_driver
        mock_driver.find_element.return_value = mock_element
        mock_element.find_element.return_value = new_mock_element

        mc = Component(locator=locator, timeout=timeout)
        result = mc.find(locator=element_locator, timeout=timeout)

        assert result == new_mock_element
        mock_driver.find_element.assert_called_once_with(*locator)
        mock_element.find_element.assert_called_once_with(*element_locator)
