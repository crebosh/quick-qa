from typing import Union

from selenium.types import WaitExcTypes
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait


class DocumentReady:
    def __call__(self, driver):
        return driver.execute_script("return document.readyState") == "complete"


class JQueryInactive:
    def __call__(self, driver):
        return driver.execute_script(
            """
            return window.jQuery === undefined || jQuery.active === 0;
        """
        )


class NetworkIdle:
    def __init__(self):
        self._script = """
        if (!window.__seleniumXHRTracker) {
            window.__seleniumXHRTracker = { pending: 0 };

            const open = XMLHttpRequest.prototype.open;
            XMLHttpRequest.prototype.open = function() {
                this.addEventListener('readystatechange', function() {
                    if (this.readyState === 1) window.__seleniumXHRTracker.pending++;
                    if (this.readyState === 4) window.__seleniumXHRTracker.pending--;
                });
                open.apply(this, arguments);
            };

            const fetch = window.fetch;
            window.fetch = function() {
                window.__seleniumXHRTracker.pending++;
                return fetch.apply(this, arguments).finally(() => {
                    window.__seleniumXHRTracker.pending--;
                });
            };
        }
        return window.__seleniumXHRTracker.pending;
        """

    def __call__(self, driver):
        return driver.execute_script(self._script) == 0


def wait(
    driver: Union[WebDriver, WebElement],
    timeout: float,
    *conditions,
    ignored_exceptions: WaitExcTypes | None = None
):
    """waits depending on the input

    Example Usage:
        wait(driver, 3.0, EC.preseence_of_element_located(locator), [StaleElementReference])

    Args:
        driver (Union[WebDriver, WebElement]):
        timeout (float):
        ignored_exceptions (WaitExcTypes | None, optional): . Defaults to None.
    """
    wait = WebDriverWait(
        driver=driver, timeout=timeout, ignored_exceptions=ignored_exceptions
    )
    combined = EC.all_of(*conditions)
    wait.until(combined)
