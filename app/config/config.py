import logging
import os
from dotenv import load_dotenv
from app.models.singleton import SingletonMeta  # Adjust the import path as necessary

class Config(metaclass=SingletonMeta):
    _is_initialized = False

    def __init__(self):
        load_dotenv()  # Load environment variables from .env file
        # Prevent re-initialization
        if not self._is_initialized:
            self.logger = logging.getLogger(__name__)
            self.MQTT_BROKER = self.get('MQTT_BROKER', 'localhost')
            self.MQTT_PORT = int(self.get('MQTT_PORT', 1883))
            self.MQTT_TOPIC = self.get('MQTT_TOPIC', 'iot/devices')
            self._is_initialized = True

    @classmethod
    def initialize(cls):
        # Convenience method to explicitly initialize the Config
        # This method can be expanded to include more initialization parameters if needed
        cls()

    @staticmethod
    def get(key, default=None):
        return os.getenv(key, default)
