from selenium.webdriver.remote.webelement import WebElement


class Element:
    """light element wrapper"""

    def __init__(self, web_element: WebElement, name: str):
        self._parent = web_element
        self.name = name

    def click(self) -> None:
        """click on element"""
        self._parent.click()

    def send_keys(self, text: str) -> None:
        """send text to an element

        Args:
            text (str):
        """
        self._parent.send_keys(text)

    def __getattr__(self, name):
        """fallback that allows using wrapped element."""
        return getattr(self._parent, name)
