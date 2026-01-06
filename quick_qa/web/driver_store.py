import contextvars

from selenium.webdriver.remote.webdriver import WebDriver

_driver_ctx: contextvars.ContextVar[WebDriver | None] = contextvars.ContextVar(
    "webdriver", default=None
)


def set_driver(driver: WebDriver) -> None:
    """Sets a driver into a context var

    Args:
        driver (WebDriver)
    """
    _driver_ctx.set(driver)


def get_driver() -> WebDriver:
    """retrieves driver from context var

    Raises:
        RuntimeError: raised when no driver is set

    Returns:
        WebDriver:
    """
    driver = _driver_ctx.get()
    if driver is None:
        raise RuntimeError(
            "WebDriver not initialised for this context. "
            "Make sure the pytest fixture has run."
        )
    return driver


def clear_driver() -> None:
    """reset contextvar to None"""
    _driver_ctx.set(None)
