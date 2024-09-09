import logging

from .tv_service import TVService


class PowerIntentService:
    """
    Asynchronous service class to handle 'Power On' and 'Power Off' intents for Sony Bravia TVs.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    async def handle_power_on_intent(self, device_config: dict) -> bool:
        """
        Asynchronously handle the 'Power On' intent for the specified device.

        Args:
            device_config (dict): The configuration of the TV to be powered on.

        Returns:
            bool: True if the TV was successfully powered on, False otherwise.
        """
        self.logger.info("Handling Power On intent for device: %s", device_config["device_id"])
        tv_service = TVService(device_config)
        try:
            await tv_service.turn_on()
            self.logger.info("TV %s has been powered on.", device_config["device_id"])
            return True
        except Exception as e:
            self.logger.error("Failed to connect to TV %s: %s", device_config["device_id"], e)
            return False

    async def handle_power_off_intent(self, device_config: dict) -> bool:
        """
        Asynchronously handle the 'Power Off' intent for the specified device.

        Args:
            device_config (dict): The configuration of the TV to be powered off.

        Returns:
            bool: True if the TV was successfully powered off, False otherwise.
        """
        self.logger.info("Handling Power Off intent for device: %s", device_config["device_id"])
        tv_service = TVService(device_config)
        try:
            await tv_service.turn_off()
            self.logger.info("TV %s has been powered off.", device_config["device_id"])
            return True
        except Exception as e:
            self.logger.error("Failed to connect to TV %s: %s", device_config["device_id"], e)
            return False

