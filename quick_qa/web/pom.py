from __future__ import annotations

from typing import Optional, Union, overload

from loguru import logger
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By as _By
from selenium.webdriver.remote.webelement import WebElement

from quick_qa.web import driver_store
from quick_qa.web.config import Config
from quick_qa.web.element import Element
from quick_qa.web.waits import DocumentReady, JQueryInactive, NetworkIdle, wait


def DEFAULT_FIND_TIMEOUT():
    return Config.timeouts["find"]


def _find(
    locator: tuple, timeout: Optional[float] = None, parent: Optional[WebElement] = None
) -> WebElement:
    """find helper for basic find element logic."""
    timeout = timeout or DEFAULT_FIND_TIMEOUT()
    driver = parent or driver_store.get_driver()
    wait(driver, timeout, lambda d: d.find_element(*locator))
    return driver.find_element(*locator)


class Page:
    """base class for page objects

    Raises:
        TypeError: raised when concrete class doesn't have url attribute
    """

    url: str

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not hasattr(cls, "url"):
            raise TypeError(
                f"Class {cls.__name__} must define a class attribute `url`."
            )

    def find(self, locator: tuple, timeout: Optional[float] = None) -> WebElement:
        """find element on the page

        Args:
            locator (tuple):
            timeout (float, optional): used to set a different value from default wait timeout. Defaults to None.

        Returns:
            WebElement:
        """
        try:
            element = _find(locator=locator, timeout=timeout)
            return element
        except TimeoutException:
            logger.error(f"timed out trying to find element at: {locator}")
            raise

    def navigate_to(self):
        """navigates to page"""
        driver = driver_store.get_driver()
        self.wait_for_load()
        driver.get(self.url)

    def wait_for_load(self):
        driver = driver_store.get_driver()
        wait(driver, 10.0, DocumentReady(), JQueryInactive(), NetworkIdle())


class Component:
    """base class for page components"""

    def __init__(self, locator: tuple, timeout: Optional[float] = None):
        """
        Args:
            locator (tuple): use the locator for the componet root element.
            timeout (Optional[float], optional): used to set a different value from default wait timeout. Defaults to None.
        """
        self._root_locator = locator
        self._timeout = timeout

    @property
    def root(self) -> WebElement:
        """Property that finds and returns root element
        based on the root locator.

        Returns:
            WebElement:
        """
        try:
            root = _find(locator=self._root_locator, timeout=self._timeout)
            return root
        except TimeoutException:
            logger.error(
                f"timed out finding root element for componet: {self._root_locator}"
            )
            raise

    def find(self, locator: tuple, timeout: Optional[float] = None) -> WebElement:
        """find element from element

        Args:
            locator (tuple):
            timeout (Optional[float], optional):  used to set a different value from default wait timeout. Defaults to None.

        Returns:
            WebElement:
        """
        timeout = timeout or DEFAULT_FIND_TIMEOUT()
        try:
            root = self.root
            wait(root, timeout, lambda d: d.find_element(*locator))
            element = root.find_element(*locator)
            return element
        except TimeoutException:
            logger.error(f"timeout out finding element from component at: {locator}")
            raise


class Locator:
    """descriptor class for locating elements from pages or components.
    wraps WebElement in the Element class
    """

    def __init__(self, locator: tuple, timeout: Optional[float] = None):
        self.locator = locator
        self.timeout = timeout

    def __set_name__(self, owner, name):
        self.property_name = name

    @overload
    def __get__(self, instance: None, owner) -> Locator: ...
    @overload
    def __get__(self, instance: Union[Page, Component], owner) -> Element: ...
    def __get__(self, instance, owner) -> Locator | Element:
        if instance is None:
            return self

        web_element = instance.find(self.locator)
        return Element(web_element, self.property_name)


class By(_By):
    pass
