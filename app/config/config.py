import logging
import os

from dotenv import load_dotenv

from app.models import SingletonMeta


class Config(metaclass=SingletonMeta):

    _is_initialized = False

    def __init__(self):
        load_dotenv()  # Load environment variables from .env file
        # Prevent re-initialization
        if not self._is_initialized:
            # Initialize other configuration settings here
            self.logger = logging.getLogger(__name__)

    @classmethod
    def initialize(cls):
        # Convenience method to explicitly initialize the Config
        # This method can be expanded to include more initialization parameters if needed
        cls()

    @staticmethod
    def get(key, default=None):
        return os.getenv(key, default)
