from abc import ABC, abstractmethod

class IotPlugin(ABC):
    """
    Abstract base class for IoT plugins. All plugins must implement the defined methods.
    """

    @abstractmethod
    async def initialize(self):
        """
        This method should be implemented to handle any initialization logic
        for the plugin, like setting up connections or loading configurations.
        """
        pass

    @abstractmethod
    def can_handle_topic(self, topic: str) -> bool:
        """
        Returns whether this plugin can handle the given topic.
        """
        pass

    @abstractmethod
    def get_topics(self) -> list:
        """
        Returns a list of MQTT topics that this plugin should handle.

        Returns:
        - list: A list of topics the plugin subscribes to (e.g., "domus/devices/tv/#").
        """
        pass

    @abstractmethod
    async def process_message(self, topic: str, payload: str):
        """
        Processes the message received for the plugin.

        Parameters:
        - topic (str): The MQTT topic the message was received on.
        - payload (str): The message payload received on the topic.
        """
        pass

    @abstractmethod
    async def shutdown(self):
        """
        This method should handle cleanup and shutdown logic for the plugin.
        """
        pass
