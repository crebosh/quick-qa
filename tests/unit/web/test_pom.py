from unittest.mock import PropertyMock

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

    def test_find(self, mock_driverstore, mock_driver, mock_element, mocker):
        mock_driver.find_element.return_value = mock_element
        mock_driverstore.return_value = mock_driver
        mock_wait = mocker.patch("quick_qa.web.pom.wait")

        locator = (By.ID, "myid")

        my_page = MyPage()
        result = my_page.find(locator=locator, timeout=None)

        mock_wait.assert_called_once()
        mock_driver.find_element.assert_called_once_with(*locator)
        assert result == mock_element

    def test_navigate_to(self, mocker: MockerFixture, mock_driverstore, mock_driver):
        mock_driverstore.return_value = mock_driver
        mock_wait = mocker.patch("quick_qa.web.pom.wait")

        mp = MyPage()
        mp.navigate_to()

        mock_wait.assert_called_once()
        mock_driver.get.assert_called_once_with(mp.url)


class TestComponent:
    def test_init(self):
        locator = (By.ID, "myid")
        timeout = 3.0

        c = Component(locator=locator, timeout=timeout)
        assert c._root_locator == locator
        assert c._timeout == timeout

    def test_find(self, mocker: MockerFixture, mock_element):
        locator = (By.ID, "mycomponentid")
        timeout = 3.0
        expected_element = mocker.Mock(spec=WebElement)
        mock_element.find_element.return_value = expected_element
        mc = Component(locator=(), timeout=2)

        mock_root = mocker.patch.object(
            Component,
            "root",
            new_callable=PropertyMock,
        )
        mock_root.return_value = mock_element
        mock_wait = mocker.patch("quick_qa.web.pom.wait")

        e = mc.find(locator, timeout)

        mock_root.assert_called_once()
        mock_wait.assert_called_once()
        mock_element.find_element.assert_called_once()
        assert e == expected_element
