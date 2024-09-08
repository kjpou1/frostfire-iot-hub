import json
import logging

from pybravia import BraviaClient, BraviaError


class TVService:
    """
    Asynchronous service class to handle all interactions with the Sony Bravia TV.
    """

    def __init__(self, device_config: dict):
        """
        Initialize the TVService with the device-specific settings from the configuration.

        Args:
            device_config (dict): The configuration dictionary of the TV device being controlled.
        """
        self.logger = logging.getLogger(__name__)

        # Load the necessary device configuration from the provided dictionary
        self.tv_ip_address = device_config.get('ip_address')
        self.client_id = device_config.get('client_id')
        self.nick_name = device_config.get('nick_name')
        self.pin = str(device_config.get('pin')) if device_config.get('pin') is not None else None  # Convert pin to string
        self.psk = device_config.get('preshared_key')
        self.device_id = device_config.get('device_id', None)
        self.object_id = device_config.get('object_id', None)
        self.tv = None

        # Ensure either device_id or object_id exists
        if not self.device_id and not self.object_id:
            raise ValueError("Either 'device_id' or 'object_id' must be specified in the device configuration.")

    async def connect_to_tv(self):
        """
        Asynchronously connect to the Sony Bravia TV using the configured credentials.

        Returns:
            BraviaClient: An instance of BraviaClient if the connection is successful.
            None: If the connection fails.
        """
        try:
            client = BraviaClient(self.tv_ip_address)
            if self.pin:
                await client.connect(
                    pin=self.pin, clientid=self.client_id, nickname=self.nick_name
                )
            else:
                await client.connect(psk=self.psk)
            return client
        except BraviaError as e:
            self.logger.error("Failed to connect to TV: %s", e)
            return None

    async def turn_on(self):
        """
        Asynchronously turn on the TV.
        """
        client = await self.connect_to_tv()
        if client:
            try:
                await client.turn_on()
                self.logger.info("TV turned on successfully.")
            except BraviaError as e:
                self.logger.error("Failed to turn on TV: %s", e)
            finally:
                await client.disconnect()
        else:
            self.logger.error("TV is not connected.")

    async def turn_off(self):
        """
        Asynchronously turn off the TV.
        """
        client = await self.connect_to_tv()
        if client:
            try:
                await client.turn_off()
                self.logger.info("TV turned off successfully.")
            except BraviaError as e:
                self.logger.error("Failed to turn off TV: %s", e)
            finally:
                await client.disconnect()
        else:
            self.logger.error("TV is not connected.")

    async def set_volume(self, level: str):
        """
        Asynchronously set the TV volume to a specific level.

        Args:
            level (str): The volume level to set (e.g., '10', '+1', '-1').
        """
        client = await self.connect_to_tv()
        if client:
            try:
                await client.volume_level(level)
                self.logger.info("TV volume set to %s.", level)
            except BraviaError as e:
                self.logger.error("Failed to set TV volume: %s", e)
            finally:
                await client.disconnect()
        else:
            self.logger.error("TV is not connected.")

    async def volume_up(self, step: int = 1):
        """
        Asynchronously increase the TV volume by a specific step.

        Args:
            step (int): The number of volume steps to increase (default is 1).
        """
        level = f"+{step}"
        await self.set_volume(level)

    async def volume_down(self, step: int = 1):
        """
        Asynchronously decrease the TV volume by a specific step.

        Args:
            step (int): The number of volume steps to decrease (default is 1).
        """
        level = f"-{step}"
        await self.set_volume(level)

    async def mute(self):
        """
        Asynchronously mute the TV.
        """
        client = await self.connect_to_tv()
        if client:
            try:
                await client.volume_mute(True)
                self.logger.info("TV muted successfully.")
            except BraviaError as e:
                self.logger.error("Failed to mute TV: %s", e)
            finally:
                await client.disconnect()
        else:
            self.logger.error("TV is not connected.")

    async def unmute(self):
        """
        Asynchronously unmute the TV.
        """
        client = await self.connect_to_tv()
        if client:
            try:
                await client.volume_mute(False)
                self.logger.info("TV unmuted successfully.")
            except BraviaError as e:
                self.logger.error("Failed to unmute TV: %s", e)
            finally:
                await client.disconnect()
        else:
            self.logger.error("TV is not connected.")

    # Additional methods (play, pause, stop, etc.) would also work similarly
