import logging
from .tv_service import TVService

class SpeakerIntentService:
    """
    Asynchronous service class to handle 'Volume' intents for Sony Bravia TVs.

    This class interacts with the TVService to manage the volume state of the TV based on
    intents received from an Alexa skill or similar service.
    """

    def __init__(self):
        """
        Initialize the SpeakerIntentService.

        Sets up logging for the service to track intent handling and errors.
        """
        self.logger = logging.getLogger(__name__)

    async def handle_volume_intent(self, device: dict, volume_command: str, volume: int = None, step: int = 1) -> bool:
        """
        Asynchronously handle the 'Volume' intent for the specified device.

        This method creates an instance of TVService for the given device and attempts
        to adjust the volume based on the volume_command and volume or step (if applicable).
        Logs success or failure.

        Args:
            device (dict): The device configuration dictionary containing details for the TV.
            volume_command (str): The volume command (e.g., 'increase', 'decrease', 'mute', 'unmute', 'set').
            volume (int, optional): The volume to set if the volume_command is 'set'.
            step (int, optional): The step size for volume increase or decrease. Default is 1.

        Returns:
            bool: True if the volume was successfully adjusted, False otherwise.
        """
        device_id = device.get("device_id") or device.get("object_id")
        self.logger.info(
            "Handling Volume intent for device: %s with command: %s, volume: %s, step: %s",
            device_id,
            volume_command,
            volume,
            step,
        )

        # Create TVService instance using the device configuration dictionary
        tv_service = TVService(device)

        try:
            # Adjust volume based on the command provided
            if volume_command == "increase":
                await tv_service.volume_up(step)  # Increase the volume by step
            elif volume_command == "decrease":
                await tv_service.volume_down(step)  # Decrease the volume by step
            elif volume_command == "mute":
                await tv_service.mute()  # Mute the TV
            elif volume_command == "unmute":
                await tv_service.unmute()  # Unmute the TV
            elif volume_command == "set":
                if volume is not None and isinstance(volume, int):
                    await tv_service.set_volume(volume)  # Set the volume to the specified level
                else:
                    self.logger.error("Invalid or missing volume for 'set' command.")
                    return False
            else:
                # Log an error if an invalid volume command is received
                self.logger.error("Invalid volume command: %s", volume_command)
                return False

            # Log success and return True if the volume adjustment was successful
            self.logger.info("TV %s volume adjusted: %s", device_id, volume_command)
            return True

        except Exception as e:
            # Log and return False if there was an issue adjusting the volume
            self.logger.error(
                "Failed to adjust volume on TV %s for command %s: %s",
                device_id,
                volume_command,
                e,
            )
            return False
