from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Callable, Dict, Optional, Protocol

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.remote.webdriver import WebDriver


class BrowserType(str, Enum):
    CHROME = "chrome"
    FIREFOX = "firefox"


@dataclass(frozen=True)
class BrowserOptions:
    """data class for building drivers"""

    browser_type: BrowserType
    headless: bool = False


@dataclass(frozen=True)
class BrowserOptionsBuilder:
    """builder classs to contruct the BrowserOptions
    dataclass

    Raises:
        ValueError: raised when using build with no browser_type
    """

    _browser_type: Optional[BrowserType] = None
    _headless: bool = False

    @staticmethod
    def create() -> BrowserOptionsBuilder:
        """initiates build process

        Returns:
            BrowserOptionsBuilder:
        """
        return BrowserOptionsBuilder()

    def set_browser_type(self, browser_type: BrowserType) -> BrowserOptionsBuilder:
        """sets the browser ype

        Args:
            browser_type (BrowserType):

        Returns:
            BrowserOptionsBuilder:
        """
        return replace(self, _browser_type=browser_type)

    def set_headless(self, value: bool) -> BrowserOptionsBuilder:
        """sets headless

        Args:
            value (bool):

        Returns:
            BrowserOptionsBuilder:
        """
        return replace(self, _headless=value)

    def build(self) -> BrowserOptions:
        """builds the BrowserOptions

        Raises:
            ValueError: returned when no browser_type set

        Returns:
            BrowserOptions:
        """
        if self._browser_type is None:
            raise ValueError("Browser type must be specified before building.")
        return BrowserOptions(browser_type=self._browser_type, headless=self._headless)


class _BuilderProtocol(Protocol):
    def __init__(self, opts: BrowserOptions) -> None: ...
    def build(self) -> WebDriver: ...


class ChromeBuilder:
    """implements builder protocol for building chrome driver"""

    def __init__(self, opts: BrowserOptions) -> None:
        self.opts = opts
        self.options = ChromeOptions()
        if opts.headless:
            self.options.add_argument("--headless")

    def build(self) -> WebDriver:
        """returns the webdriver"""
        return webdriver.Chrome(options=self.options)


class FirefoxBuilder:
    """implements builder protocol for building firefox driver"""

    def __init__(self, opts: BrowserOptions) -> None:
        self.opts = opts
        self.options = FirefoxOptions()
        if opts.headless:
            self.options.add_argument("--headless")

    def build(self) -> WebDriver:
        """returns the webdriver"""
        return webdriver.Firefox(options=self.options)


class DriverFactory:
    """utilizes the driver builders to return your driver based on inputs

    Raises:
        ValueError: when browsertype enum uses a browser value that isn't supported yet
    """

    _registry: Dict[BrowserType, Callable[[BrowserOptions], _BuilderProtocol]] = {
        BrowserType.CHROME: ChromeBuilder,
        BrowserType.FIREFOX: FirefoxBuilder,
    }

    @classmethod
    def register(
        cls, btype: BrowserType, builder: Callable[[BrowserOptions], _BuilderProtocol]
    ) -> None:
        """Add support for a new browser type at runtime."""
        cls._registry[btype] = builder

    @staticmethod
    def get_driver(opts: BrowserOptions) -> WebDriver:
        """used for gettting a driver

        Args:
            opts (BrowserOptions):

        Raises:
            ValueError: when browsertype enum uses a browser value that isn't supported yet

        Returns:
            WebDriver:
        """
        try:
            builder_cls = DriverFactory._registry[opts.browser_type]
        except KeyError as exc:
            raise ValueError(f"Unsupported browser type: {opts.browser_type}") from exc

        builder = builder_cls(opts)
        return builder.build()
