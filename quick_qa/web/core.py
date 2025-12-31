"""Module that holds the core web classes"""

from __future__ import annotations

from typing import Any, Generic, List, Optional, Tuple, Type, TypeVar, Union, overload

from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

DEFAULT_FIND_TIMEOUT = 5.0


DriverLike = Union[WebDriver, WebElement]
C = TypeVar("C", bound="DriverContainer")


class DriverContainer:
    """Class for holding driver like objects"""

    def __init__(self, driver: DriverLike):
        self._driver = driver

    def find(
        self, locator: Tuple[str, str], timeout: Optional[float] = None
    ) -> WebElement:
        """find an element

        Args:
            locator (Tuple[str,str]): (By.Id, 'id1')
            timeout (Optional[float], optional): sets a non default timeout value. Defaults to None.

        Returns:
            WebElement:
        """
        timeout = timeout or DEFAULT_FIND_TIMEOUT
        wait = WebDriverWait(
            self._driver, timeout=timeout, ignored_exceptions=[NoSuchElementException]
        )
        element = wait.until(EC.presence_of_element_located(locator))
        return element

    def find_all(
        self, locator: Tuple[str, str], timeout: Optional[float] = None
    ) -> List[WebElement]:
        """finds all elements based on locator

        Args:
            locator (Tuple[str,str]): (By.ID, id1)
            timeout (Optional[float], optional): sets a non default timeout value. Defaults to None.

        Returns:
            List[WebElement]:
        """
        timeout = timeout or DEFAULT_FIND_TIMEOUT
        wait = WebDriverWait(
            self._driver, timeout=timeout, ignored_exceptions=[NoSuchElementException]
        )
        elements = wait.until(EC.presence_of_all_elements_located(locator))
        return elements


class Element:
    def __init__(self, locator: Tuple[str, str], timeout: Optional[float] = None):
        self.locator = locator
        self.timeout = timeout

    @overload
    def __get__(self, instance: None, owner: type[Any]) -> "Element": ...
    @overload
    def __get__(self, instance: DriverContainer, owner: type[Any]) -> WebElement: ...
    def __get__(self, instance, owner) -> Union[WebElement, "Element"]:
        if instance is None:
            return self

        element = instance.find(self.locator, self.timeout)
        return element


class Elements:
    """Element descriptor for page"""

    def __init__(self, locator: Tuple[str, str], timeout: Optional[float] = None):
        self.locator = locator
        self.timeout = timeout

    @overload
    def __get__(self, instance: None, owner: type[Any]) -> "Elements": ...
    @overload
    def __get__(
        self, instance: DriverContainer, owner: type[Any]
    ) -> List[WebElement]: ...
    def __get__(self, instance, owner) -> Union[List[WebElement], "Elements"]:
        if instance is None:
            return self

        elements = instance.find_all(self.locator, self.timeout)
        return elements


class Component(Generic[C]):
    """Component descriptor for page

    Args:
        Generic (_type_): _description_
    """

    def __init__(
        self,
        component_cls: Type[C],
        locator: Tuple[str, str],
        timeout: Optional[float] = None,
    ):
        self.component_cls = component_cls
        self.locator = locator
        self.timeout = timeout

    @overload
    def __get__(self, instance: None, owner: type[Any]) -> "Component[C]": ...
    @overload
    def __get__(self, instance: DriverContainer, owner: type[Any]) -> C: ...
    def __get__(self, instance, owner) -> Union[C, "Component[C]"]:
        if instance is None:
            return self

        instance.find(self.locator, self.timeout)
        return self.component_cls(instance._driver)


class PageComponent(DriverContainer):
    pass


class Page(DriverContainer):
    pass
