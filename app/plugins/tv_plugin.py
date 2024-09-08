import json
import logging
from app.plugins.plugin_interface import IotPlugin

class TVPlugin(IotPlugin):
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def initialize(self):
        """
        Initialization logic for the TV plugin.
        This can include setting up any connections or loading TV-specific configurations.
        """
        self.logger.info("Initializing TV Plugin...")

    def can_handle_topic(self, topic: str) -> bool:
        """
        Determine if this plugin can handle the given topic.
        We assume TV-related topics follow a pattern like 'domus/devices/tv/#'
        """
        #return "domus/devices/tv/" in topic
        return False

    def get_topics(self) -> list:
        """
        Return the list of topics that this plugin handles.
        """
        return ["domus/devices/tv/#"]

    async def process_message(self, topic: str, payload: str):
        """
        Processes TV-related messages. The payload is expected to be a JSON string 
        with a power state like {"powerState": "ON"} or {"powerState": "OFF"}.
        """
        try:
            # Parse the JSON payload
            data = json.loads(payload)
            power_state = data.get("powerState")

            if power_state == "ON":
                self.logger.info("Turning TV ON")
                # Logic to turn the TV on
            elif power_state == "OFF":
                self.logger.info("Turning TV OFF")
                # Logic to turn the TV off
            else:
                self.logger.warning("Unrecognized power state: %s", power_state)

        except json.JSONDecodeError:
            self.logger.error("Failed to decode TV message payload: %s", payload)


    async def power_on(self):
        """Turn the TV on."""
        self.logger.info("Turning TV on...")
        # Add logic for turning the TV on

    async def power_off(self):
        """Turn the TV off."""
        self.logger.info("Turning TV off...")
        # Add logic for turning the TV off

    async def shutdown(self):
        """
        Clean-up logic for the plugin during shutdown.
        """
        self.logger.info("Shutting down TV Plugin...")
