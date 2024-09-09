import json
import logging

from ..services.playback_intent_service import PlaybackIntentService


class PlaybackIntentHandler:
    """
    A handler class to process playback directives for TV devices.
    """

    def __init__(self, playback_intent_service: PlaybackIntentService):
        """
        Initialize the PlaybackIntentHandler with the PlaybackIntentService.

        Args:
            playback_intent_service (PlaybackIntentService): The service responsible for handling playback intents.
        """
        self.logger = logging.getLogger(__name__)
        self.playback_intent_service = playback_intent_service

    async def handle_playback_command(
        self, device_type: str, device: dict, command: str, payload
    ):
        """
        Handle the playback command directive for a given device.

        Args:
            device_type (str): Type of the device (e.g., 'tv').
            device (dict): The device configuration dictionary.
            command (str): The playback command to execute (e.g., 'play', 'pause', 'stop').
            payload (str or dict): JSON string or dictionary containing playback command information.
        """
        device_id = device.get("device_id") or device.get("object_id")
        
        self.logger.info(
            "Handling playback command: Device Type: %s, Device ID: %s, Command: %s, Payload: %s",
            device_type,
            device_id,
            command,
            payload,
        )
        
        # Ensure payload is a dictionary by parsing JSON if it's a string
        if isinstance(payload, str):
            try:
                payload_dict = json.loads(payload)
            except json.JSONDecodeError as e:
                self.logger.error("Failed to decode JSON payload: %s", e)
                return
        else:
            payload_dict = payload

        # Validate the payload structure and content
        if not await self.validate_payload(payload_dict, command):
            self.logger.error("Invalid payload: %s", payload_dict)
            return

        # Handle playback commands
        try:
            success = False
            if command == "play":
                success = await self.playback_intent_service.play(device)
            elif command == "pause":
                success = await self.playback_intent_service.pause(device)
            elif command == "stop":
                success = await self.playback_intent_service.stop(device)
            elif command == "rewind":
                success = await self.playback_intent_service.rewind(device)
            elif command == "fastforward":
                success = await self.playback_intent_service.fast_forward(device)
            elif command == "startover":
                success = await self.playback_intent_service.start_over(device)
            elif command == "previous":
                success = await self.playback_intent_service.previous(device)
            elif command == "next":
                success = await self.playback_intent_service.next(device)
            else:
                self.logger.error("Invalid playback command: %s", command)

            if success:
                self.logger.info(
                    "Successfully executed playback command '%s' for device %s.",
                    command,
                    device_id,
                )
            else:
                self.logger.error(
                    "Failed to execute playback command for device %s.", device_id
                )

        except Exception as e:
            self.logger.error(
                "Exception while executing playback command '%s' for device %s: %s",
                command,
                device_id,
                e,
            )

    async def validate_payload(self, payload: dict, command: str) -> bool:
        """
        Validate the structure and content of the payload based on the command.

        Args:
            payload (dict): The JSON payload dictionary to validate.
            command (str): The playback command to execute (e.g., 'play', 'pause', 'stop').

        Returns:
            bool: True if the payload is valid, False otherwise.
        """
        # In this scenario, most playback commands may not require specific payload validation.
        # However, if additional parameters are needed, implement the checks here.
        if command not in [
            "play",
            "pause",
            "stop",
            "rewind",
            "fastforward",
            "startover",
            "previous",
            "next",
        ]:
            self.logger.error("Invalid playback command: %s", command)
            return False

        # Additional validation logic can be added here if needed
        return True
