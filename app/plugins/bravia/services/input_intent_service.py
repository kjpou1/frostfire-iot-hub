import logging
import os

from app.plugins.bravia.services.tv_service import TVService
from app.plugins.bravia.utils.tv_input_mapper import TVInputMapper


class InputIntentService:
    """
    Asynchronous service class to handle input change intents for Sony Bravia TVs.
    """

    def __init__(self, plugin_directory):
        """
        Initialize the InputIntentService.
        """
        self.logger = logging.getLogger(__name__)
        # Ensure the plugin directory contains the 'resources' subdirectory
        if not plugin_directory.endswith('resources'):
            resources_dir = os.path.join(plugin_directory, 'resources')
        else:
            resources_dir = plugin_directory

        if not os.path.isdir(resources_dir):
            self.logger.error(f"Resources directory not found in {resources_dir}.")
        # else:
        #     self.logger.info(f"Loading Alexa input mappings from {resources_dir}")

        # Load Alexa input mappings
        input_mappings_file_path = os.path.join(resources_dir, 'input_mappings.json')
        self.tv_input_mapper = TVInputMapper(input_mappings_file_path)

    async def select_input(self, device: dict, input_source: str):
        """
        Asynchronously change the input source on the specified device.

        Args:
            device (dict): The device configuration dictionary.
            input_source (str): The input source to switch to (e.g., 'HDMI 2').

        Returns:
            bool: True if the input source was successfully changed, False otherwise.
        """
        device_id = device.get("device_id") or device.get("object_id")
        self.logger.info(
            "Changing input to '%s' on device: %s", input_source, device_id
        )

        tv_service = TVService(device)

        try:
            tv_source = self.tv_input_mapper.get_tv_input_command(input_source)
            await tv_service.change_input(tv_source)
            return True
        except Exception as e:
            self.logger.error(
                "Failed to change input to '%s' on device %s: %s",
                input_source,
                device_id,
                e,
            )
            return False

