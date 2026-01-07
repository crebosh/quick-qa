from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
from typing import Callable, Dict, List, Optional, Protocol, Tuple, Union

from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.remote.webdriver import WebDriver


#  -------------------------------------#
#  Enums
# --------------------------------------#
class BrowserType(str, Enum):
    CHROME = "chrome"
    FIREFOX = "firefox"


#  -------------------------------------#
#  Specs
# --------------------------------------#


@dataclass(frozen=True)
class BrowserOptionsSpec:
    """data class for building drivers"""

    browser_type: BrowserType
    window_size: Union[str, Tuple[int, int], None]
    headless: bool = False


class _DriverBuilderProtocol(Protocol):
    def __init__(self, opts: BrowserOptionsSpec) -> None: ...
    def _build_options(self) -> None: ...
    def build(self) -> WebDriver: ...


#  -------------------------------------#
#  Spec Builder
# --------------------------------------#
@dataclass(frozen=True)
class BrowserOptionsSpecBuilder:
    """builder classs to contruct the BrowserOptions
    dataclass

    Raises:
        ValueError: raised when using build with no browser_type
    """

    _browser_type: Optional[BrowserType] = None
    _headless: bool = False
    _window_size: Union[str, Tuple[int, int], None] = None

    @staticmethod
    def create() -> BrowserOptionsSpecBuilder:
        """initiates build process

        Returns:
            BrowserOptionsBuilder:
        """
        return BrowserOptionsSpecBuilder()

    def set_browser_type(self, browser_type: BrowserType) -> BrowserOptionsSpecBuilder:
        """sets the browser ype

        Args:
            browser_type (BrowserType):

        Returns:
            BrowserOptionsBuilder:
        """
        return replace(self, _browser_type=browser_type)

    def set_headless(self, value: bool) -> BrowserOptionsSpecBuilder:
        """sets headless

        Args:
            value (bool):

        Returns:
            BrowserOptionsBuilder:
        """
        return replace(self, _headless=value)

    def set_extensions(self, extensions: List[str]) -> BrowserOptionsSpecBuilder:
        return replace(self, _extensions=extensions)

    def set_window_size(self, value: str) -> BrowserOptionsSpecBuilder:
        return_value = value.lower().strip()
        if return_value != "full":
            return_value = tuple([int(x) for x in value.split(",")])
        return replace(self, _window_size=return_value)

    def build(self) -> BrowserOptionsSpec:
        """builds the BrowserOptions

        Raises:
            ValueError: returned when no browser_type set

        Returns:
            BrowserOptions:
        """
        if self._browser_type is None:
            raise ValueError("Browser type must be specified before building.")
        return BrowserOptionsSpec(
            browser_type=self._browser_type,
            headless=self._headless,
            window_size=self._window_size,
        )


#  -------------------------------------#
#  Builder Implementations
# --------------------------------------#
class ChromeBuilder:
    """implements builder protocol for building chrome driver"""

    def __init__(self, opts: BrowserOptionsSpec) -> None:
        self._opts_spec = opts
        self.options = ChromeOptions()

    def _build_options(self) -> None:
        if self._opts_spec.headless:
            self.options.add_argument("--headless")
        if self._opts_spec.window_size == "full":
            self.options.add_argument("--start-maximized")
        elif self._opts_spec.window_size:
            self.options.add_argument(
                f"--window-size={self._opts_spec.window_size[0]},{self._opts_spec.window_size[1]}"
            )

    def build(self) -> WebDriver:
        """returns the webdriver"""
        self._build_options()
        return webdriver.Chrome(options=self.options)


class FirefoxBuilder:
    """implements builder protocol for building firefox driver"""

    def __init__(self, opts: BrowserOptionsSpec) -> None:
        self._opts_spec = opts
        self.options = FirefoxOptions()

    def _build_options(self) -> None:
        if self._opts_spec.headless:
            self.options.add_argument("--headless")
        if self._opts_spec.window_size == "full":
            self.options.add_argument("--start-maximized")
        elif self._opts_spec.window_size:
            self.options.add_argument(
                f"--window-size={self._opts_spec.window_size[0]},{self._opts_spec.window_size[1]}"
            )

    def build(self) -> WebDriver:
        """returns the webdriver"""
        self._build_options()
        return webdriver.Firefox(options=self.options)


class DriverFactory:
    """utilizes the driver builders to return your driver based on inputs

    Raises:
        ValueError: when browsertype enum uses a browser value that isn't supported yet
    """

    _registry: Dict[
        BrowserType, Callable[[BrowserOptionsSpec], _DriverBuilderProtocol]
    ] = {
        BrowserType.CHROME: ChromeBuilder,
        BrowserType.FIREFOX: FirefoxBuilder,
    }

    @classmethod
    def register(
        cls,
        btype: BrowserType,
        builder: Callable[[BrowserOptionsSpec], _DriverBuilderProtocol],
    ) -> None:
        """Add support for a new browser type at runtime."""
        cls._registry[btype] = builder

    @staticmethod
    def get_driver(opts: BrowserOptionsSpec) -> WebDriver:
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
