from enum import Enum
from typing import Union

import yaml
from loguru import logger


class ConfigType(Enum):
    """enum for choosing configuration type"""

    WEB = "web"
    API = "api"


class Configuration:
    """class that handles grabbing dictionary data from config yaml
    files
    """

    config_data: Union[dict, None] = None

    @classmethod
    def set_config_data(cls, path: str) -> None:
        """sets the config_data attribute to the dict
        value from the yaml

        Args:
            path (str): path to the yaml file
        """
        with open(path, "r", encoding="utf8") as f:
            data = yaml.load(f, Loader=yaml.SafeLoader)
        cls.config_data = data

    @classmethod
    def get_config(cls, config_type: ConfigType) -> Union[dict, None]:
        """returns a dict based on the ConfigType

        Args:
            config_type (ConfigType):

        Raises:
            ValueError: raised when run before set_config_data

        Returns:
            Union[dict, None]: returns None if the config does not have the
            targeted value
        """
        if cls.config_data is None:
            raise ValueError("set_config_data must be run first")

        target_config = cls.config_data.get(config_type.value)
        if target_config is None:
            logger.warning(f"no configuration found for: {config_type}")
        return target_config
