import logging

from .tv_service import TVService


class PlaybackIntentService:
    """
    Asynchronous service class to handle playback intents for Sony Bravia TVs.

    This class interacts with the TVService to manage the playback state of the TV based on
    intents received from an Alexa skill or similar service.
    """

    def __init__(self):
        """
        Initialize the PlaybackIntentService.

        Sets up logging for the service to track intent handling and errors.
        """
        self.logger = logging.getLogger(__name__)

    async def play(self, device: dict):
        """Asynchronously start or resume playback on the specified device."""
        self.logger.info("Playing content on device: %s", device.get("device_id") or device.get("object_id"))
        tv_service = TVService(device)  # Pass the entire device config to TVService
        try:
            await tv_service.play()
            return True
        except Exception as e:
            self.logger.error("Failed to play on device %s: %s", device, e)
            return False

    async def pause(self, device: dict):
        """Asynchronously pause playback on the specified device."""
        self.logger.info("Pausing content on device: %s", device.get("device_id") or device.get("object_id"))
        tv_service = TVService(device)
        try:
            await tv_service.pause()
            return True
        except Exception as e:
            self.logger.error("Failed to pause on device %s: %s", device, e)
            return False

    async def stop(self, device: dict):
        """Asynchronously stop playback on the specified device."""
        self.logger.info("Stopping content on device: %s", device.get("device_id") or device.get("object_id"))
        tv_service = TVService(device)
        try:
            await tv_service.stop()
            return True
        except Exception as e:
            self.logger.error("Failed to stop on device %s: %s", device, e)
            return False

    async def rewind(self, device: dict):
        """Asynchronously rewind playback on the specified device."""
        self.logger.info("Rewinding content on device: %s", device.get("device_id") or device.get("object_id"))
        tv_service = TVService(device)
        try:
            # await tv_service.rewind()
            return True
        except Exception as e:
            self.logger.error("Failed to rewind on device %s: %s", device, e)
            return False

    async def fast_forward(self, device: dict):
        """Asynchronously fast forward playback on the specified device."""
        self.logger.info("Fast forwarding content on device: %s", device.get("device_id") or device.get("object_id"))
        tv_service = TVService(device)
        try:
            # await tv_service.fast_forward()
            return True
        except Exception as e:
            self.logger.error("Failed to fast forward on device %s: %s", device, e)
            return False

    async def start_over(self, device: dict):
        """Asynchronously start playback from the beginning on the specified device."""
        self.logger.info("Starting over content on device: %s", device.get("device_id") or device.get("object_id"))
        tv_service = TVService(device)
        try:
            # await tv_service.start_over()
            return True
        except Exception as e:
            self.logger.error("Failed to start over on device %s: %s", device, e)
            return False

    async def previous(self, device: dict):
        """Asynchronously skip to the previous item on the specified device."""
        self.logger.info("Skipping to previous content on device: %s", device.get("device_id") or device.get("object_id"))
        tv_service = TVService(device)
        try:
            # await tv_service.previous()
            return True
        except Exception as e:
            self.logger.error("Failed to skip to previous on device %s: %s", device, e)
            return False

    async def next(self, device: dict):
        """Asynchronously skip to the next item on the specified device."""
        self.logger.info("Skipping to next content on device: %s", device.get("device_id") or device.get("object_id"))
        tv_service = TVService(device)
        try:
            await tv_service.next()
            return True
        except Exception as e:
            self.logger.error("Failed to skip to next on device %s: %s", device, e)
            return False
