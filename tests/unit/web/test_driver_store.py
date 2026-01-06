import contextvars

import pytest
from pytest_mock import MockerFixture
from selenium.webdriver.remote.webdriver import WebDriver

from quick_qa.web import driver_store


def test_driver_ctx():
    assert isinstance(driver_store._driver_ctx, contextvars.ContextVar)
    assert driver_store._driver_ctx.name == "webdriver"


def test_set_driver(mocker: MockerFixture):
    mock_driver = mocker.Mock(spec=WebDriver)

    driver_store.set_driver(driver=mock_driver)

    assert driver_store._driver_ctx.get() == mock_driver


def test_get_driver(mocker: MockerFixture):
    mock_driver = mocker.Mock(spec=WebDriver)
    driver_store._driver_ctx.set(mock_driver)

    result = driver_store.get_driver()
    expected = driver_store._driver_ctx.get()

    assert result == expected


def test_get_driver_error(mocker: MockerFixture):
    driver_store.clear_driver()
    with pytest.raises(RuntimeError):
        driver_store.get_driver()


def test_clear_driver(mocker: MockerFixture):
    mock_driver = mocker.Mock(spec=WebDriver)
    driver_store._driver_ctx.set(mock_driver)

    driver_store.clear_driver()

    assert driver_store._driver_ctx.get() is None
