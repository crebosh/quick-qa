import pytest
from pytest_mock.plugin import MockerFixture
from selenium.webdriver import ChromeOptions, FirefoxOptions
from selenium.webdriver.remote.webdriver import WebDriver

from quick_qa.web.webdriver_factory import (
    BrowserOptionsSpec,
    BrowserOptionsSpecBuilder,
    BrowserType,
    ChromeBuilder,
    FirefoxBuilder,
)


class TestBrowserOptionsBuilder:
    def test_create(self):
        result = BrowserOptionsSpecBuilder.create()

        assert isinstance(result, BrowserOptionsSpecBuilder)

    @pytest.mark.parametrize(
        "browser_type", [(BrowserType.CHROME), (BrowserType.FIREFOX)]
    )
    def test_set_browser_type(self, browser_type):
        result = BrowserOptionsSpecBuilder.create().set_browser_type(browser_type)

        assert result._browser_type == browser_type

    @pytest.mark.parametrize(
        "value, expected",
        [
            (True, True),
            (False, False),
        ],
    )
    def test_set_headless(self, value, expected):
        result = BrowserOptionsSpecBuilder.create().set_headless(value=value)

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
            options_builder = BrowserOptionsSpecBuilder.create().set_browser_type(
                browser_type
            )
        else:
            options_builder = (
                BrowserOptionsSpecBuilder.create()
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
            BrowserOptionsSpecBuilder.create().build()


class TestChromeBuilder:
    def test_init(self, mocker: MockerFixture):
        mock_browseroptionsspec = mocker.Mock(spec=BrowserOptionsSpec)
        cb = ChromeBuilder(mock_browseroptionsspec)

        assert cb._opts_spec == mock_browseroptionsspec
        assert isinstance(cb.options, ChromeOptions)

    @pytest.mark.parametrize(
        "options_spec, expected_windowsize, expected_headless",
        [
            (
                BrowserOptionsSpec(
                    browser_type=BrowserType.CHROME, window_size="full", headless=False
                ),
                "--start-maximized",
                None,
            ),
            (
                BrowserOptionsSpec(
                    browser_type=BrowserType.CHROME,
                    window_size=(1920, 1280),
                    headless=False,
                ),
                "--window-size=1920,1280",
                None,
            ),
            (
                BrowserOptionsSpec(
                    browser_type=BrowserType.CHROME, window_size=None, headless=False
                ),
                None,
                None,
            ),
            (
                BrowserOptionsSpec(
                    browser_type=BrowserType.CHROME, window_size=None, headless=True
                ),
                None,
                "--headless",
            ),
        ],
    )
    def test_build_options(
        self,
        options_spec: BrowserOptionsSpec,
        expected_windowsize,
        expected_headless,
        mocker: MockerFixture,
    ):
        mock_chrome_options = mocker.Mock(ChromeOptions)
        mock_chrome_options_cls = mocker.patch(
            "quick_qa.web.webdriver_factory.ChromeOptions"
        )
        mock_chrome_options_cls.return_value = mock_chrome_options

        cb = ChromeBuilder(options_spec)
        cb._build_options()

        if options_spec.window_size:
            mock_chrome_options.add_argument.assert_called_with(expected_windowsize)
        if options_spec.headless:
            mock_chrome_options.add_argument.asset_called_with(expected_headless)

    def test_build(self, mocker: MockerFixture):
        mock_browseroptionssec = mocker.Mock(spec=BrowserOptionsSpec)
        mock_driver = mocker.Mock(spec=WebDriver)
        mock_chrome_cls = mocker.patch(
            "quick_qa.web.webdriver_factory.webdriver.Chrome"
        )
        mock_chrome_cls.return_value = mock_driver

        cb = ChromeBuilder(mock_browseroptionssec)
        bo = mocker.patch.object(cb, "_build_options")
        result = cb.build()

        bo.assert_called_once()
        assert result == mock_driver


class TestFirefoxBuilder:
    def test_init(self, mocker: MockerFixture):
        mock_browseroptionsspec = mocker.Mock(spec=BrowserOptionsSpec)
        cb = FirefoxBuilder(mock_browseroptionsspec)

        assert cb._opts_spec == mock_browseroptionsspec
        assert isinstance(cb.options, FirefoxOptions)

    @pytest.mark.parametrize(
        "options_spec, expected_windowsize, expected_headless",
        [
            (
                BrowserOptionsSpec(
                    browser_type=BrowserType.FIREFOX, window_size="full", headless=False
                ),
                "--start-maximized",
                None,
            ),
            (
                BrowserOptionsSpec(
                    browser_type=BrowserType.FIREFOX,
                    window_size=(1920, 1280),
                    headless=False,
                ),
                "--window-size=1920,1280",
                None,
            ),
            (
                BrowserOptionsSpec(
                    browser_type=BrowserType.FIREFOX, window_size=None, headless=False
                ),
                None,
                None,
            ),
            (
                BrowserOptionsSpec(
                    browser_type=BrowserType.FIREFOX, window_size=None, headless=True
                ),
                None,
                "--headless",
            ),
        ],
    )
    def test_build_options(
        self,
        options_spec: BrowserOptionsSpec,
        expected_windowsize,
        expected_headless,
        mocker: MockerFixture,
    ):
        mock_firefox_options = mocker.Mock(FirefoxOptions)
        mock_firefox_options_cls = mocker.patch(
            "quick_qa.web.webdriver_factory.FirefoxOptions"
        )
        mock_firefox_options_cls.return_value = mock_firefox_options

        fb = FirefoxBuilder(options_spec)
        fb._build_options()

        if options_spec.window_size:
            mock_firefox_options.add_argument.assert_called_with(expected_windowsize)
        if options_spec.headless:
            mock_firefox_options.add_argument.asset_called_with(expected_headless)

    def test_build(self, mocker: MockerFixture):
        mock_browseroptionssec = mocker.Mock(spec=BrowserOptionsSpec)
        mock_driver = mocker.Mock(spec=WebDriver)
        mock_chrome_cls = mocker.patch(
            "quick_qa.web.webdriver_factory.webdriver.Firefox"
        )
        mock_chrome_cls.return_value = mock_driver

        fb = FirefoxBuilder(mock_browseroptionssec)
        bo = mocker.patch.object(fb, "_build_options")
        result = fb.build()

        bo.assert_called_once()
        assert result == mock_driver
