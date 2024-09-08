import logging
import os
from dotenv import load_dotenv
from app.models.singleton import SingletonMeta  # Adjust the import path as necessary

class Config(metaclass=SingletonMeta):
    _is_initialized = False

    def __init__(self):
        load_dotenv()  # Load environment variables from .env file
        if not self._is_initialized:
            self.logger = logging.getLogger(__name__)
            
            # Store the configuration values in private variables
            self._mqtt_broker = self.get('MQTT_BROKER', 'localhost')
            self._mqtt_port = int(self.get('MQTT_PORT', 1883))
            self._mqtt_topic = self.get('MQTT_TOPIC', 'iot/devices')

            # SSL key and cert with development defaults
            self._ssl_keyfile = self.get('SSL_KEYFILE', 'ssl/private/insecure.key')
            self._ssl_certfile = self.get('SSL_CERTFILE', 'ssl/certs/insecure.pem')

            # Host and Port for FastAPI/Uvicorn
            self._host = self.get('HOST', '127.0.0.1')  # Default local host
            self._port = int(self.get('PORT', 8084))  # Default to 8084
            
            # Plugins directory path from .env
            self._plugins_dir = self.get('PLUGINS_DIR', 'app/plugins')            

            self._is_initialized = True

    @classmethod
    def initialize(cls):
        # Convenience method to explicitly initialize the Config
        cls()

    @staticmethod
    def get(key, default=None):
        return os.getenv(key, default)

    # Property for MQTT_BROKER
    @property
    def MQTT_BROKER(self):
        return self._mqtt_broker

    # Property for MQTT_PORT
    @property
    def MQTT_PORT(self):
        return self._mqtt_port

    # Property for MQTT_TOPIC
    @property
    def MQTT_TOPIC(self):
        return self._mqtt_topic

    # Property for SSL_KEYFILE
    @property
    def SSL_KEYFILE(self):
        return self._ssl_keyfile

    # Property for SSL_CERTFILE
    @property
    def SSL_CERTFILE(self):
        return self._ssl_certfile

    # Property for HOST
    @property
    def HOST(self):
        return self._host

    # Property for PORT
    @property
    def PORT(self):
        return self._port

    # Property for PLUGINS_DIR
    @property
    def PLUGINS_DIR(self):
        return self._plugins_dir