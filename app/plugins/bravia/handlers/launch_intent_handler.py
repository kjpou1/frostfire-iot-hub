import json
import logging

from ..services.launch_intent_service import LaunchIntentService


class LaunchIntentHandler:
    """
    A handler class to process launch directives for TV devices.
    """

    def __init__(self, launch_intent_service: LaunchIntentService):
        """
        Initialize the LaunchIntentHandler with the LaunchIntentService.
        :param launch_intent_service: Instance of LaunchIntentService to manage launch actions.
        """
        self.logger = logging.getLogger(__name__)
        self.launch_intent_service = launch_intent_service

    async def handle_launch_command(self, device_type: str, device: dict, payload):
        """
        Handle the launch command directive for a given device.

        :param device_type: Type of the device (e.g., 'tv').
        :param device: Dictionary containing device-specific configuration.
        :param payload: JSON string or dictionary containing launch command information.
        """
        device_id = device.get("device_id") or device.get("object_id")
        self.logger.info(
            "Handling launch command: Device Type: %s, Device ID: %s, Payload: %s",
            device_type,
            device_id,
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
        if not self.validate_payload(payload_dict):
            self.logger.error("Invalid payload: %s", payload_dict)
            return

        # Handle the launch command
        try:
            app_name = payload_dict.get("app")
            if app_name:
                success = await self.launch_intent_service.launch_app(
                    device, app_name
                )
            else:
                self.logger.error("No 'app' specified for launch command.")
                success = False

            if success:
                self.logger.info(
                    "Successfully executed launch command for device %s.",
                    device_id,
                )
            else:
                self.logger.error(
                    "Failed to execute launch command for device %s.", device_id
                )

        except Exception as e:
            self.logger.error(
                "Exception while executing launch command for device %s: %s",
                device_id,
                e,
            )

    def validate_payload(self, payload: dict) -> bool:
        """
        Validate the structure and content of the payload.

        :param payload: The JSON payload dictionary to validate.
        :return: True if the payload is valid, False otherwise.
        """
        if "action" not in payload or payload["action"] != "launch":
            self.logger.error("Invalid or missing 'action' key for launch command.")
            return False
        if "app" not in payload:
            self.logger.error("Payload missing 'app' key for launch command.")
            return False

        return True
