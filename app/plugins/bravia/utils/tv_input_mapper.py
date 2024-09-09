import logging
from typing import Dict, Optional
from .json_utils import JsonUtils

class TVInputMapper:
    """
    Utility class for mapping Alexa input values to TV input commands.
    """

    def __init__(self, input_mappings_file_path: str):
        """
        Initializes the TVInputMapper by loading the input mappings from a JSON configuration file.

        The configuration file path is passed during initialization, and the input mappings
        are loaded into a dictionary for quick lookups.
        """
        self.logger = logging.getLogger(__name__)
        self.input_mappings = self._load_input_mappings(input_mappings_file_path)

    def _load_input_mappings(self, input_mappings_file_path: str) -> Dict[str, str]:
        """
        Load input mappings from the JSON configuration file specified by the provided file path.

        Returns:
            dict: A dictionary containing the Alexa to TV input mappings.
                  Returns an empty dictionary if the file cannot be loaded.
        """
        data = JsonUtils.load_json_file(input_mappings_file_path)  # Use JsonUtils for file loading

        if data:
            self.logger.info("Input mappings loaded successfully.")
            return data.get("input_mappings", {})
        else:
            self.logger.error(f"Failed to load input mappings from {input_mappings_file_path}")
            return {}

    def get_tv_input_command(self, alexa_input: str) -> Optional[str]:
        """
        Convert an Alexa input value to the corresponding TV input command.

        Args:
            alexa_input (str): The Alexa input value (e.g., 'HDMI 1', 'DVD').

        Returns:
            Optional[str]: The TV command name that corresponds to the Alexa input,
                           or None if no mapping is found.
        """
        if not alexa_input:
            self.logger.warning("No Alexa input provided.")
            return None

        tv_input_command = self.input_mappings.get(alexa_input.upper())
        if tv_input_command:
            self.logger.info(
                "Mapped Alexa input '%s' to TV input command '%s'.",
                alexa_input,
                tv_input_command,
            )
        else:
            self.logger.warning("No mapping found for Alexa input '%s'.", alexa_input)
        return tv_input_command
