from typing import Optional

from loguru import logger
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

from quick_qa.web.config import Config
from quick_qa.web.waits import wait


def DEFAULT_INTERACT_TIMEOUT():
    return Config.timeouts["interact"]


class Element:
    """light element wrapper"""

    __slots__ = ("_parent", "name")

    def __init__(self, web_element: WebElement, name: str):
        self._parent = web_element
        self.name = name

    def click(self, timeout: Optional[float] = None) -> None:
        """click on element"""
        timeout = timeout or DEFAULT_INTERACT_TIMEOUT()
        try:
            wait(self._parent, timeout, EC.element_to_be_clickable(self._parent))
            self._parent.click()
        except TimeoutException:
            logger.error(f"timed out clicking on {self.name}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error {e}")
            raise

    def send_keys(self, text: str, timeout: Optional[float] = None) -> None:
        """send text to an element

        Args:
            text (str):
        """
        timeout = timeout or DEFAULT_INTERACT_TIMEOUT()
        try:
            wait(
                self._parent,
                timeout,
                EC.visibility_of(self._parent),
                lambda d: d.is_enabled,
            )
            self._parent.send_keys(text)
        except TimeoutException:
            logger.error(f"timedout out sending text to {self.name}: {text}")
            raise

    def __getattr__(self, name):
        """fallback that allows using wrapped element."""
        return getattr(self._parent, name)
