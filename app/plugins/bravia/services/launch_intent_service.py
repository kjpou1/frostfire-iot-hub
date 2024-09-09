import logging
import os

from app.config import Config
from .tv_service import TVService
from ..utils.tv_app_mapper import TVAppMapper

class LaunchIntentService:
    """
    Asynchronous service class to handle launch intents for Sony Bravia TVs.

    This class interacts with the TVService to manage the launch state of the TV based on
    intents received from an Alexa skill or similar service.
    """

    # Internal mapping of friendly command names to TV commands
    _command_mappings = {
        "power": "Power",
        "input": "Input",
        "syncmenu": "SyncMenu",
        "hdmi1": "Hdmi1",
        "hdmi2": "Hdmi2",
        "hdmi3": "Hdmi3",
        "hdmi4": "Hdmi4",
        "num1": "Num1",
        "num2": "Num2",
        "num3": "Num3",
        "num4": "Num4",
        "num5": "Num5",
        "num6": "Num6",
        "num7": "Num7",
        "num8": "Num8",
        "num9": "Num9",
        "num0": "Num0",
        "dot": "Dot(.)",
        "cc": "CC",
        "red": "Red",
        "green": "Green",
        "yellow": "Yellow",
        "blue": "Blue",
        "up": "Up",
        "down": "Down",
        "right": "Right",
        "left": "Left",
        "confirm": "Confirm",
        "help": "Help",
        "display": "Display",
        "options": "Options",
        "back": "Back",
        "home": "Home",
        "volumeup": "VolumeUp",
        "volumedown": "VolumeDown",
        "mute": "Mute",
        "audio": "Audio",
        "channelup": "ChannelUp",
        "channeldown": "ChannelDown",
        "play": "Play",
        "pause": "Pause",
        "stop": "Stop",
        "flashplus": "FlashPlus",
        "flashminus": "FlashMinus",
        "prev": "Prev",
        "next": "Next",
    }

    def __init__(self, plugin_directory):
        """
        Initialize the LaunchIntentService.

        Sets up logging for the service to track intent handling and errors.
        """
        self.logger = logging.getLogger(__name__)
        self.config = Config()
        self.tv_app_mapper = TVAppMapper()

        # Ensure the plugin directory contains the 'resources' subdirectory
        if not plugin_directory.endswith('resources'):
            resources_dir = os.path.join(plugin_directory, 'resources')
        else:
            resources_dir = plugin_directory

        if not os.path.isdir(resources_dir):
            self.logger.error(f"Resources directory not found in {resources_dir}.")
        # else:
        #     self.logger.info(f"Loading Alexa app mappings from {resources_dir}")

        # Load Alexa app mappings only once at initialization
        alexa_apps_file_path = os.path.join(resources_dir, 'alexa_apps.json')
        self.tv_app_mapper.load_alexa_apps(alexa_apps_file_path)
        
    async def launch_app(self, device, alexa_identifier):
        """
        Asynchronously launch an app on the specified device using Alexa identifier.

        Args:
            device (str): The identifier of the TV to be controlled.
            alexa_identifier (str): The Alexa app identifier to launch.

        Returns:
            bool: True if the app was successfully launched, False otherwise.
        """
        self.logger.info(
            "Launching app with Alexa identifier '%s' on device: %s",
            alexa_identifier,
            device,
        )

        tv_service = TVService(device)
        # Dynamically load TV apps using the TVService
        try:
            app_info = await tv_service.get_app_list()  # Use TVService to get app list
            if app_info:
                self.tv_app_mapper.set_tv_apps(app_info)  # Update TV app mappings
            else:
                self.logger.error("Received an empty app list from TV.")
                return False
        except Exception as e:
            self.logger.error("Failed to load TV app list: %s", e)
            return False

        # Convert Alexa app identifier to TV app identifier using TVAppMapper
        tv_app_identifier = self.tv_app_mapper.get_tv_app_uri_by_name_or_identifier(
            alexa_identifier
        )

        if not tv_app_identifier:
            self.logger.error(
                "No matching TV app identifier found for Alexa identifier: %s",
                alexa_identifier,
            )
            return False

        try:
            if tv_app_identifier.startswith("__") and tv_app_identifier.endswith("__"):
                # Extract command without the underscores
                command_key = tv_app_identifier.strip("__").lower()
                command = self._command_mappings.get(command_key)

                if command:
                    self.logger.info(
                        "Executing goto command '%s' for TV input '%s'.",
                        command_key,
                        command,
                    )
                    await tv_service.goto(command)
                else:
                    self.logger.error(
                        "Invalid command '%s' received; no matching TV command found.",
                        command_key,
                    )
                    return False
            else:
                # Launch the app using the resolved TV app identifier
                await tv_service.launch_app(tv_app_identifier)

            return True
        except Exception as e:
            self.logger.error(
                "Failed to launch app or execute command '%s' on device %s: %s",
                tv_app_identifier,
                device,
                e,
            )
            return False
