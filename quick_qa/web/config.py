from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional
from urllib.parse import urlparse

from loguru import logger

from quick_qa.configuration import ConfigType, Configuration


# --------------------------------------------------------------------------- #
# Helper functions
# --------------------------------------------------------------------------- #
def is_url(text: str) -> bool:
    """check if str value is a url

    Args:
        text (str):

    Returns:
        bool:
    """
    try:
        result = urlparse(text.strip())
        return bool(result.scheme and result.netloc)
    except Exception:
        return False


def is_int_pair(s: str) -> bool:
    """check if string is in format "<int>,<int>"

    Args:
        s (str):

    Returns:
        bool:
    """
    parts = s.split(",")
    if len(parts) != 2:
        return False

    left, right = parts[0].strip(), parts[1].strip()
    try:
        int(left)
        int(right)
        return True
    except ValueError:
        return False


# --------------------------------------------------------------------------- #
# Data structures
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class DriverSpec:
    """spec for driver options"""

    name: str
    browser: str
    headless: bool
    window_size: str


# --------------------------------------------------------------------------- #
# Core configuration class
# --------------------------------------------------------------------------- #
class Config:
    """class for setting web configurations"""

    timeouts: Dict[str, float] = {"find": 5.0, "interact": 3.0}
    base_url: Optional[str] = None
    drivers: List[DriverSpec] = [
        DriverSpec(
            name="chrome desktop",
            browser="chrome",
            headless=False,
            window_size="1280,1280",
        )
    ]

    # ------------------------------------------------------------------- #
    # Public API
    # ------------------------------------------------------------------- #
    @classmethod
    def set_values(cls) -> None:
        """checks that data from yaml are valid values
        then sets them to the class attributes
        """
        data = Configuration.get_config(ConfigType.WEB)
        if data is None:
            return

        Config._validate_data(data=data)

        cls._set_value("timeouts", data.get("timeouts"))
        cls._set_value("base_url", data.get("base_url"))
        cls._set_value("drivers", data.get("drivers"))

    # ------------------------------------------------------------------- #
    # Internal helpers
    # ------------------------------------------------------------------- #
    @classmethod
    def _set_value(cls, attr: str, value: Any) -> None:
        """wraps setting a value for single logging method.

        Args:
            attr (str): name of attribute
            value (Any): attribute value
        """
        if value is None:
            logger.warning(f"configfile {attr} value was None. keeping default")
            return
        setattr(cls, attr, value)

    @staticmethod
    def _validate_data(data: Mapping[str, Any]) -> None:
        """validates data for configurations

        Args:
            data (Mapping[str, Any]):

        Raises:
            ValueError: if timeout keys don't hold floats
            ValueError: unexpected timeout keys
            ValueError: invalid url
            ValueError: drivers don;t fit spec
            ValueError: missing driver keys
            ValueError: improper window size
        """
        # ---- timeouts ----------------------------------------------------
        if (timeouts := data.get("timeouts")) is not None:
            allowed_keys = {"find", "interact"}
            if not isinstance(timeouts, Mapping):
                raise ValueError("`timeouts` must be a mapping of key → float")
            unknown = set(timeouts) - allowed_keys
            if unknown:
                raise ValueError(
                    f"`timeouts` contains unexpected keys: {sorted(unknown)}; "
                    f"allowed keys are {sorted(allowed_keys)}"
                )

        # ---- base_url ----------------------------------------------------
        if (url := data.get("base_url")) is not None:
            if not isinstance(url, str) or not is_url(url):
                raise ValueError("`base_url` must be a well-formed URL")

        # ---- drivers ------------------------------------------------------
        if (drivers := data.get("drivers")) is not None:
            if not isinstance(drivers, list):
                raise ValueError("`drivers` must be a list of driver specifications")

            required_driver_keys = {"name", "browser", "headless", "window_size"}

            for idx, driver in enumerate(drivers):
                if not isinstance(driver, Mapping):
                    raise ValueError(f"driver #{idx} must be a mapping")

                missing = required_driver_keys - set(driver)
                extra = set(driver) - required_driver_keys
                if missing or extra:
                    raise ValueError(
                        f"driver #{idx} keys mismatch - missing: {sorted(missing)}, "
                        f"unexpected: {sorted(extra)}"
                    )

                # Validate window size
                ws = driver["window_size"].strip()
                if ws != "full" and not is_int_pair(ws):
                    raise ValueError(
                        f'driver #{idx} `window_size` must be "full" or an int pair '
                        f'(e.g. "1024,768"); got: {ws!r}'
                    )
