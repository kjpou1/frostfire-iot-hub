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

   # Playback Control Methods

    async def play(self):
        """
        Asynchronously start or resume playback on the TV.
        """
        client = await self.connect_to_tv()
        if client:
            try:
                await client.play()
                self.logger.info("Playback started/resumed successfully.")
            except BraviaError as e:
                self.logger.error("Failed to start/resume playback: %s", e)
            finally:
                await client.disconnect()
        else:
            self.logger.error("TV is not connected.")

    async def pause(self):
        """
        Asynchronously pause playback on the TV.
        """
        client = await self.connect_to_tv()
        if client:
            try:
                await client.pause()
                self.logger.info("Playback paused successfully.")
            except BraviaError as e:
                self.logger.error("Failed to pause playback: %s", e)
            finally:
                await client.disconnect()
        else:
            self.logger.error("TV is not connected.")

    async def stop(self):
        """
        Asynchronously stop playback on the TV.
        """
        client = await self.connect_to_tv()
        if client:
            try:
                await client.stop()
                self.logger.info("Playback stopped successfully.")
            except BraviaError as e:
                self.logger.error("Failed to stop playback: %s", e)
            finally:
                await client.disconnect()
        else:
            self.logger.error("TV is not connected.")

    async def rewind(self):
        """
        Asynchronously rewind playback on the TV.
        """
        client = await self.connect_to_tv()
        if client:
            try:
                # await client.rewind()
                self.logger.info("Playback rewound successfully.")
            except BraviaError as e:
                self.logger.error("Failed to rewind playback: %s", e)
            finally:
                await client.disconnect()
        else:
            self.logger.error("TV is not connected.")

    async def fast_forward(self):
        """
        Asynchronously fast forward playback on the TV.
        """
        client = await self.connect_to_tv()
        if client:
            try:
                # await client.fast_forward()
                self.logger.info("Playback fast forwarded successfully.")
            except BraviaError as e:
                self.logger.error("Failed to fast forward playback: %s", e)
            finally:
                await client.disconnect()
        else:
            self.logger.error("TV is not connected.")

    async def start_over(self):
        """
        Asynchronously start playback from the beginning on the TV.
        """
        client = await self.connect_to_tv()
        if client:
            try:
                # await client.start_over()
                self.logger.info("Playback started over successfully.")
            except BraviaError as e:
                self.logger.error("Failed to start playback over: %s", e)
            finally:
                await client.disconnect()
        else:
            self.logger.error("TV is not connected.")

    async def previous(self):
        """
        Asynchronously skip to the previous item on the TV.
        """
        client = await self.connect_to_tv()
        if client:
            try:
                await client.previous_track()
                self.logger.info("Skipped to previous item successfully.")
            except BraviaError as e:
                self.logger.error("Failed to skip to previous item: %s", e)
            finally:
                await client.disconnect()
        else:
            self.logger.error("TV is not connected.")

    async def next(self):
        """
        Asynchronously skip to the next item on the TV.
        """
        client = await self.connect_to_tv()
        if client:
            try:
                await client.next_track()
                self.logger.info("Skipped to next item successfully.")
            except BraviaError as e:
                self.logger.error("Failed to skip to next item: %s", e)
            finally:
                await client.disconnect()
        else:
            self.logger.error("TV is not connected.")

    async def get_app_list(self):
        """
        Asynchronously retrieve the list of available applications from the TV.

        This method connects to the Sony Bravia TV using the BraviaClient, retrieves
        the list of available applications installed on the TV, and then disconnects
        from the TV. If the connection to the TV fails or retrieving the app list
        encounters an error, appropriate logging is performed.

        Returns:
            list: A list of dictionaries, where each dictionary contains information
                about an available application on the TV, such as the app name and URI.
                Returns None if the connection fails or the app list cannot be retrieved.

        Raises:
            BraviaError: If an error occurs while attempting to retrieve the application list.

        Example:
            apps = await tv_service.get_app_list()
            if apps:
                for app in apps:
                    print(f"App Name: {app['name']}, URI: {app['uri']}")
            else:
                print("Failed to retrieve the app list.")
        """
        client = await self.connect_to_tv()
        if client:
            try:
                return await client.get_app_list()
            except BraviaError as e:
                self.logger.error("Failed to get the application list: %s", e)
            finally:
                await client.disconnect()
        else:
            self.logger.error("TV is not connected.")

    async def launch_app(self, app_name):
        """
        Asynchronously launch an app on the TV.

        Args:
            app_name (str): The name of the app to launch.
        """
        client = await self.connect_to_tv()
        if client:
            try:
                await client.set_active_app(app_name)
                self.logger.info("App '%s' launched successfully.", app_name)
            except BraviaError as e:
                self.logger.error("Failed to launch app '%s': %s", app_name, e)
            finally:
                await client.disconnect()
        else:
            self.logger.error("TV is not connected.")

    async def get_source_list(self, scheme="extInput"):
        """
        Asynchronously retrieve the list of available input sources from the TV.

        This method connects to the Sony Bravia TV using the BraviaClient, retrieves
        the list of available input sources, and then disconnects from the TV. If the
        connection to the TV fails or retrieving the source list encounters an error,
        appropriate logging is performed.

        Returns:
            list: A list of dictionaries, where each dictionary contains information
                about an available input source on the TV, such as the source name and
                corresponding input identifier (e.g., HDMI 1, HDMI 2, etc.).
                Returns None if the connection fails or the source list cannot be retrieved.

        Raises:
            BraviaError: If an error occurs while attempting to retrieve the input source list.

        Example:
            sources = await tv_service.get_source_list()
            if sources:
                for source in sources:
                    print(f"Source Name: {source['title']}, ID: {source['source']}")
            else:
                print("Failed to retrieve the source list.")
        """
        client = await self.connect_to_tv()
        if client:
            try:
                return await client.get_source_list(scheme=scheme)
            except BraviaError as e:
                self.logger.error("Failed to get the source list: %s", e)
            finally:
                await client.disconnect()
        else:
            self.logger.error("TV is not connected.")

    async def change_input(self, input_source):
        """
        Asynchronously change the input source on the TV.

        Args:
            input_source (str): The input source to switch to (e.g., 'HDMI 2').
        """
        client = await self.connect_to_tv()
        if client:
            try:
                if await client.send_command(input_source):
                    self.logger.info(
                        "Input source changed to '%s' successfully.", input_source
                    )
                else:
                    self.logger.error(
                        "Failed to change input source to '%s'.", input_source
                    )
            except BraviaError as e:
                self.logger.error(
                    "Failed to change input source to '%s': %s", input_source, e
                )
            finally:
                await client.disconnect()
        else:
            self.logger.error("TV is not connected.")

    def write_dict_to_file(self, data, file_path):
        """
        Write a Python dictionary to a file using UTF-8 encoding.

        Args:
            data (dict): The dictionary to write to the file.
            file_path (str): The path to the file where the dictionary will be written.
        """
        try:
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
            print(f"Dictionary successfully written to {file_path}")
        except Exception as e:
            print(f"Error writing dictionary to file: {e}")

    async def goto(self, where):
        """
        Asynchronously launch an app on the TV.

        Args:
            app_name (str): The name of the app to launch.
        """
        client = await self.connect_to_tv()
        if client:
            try:
                if await client.send_command(where):
                    self.logger.info("Goto where '%s' successfully.", where)
                else:
                    self.logger.error("Failed to change input source to '%s'.", where)
            except BraviaError as e:
                self.logger.error("Failed to goto '%s': %s", where, e)
            finally:
                await client.disconnect()
        else:
            self.logger.error("TV is not connected.")
