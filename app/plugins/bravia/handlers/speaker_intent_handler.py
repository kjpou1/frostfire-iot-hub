import json
import logging
from app.plugins.bravia.services.speaker_intent_service import SpeakerIntentService

class SpeakerIntentHandler:
    """
    A handler class to process speaker directives for devices.
    """

    def __init__(self, speaker_intent_service: SpeakerIntentService):
        """
        Initialize the SpeakerIntentHandler with the injected SpeakerIntentService.
        
        Args:
            speaker_intent_service (SpeakerIntentService): Service for handling speaker commands.
        """
        self.logger = logging.getLogger(__name__)
        self.speaker_intent_service = speaker_intent_service

    async def handle_speaker_command(
        self, device_type: str, device: dict,  subcategory: str, command: str, payload
    ):
        """
        Handle the speaker command directive for a given device.

        Args:
            device_type (str): The type of the device (e.g., 'tv').
            device (dict): The device configuration dictionary.
            subcategory (str): The speaker subcategory (e.g., 'volume', 'mute').
            command (str): The command to execute (e.g., 'set', 'increase', 'decrease').
            payload (str or dict): JSON string or dictionary containing speaker command information.
        """
        device_id = device.get("device_id") or device.get("object_id")
        self.logger.info(
            "Handling speaker command: Device Type: %s, Device: %s, Subcategory: %s, Command: %s, Payload: %s",
            device_type,
            device_id,
            subcategory,
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
        if not await self.validate_payload(payload_dict, subcategory, command):
            self.logger.error("Invalid payload: %s", payload_dict)
            return

        # Handle volume commands
        if subcategory == "volume":
            if command == "set":
                volume = payload_dict.get("volume")
                if volume is not None and isinstance(volume, int):
                    success = await self.speaker_intent_service.handle_volume_intent(
                        device, command, volume
                    )
                else:
                    self.logger.error("Invalid or missing volume for 'set' command.")
                    success = False
            elif command in ["increase", "decrease"]:
                step = payload_dict.get("step", 1)  # Default step to 1 if not provided
                if not isinstance(step, int) or step < 1:
                    self.logger.warning(
                        "Invalid or missing step value; defaulting to 1."
                    )
                    step = 1
                success = await self.speaker_intent_service.handle_volume_intent(
                    device, command, step=step
                )
            else:
                self.logger.error("Invalid volume command: %s", command)
                success = False

        # Handle mute commands
        elif subcategory == "mute":
            mute = payload_dict.get("mute")
            if command == "set":
                if isinstance(mute, bool):
                    if mute:
                        success = await self.speaker_intent_service.handle_volume_intent(
                            device, "mute"
                        )
                    else:
                        success = await self.speaker_intent_service.handle_volume_intent(
                            device, "unmute"
                        )
                else:
                    self.logger.error(
                        "Invalid mute value received, must be a boolean: %s", mute
                    )
                    success = False
            else:
                self.logger.error("Invalid mute command: %s", command)
                success = False

        else:
            self.logger.error("Unknown subcategory: %s", subcategory)
            success = False

        if success:
            self.logger.info(
                "Successfully executed speaker command '%s' for device %s.",
                command,
                device_id,
            )
        else:
            self.logger.error(
                "Failed to execute speaker command for device %s.", device_id
            )

    async def validate_payload(self, payload: dict, subcategory: str, command: str) -> bool:
        """
        Validate the structure and content of the payload based on the subcategory and command.

        Args:
            payload (dict): The JSON payload dictionary to validate.
            subcategory (str): The speaker subcategory (e.g., 'volume', 'mute').
            command (str): The command to execute (e.g., 'set', 'increase', 'decrease').

        Returns:
            bool: True if the payload is valid, False otherwise.
        """
        # Validate payload for volume commands
        if subcategory == "volume":
            if command == "set":
                if "volume" not in payload or not isinstance(payload["volume"], int):
                    self.logger.error(
                        "Payload missing 'volume' key or invalid value for 'set' command."
                    )
                    return False
            elif command in ["increase", "decrease"]:
                # No specific requirement for 'step', defaults to 1 if missing
                if "step" in payload and not isinstance(payload["step"], int):
                    self.logger.warning(
                        "Invalid 'step' value, must be an integer: %s", payload["step"]
                    )
                    return False
            else:
                self.logger.error("Invalid command for volume: %s", command)
                return False

        # Validate payload for mute commands
        elif subcategory == "mute":
            if command == "set" and "mute" not in payload:
                self.logger.error("Payload missing 'mute' key for 'mute' command.")
                return False
            if "mute" in payload and not isinstance(payload["mute"], bool):
                self.logger.error(
                    "Invalid 'mute' value, must be a boolean: %s", payload["mute"]
                )
                return False

        else:
            self.logger.error(
                "Unknown subcategory in payload validation: %s", subcategory
            )
            return False

        return True
