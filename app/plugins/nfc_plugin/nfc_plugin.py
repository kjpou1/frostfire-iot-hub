# /plugins/nfc_plugin/nfc_plugin.py
import fnmatch
import logging
from app.plugins.plugin_interface import IotPlugin

class NfcPlugin(IotPlugin):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.nfc_topics = [
            "domus/devices/nfc/+",
        ]
    
    async def initialize(self):
        self.logger.info("Initializing NFC Plugin...")
    
    def can_handle_topic(self, topic: str) -> bool:
        """
        Determine if this plugin can handle the given topic.
        
        This function uses the `fnmatch` module to match the incoming topic with the topics
        that the plugin is subscribed to. Since MQTT topics can contain wildcards (`+` and `#`),
        we translate those wildcards to the equivalent shell-style wildcards supported by `fnmatch`:
        
        - The `+` MQTT wildcard is converted to `*` in `fnmatch`, which matches any single-level element in the topic.
        - The `#` MQTT wildcard is converted to `**` in `fnmatch`, which matches multiple levels in the topic hierarchy.
        
        For example:
        - `domus/devices/nfc/+/power/set` will match `domus/devices/tv/uuid:12345/power/set`
        
        Parameters:
        - topic (str): The MQTT topic of the incoming message.
        
        Returns:
        - bool: True if the plugin can handle the topic, False otherwise.
        """
        for t in self.nfc_topics:
            # Convert MQTT wildcards (+ -> *, # -> **) to fnmatch-compatible wildcards
            pattern = t.replace("+", "*").replace("#", "**")
            if fnmatch.fnmatch(topic, pattern):
                return True
        return False
    
    def get_topics(self) -> list:
        """
        Return the list of topics that this plugin handles.
        """
        return self.nfc_topics
    
    async def process_message(self, topic: str, payload: str):
        # Simple logging functionality to test message reception
        print(f"Test Message Received on topic {topic}: {payload}")

    async def shutdown(self):
        print("NFC Plugin shutting down.")
