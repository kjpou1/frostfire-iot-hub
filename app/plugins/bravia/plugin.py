import fnmatch
import json
import logging
import os
from app.plugins.bravia.handlers.input_intent_handler import InputIntentHandler
from app.plugins.bravia.handlers.launch_intent_handler import LaunchIntentHandler
from app.plugins.bravia.handlers.playback_intent_handler import PlaybackIntentHandler
from app.plugins.bravia.handlers.speaker_intent_handler import SpeakerIntentHandler
from app.plugins.bravia.services.input_intent_service import InputIntentService
from app.plugins.bravia.services.launch_intent_service import LaunchIntentService
from app.plugins.bravia.services.playback_intent_service import PlaybackIntentService
from app.plugins.bravia.services.power_intent_service import PowerIntentService
from app.plugins.bravia.services.speaker_intent_service import SpeakerIntentService
from app.plugins.plugin_interface import IotPlugin
from app.plugins.bravia.handlers.power_intent_handler import PowerIntentHandler

class BraviaPlugin(IotPlugin):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.bravia_topics = [
            "domus/devices/tv/+/power/set",
            "domus/devices/tv/+/speaker/volume/+",
            "domus/devices/tv/+/speaker/mute/set",
            "domus/devices/tv/+/playback/+",
            "domus/devices/tv/+/launcher",
            "domus/devices/tv/+/input",
        ]
        
        self.devices = []  # To store device configurations

        # Dynamically determine the plugin's base directory
        self.plugin_directory = os.path.dirname(os.path.abspath(__file__))
        
        # Define handlers for different command categories
        self.power_handler = PowerIntentHandler(PowerIntentService())
        self.speaker_handler = SpeakerIntentHandler(SpeakerIntentService())
        self.playback_handler = PlaybackIntentHandler(PlaybackIntentService())
        self.launch_handler = LaunchIntentHandler(LaunchIntentService(self.plugin_directory))
        self.input_handler = InputIntentHandler(InputIntentService(self.plugin_directory))
                

    async def initialize(self):
        """
        Initialization logic for the Bravia plugin.
        This can include setting up any connections or loading TV-specific configurations.
        """
        self.logger.info("Initializing Bravia Plugin...")
        
        # Load config.json from the plugin directory
        config_file_path = os.path.join(os.path.dirname(__file__), 'config.json')
        
        if not os.path.exists(config_file_path):
            self.logger.error("Config file not found at path: %s", config_file_path)
            return
        
        try:
            with open(config_file_path, 'r') as f:
                config_data = json.load(f)
                
            # Validate the device configurations
            if 'devices' not in config_data:
                self.logger.error("No devices found in config.json")
                return
            
            for device in config_data['devices']:
                if 'device_id' not in device and 'object_id' not in device:
                    self.logger.error("Device must contain at least one of 'device_id' or 'object_id'")
                    continue  # Skip invalid entries
                
                self.devices.append(device)  # Add the valid device to the list

            self.logger.info(f"Loaded {len(self.devices)} devices from config.json")

        except json.JSONDecodeError as e:
            self.logger.error("Failed to parse config.json: %s", e)        

    def can_handle_topic(self, topic: str) -> bool:
        """
        Determine if this plugin can handle the given topic.
        
        This function uses the `fnmatch` module to match the incoming topic with the topics
        that the plugin is subscribed to. Since MQTT topics can contain wildcards (`+` and `#`),
        we translate those wildcards to the equivalent shell-style wildcards supported by `fnmatch`:
        
        - The `+` MQTT wildcard is converted to `*` in `fnmatch`, which matches any single-level element in the topic.
        - The `#` MQTT wildcard is converted to `**` in `fnmatch`, which matches multiple levels in the topic hierarchy.
        
        For example:
        - `domus/devices/tv/+/power/set` will match `domus/devices/tv/uuid:12345/power/set`
        - `domus/devices/#` will match both `domus/devices/tv/1` and `domus/devices/tv/1/power/set`
        
        Parameters:
        - topic (str): The MQTT topic of the incoming message.
        
        Returns:
        - bool: True if the plugin can handle the topic, False otherwise.
        """
        for t in self.bravia_topics:
            # Convert MQTT wildcards (+ -> *, # -> **) to fnmatch-compatible wildcards
            pattern = t.replace("+", "*").replace("#", "**")
            if fnmatch.fnmatch(topic, pattern):
                return True
        return False

    
    def get_topics(self) -> list:
        """
        Return the list of topics that this plugin handles.
        """
        return self.bravia_topics

    async def process_message(self, topic: str, payload_str: str):
        """
        Process the received message for a specific topic.
        
        Parameters:
        - topic: MQTT topic received
        - payload_str: JSON payload (received as a string) for the topic
        """
        try:
            # Parse the topic to extract necessary parts
            topic_parts = topic.split("/")

            if len(topic_parts) >= 5:
                base_topic, devices, device_type, device_id, category = topic_parts[0:5]

                device_id = topic_parts[3] if len(topic_parts) > 3 else None

                if not device_id:
                    self.logger.error("Device ID not found in topic")
                    return

                # Find the matching device by either device_id or object_id
                device = self.get_device_by_id(device_id)

                if not device:
                    self.logger.warning("No matching device found for ID: %s", device_id)
                    return
            
                # Check if the topic is specifically for TV devices power set
                if (
                    device_type == "tv"
                    and category == "power"
                    and len(topic_parts) == 6
                    and topic_parts[5] == "set"
                ):
                    self.logger.info(f"Handling power command for {device_id}")
                    await self.power_handler.handle_power_set(
                        device_type, device, payload_str
                    )

                # Handling Speaker Commands
                elif (
                    device_type == "tv" and category == "speaker" and len(topic_parts) >= 7
                ):
                    subcategory = topic_parts[5]  # 'volume' or 'mute'
                    action = topic_parts[6]
                    self.logger.info(f"Handling speaker command: {subcategory} - {action}")
                    await self.speaker_handler.handle_speaker_command(
                        device_type, device, subcategory, action, payload_str
                    )

                # Handling Playback Commands
                elif (
                    device_type == "tv" and category == "playback" and len(topic_parts) >= 6
                ):
                    action = topic_parts[5]
                    self.logger.info(f"Handling playback command: {action}")
                    await self.playback_handler.handle_playback_command(
                        device_type, device, action, payload_str
                    )

                # Handling Launch Commands
                elif device_type == "tv" and category == "launcher":
                    self.logger.info(f"Handling launch command for {device_id}")
                    await self.launch_handler.handle_launch_command(
                        device_type, device, payload_str
                    )

                # Check if the topic is for TV input change
                elif device_type == "tv" and category == "input":
                    self.logger.info(f"Handling input change for {device_id}")
                    await self.input_handler.handle_input_change(
                        device_type, device, payload_str
                    )
                else:
                    self.logger.warning(f"Unrecognized command category: {category}")
            else:
                self.logger.error(f"Malformed topic: {topic}")

        except json.JSONDecodeError:
            self.logger.error(f"Failed to decode payload for topic {topic}: {payload_str}")
        except Exception as e:
            self.logger.error(f"Error processing message on topic {topic}: {e}")

    def get_device_by_id(self, identifier: str):
        """
        Retrieve a device by either device_id or object_id.
        
        :param identifier: The device_id or object_id to search for.
        :return: The device configuration if found, else None.
        """
        for device in self.devices:
            if device.get('device_id') == identifier or device.get('object_id') == identifier:
                return device
        return None
    
    async def shutdown(self):
        """
        Clean-up logic for the plugin during shutdown.
        """
        self.logger.info("Shutting down Bravia Plugin...")
