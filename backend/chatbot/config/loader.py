import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, TextIO

from yaml import SafeLoader

logger = logging.getLogger(__name__)


class ConfigLoader:
    """
    Class responsible for loading configuration files with environment variable support.
    """

    def __init__(self, profile_name: str):
        """
        Initializes the ConfigLoader with the given profile name.

        :param profile_name: The name of the profile to load configuration for.
        """
        self.project_root = Path(__file__).parents[2]
        self.profile_file_name = f"settings-{profile_name}.yaml"
        self.path = self.project_root / self.profile_file_name

    def load(self) -> Dict[str, Any]:
        """
        Loads the configuration file, replacing environment variables as needed.

        :return: The loaded configuration as a dictionary.
        :raises TypeError: If the top-level of the config file is not a mapping.
        """
        with self.path.open("r") as f:
            config = self._load_yaml_with_env_vars(f)

        if not isinstance(config, dict):
            raise TypeError(f"Config file must have a top-level mapping: {self.path}")

        logger.info("Configuration successfully loaded")
        return config

    @staticmethod
    def _load_yaml_with_env_vars(stream: TextIO, environ: Dict[str, Any] = os.environ) -> Dict[str, Any]:
        """
        Loads YAML data from the stream, replacing environment variables.

        :param stream: The input stream to read the YAML data from.
        :param environ: A dictionary of environment variables.
        :return: The loaded YAML data as a dictionary.
        """
        loader = SafeLoader(stream)

        env_var_pattern = re.compile(r"\$\{(\w+)(?::([^}]*))?\}")

        def _load_env_var(loader, node) -> str:
            """
            Replaces environment variable placeholders with actual values.

            :param loader: The YAML loader.
            :param node: The node in the YAML file containing the environment variable placeholder.
            :return: The value of the environment variable or its default.
            :raises ValueError: If the environment variable is not set and no default is provided.
            """
            value = node.value
            match = env_var_pattern.match(value)
            if not match:
                raise ValueError(f"Invalid environment variable placeholder: {value}")

            env_var, default = match.groups()
            actual_value = environ.get(env_var, default)

            if actual_value is None:
                raise ValueError(f"Environment variable '{env_var}' is not set and no default value was provided")

            return actual_value

        loader.add_implicit_resolver("!env_var", env_var_pattern, None)
        loader.add_constructor("!env_var", _load_env_var)

        try:
            return loader.get_single_data()
        finally:
            loader.dispose()
