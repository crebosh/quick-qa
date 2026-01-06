import pytest
from pytest_mock.plugin import MockerFixture
from selenium.webdriver import ChromeOptions, FirefoxOptions

from quick_qa.web.webdriver_factory import (
    BrowserOptions,
    BrowserOptionsBuilder,
    BrowserType,
    ChromeBuilder,
    FirefoxBuilder,
)


class TestBrowserOptionsBuilder:
    def test_create(self):
        result = BrowserOptionsBuilder.create()

        assert isinstance(result, BrowserOptionsBuilder)

    @pytest.mark.parametrize(
        "browser_type", [(BrowserType.CHROME), (BrowserType.FIREFOX)]
    )
    def test_set_browser_type(self, browser_type):
        result = BrowserOptionsBuilder.create().set_browser_type(browser_type)

        assert result._browser_type == browser_type

    @pytest.mark.parametrize(
        "value, expected",
        [
            (True, True),
            (False, False),
        ],
    )
    def test_set_headless(self, value, expected):
        result = BrowserOptionsBuilder.create().set_headless(value=value)

        assert result._headless is expected

    @pytest.mark.parametrize(
        "browser_type, headless, expected_headless",
        [
            (BrowserType.CHROME, True, True),
            (BrowserType.CHROME, False, False),
            (BrowserType.CHROME, None, False),
            (BrowserType.FIREFOX, True, True),
            (BrowserType.FIREFOX, False, False),
            (BrowserType.FIREFOX, None, False),
        ],
    )
    def test_build(self, browser_type, headless, expected_headless):
        if headless is None:
            options_builder = BrowserOptionsBuilder.create().set_browser_type(
                browser_type
            )
        else:
            options_builder = (
                BrowserOptionsBuilder.create()
                .set_browser_type(browser_type)
                .set_headless(headless)
            )

        result = options_builder.build()

        assert result.browser_type == browser_type
        assert result.headless is expected_headless

    def test_build_error(self):
        with pytest.raises(
            ValueError, match="Browser type must be specified before building."
        ):
            BrowserOptionsBuilder.create().build()


class TestChromeBuilder:
    def test_init(self, mocker: MockerFixture):
        mock_browseroptions = mocker.Mock(spec=BrowserOptions)
        mock_browseroptions.headless = True

        mock_chromeoptions_cls = mocker.patch(
            "quick_qa.web.webdriver_factory.ChromeOptions",
            spec=ChromeOptions,
        )
        mock_chromeoptions_obj = mocker.Mock(spec=ChromeOptions)
        mock_chromeoptions_cls.return_value = mock_chromeoptions_obj

        chrome_builder = ChromeBuilder(mock_browseroptions)

        assert chrome_builder.opts == mock_browseroptions
        assert isinstance(chrome_builder.options, ChromeOptions)
        chrome_builder.options.add_argument.assert_called_once_with("--headless")

    def test_build(self, mocker: MockerFixture):
        mock_browseroptions = mocker.Mock(spec=BrowserOptions)

        mock_chromeoptions_cls = mocker.patch(
            "quick_qa.web.webdriver_factory.ChromeOptions",
            autospec=True,
        )
        mock_chromeoptions_obj = mocker.Mock()
        mock_chromeoptions_cls.return_value = mock_chromeoptions_obj

        mock_chrome_ctor = mocker.patch(
            "quick_qa.web.webdriver_factory.webdriver.Chrome",
            autospec=True,
        )
        mock_chrome_obj = mocker.Mock()
        mock_chrome_ctor.return_value = mock_chrome_obj

        builder = ChromeBuilder(mock_browseroptions)
        result = builder.build()

        assert (
            result is mock_chrome_obj
        ), "build() should return the webdriver.Chrome mock"

        mock_chrome_ctor.assert_called_once_with(options=mock_chromeoptions_obj)

        assert builder.options is mock_chromeoptions_obj


class TestFirefoxBuilder:
    def test_init(self, mocker: MockerFixture):
        mock_browseroptions = mocker.Mock(spec=BrowserOptions)
        mock_browseroptions.headless = True

        mock_firefoxoptions_cls = mocker.patch(
            "quick_qa.web.webdriver_factory.FirefoxOptions",
            spec=FirefoxOptions,
        )
        mock_firefoxoptions_obj = mocker.Mock(spec=FirefoxOptions)
        mock_firefoxoptions_cls.return_value = mock_firefoxoptions_obj

        firefox_builder = FirefoxBuilder(mock_browseroptions)

        assert firefox_builder.opts == mock_browseroptions
        assert isinstance(firefox_builder.options, FirefoxOptions)
        firefox_builder.options.add_argument.assert_called_once_with("--headless")

    def test_build(self, mocker: MockerFixture):
        mock_browseroptions = mocker.Mock(spec=BrowserOptions)

        mock_firefoxoptions_cls = mocker.patch(
            "quick_qa.web.webdriver_factory.FirefoxOptions",
            autospec=True,
        )
        mock_firefoxoptions_obj = mocker.Mock()
        mock_firefoxoptions_cls.return_value = mock_firefoxoptions_obj

        mock_firefox_ctor = mocker.patch(
            "quick_qa.web.webdriver_factory.webdriver.Firefox",
            autospec=True,
        )
        mock_firefox_obj = mocker.Mock()
        mock_firefox_ctor.return_value = mock_firefox_obj

        builder = FirefoxBuilder(mock_browseroptions)
        result = builder.build()

        assert (
            result is mock_firefox_obj
        ), "build() should return the webdriver.Chrome mock"

        mock_firefox_ctor.assert_called_once_with(options=mock_firefoxoptions_obj)

        assert builder.options is mock_firefoxoptions_obj
