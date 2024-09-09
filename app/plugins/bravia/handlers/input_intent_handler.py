import json
import logging

from ..services.input_intent_service import InputIntentService


class InputIntentHandler:
    """
    A handler class to process input change directives for TV devices.
    """

    def __init__(self, input_intent_service: InputIntentService):
        """
        Initialize the InputIntentHandler with the InputIntentService.
        """
        self.logger = logging.getLogger(__name__)
        self.input_intent_service = input_intent_service

    async def handle_input_change(self, device_type: str, device: dict, payload):
        """
        Handle the input change directive for a given device.

        :param device_type: Type of the device (e.g., 'tv').
        :param device: Dictionary containing device configuration details.
        :param payload: JSON string or dictionary containing input change information.
        """
        device_id = device.get("device_id") or device.get("object_id")
        self.logger.info(
            "Handling input change directive: Device Type: %s, Device ID: %s, Payload: %s",
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

        # Extract action and input from the validated payload
        action = payload_dict.get("action")
        input_source = payload_dict.get("input")

        if action == "selectInput" and input_source:
            success = await self.input_intent_service.select_input(
                device, input_source
            )

            if success:
                self.logger.info(
                    "Successfully changed input to %s for device %s.",
                    input_source,
                    device_id,
                )
            else:
                self.logger.error("Failed to change input for device %s.", device_id)
        else:
            self.logger.error("Invalid action or input source in payload.")


    def validate_payload(self, payload: dict) -> bool:
        """
        Validate the structure and content of the payload.

        :param payload: The JSON payload dictionary to validate.
        :return: True if the payload is valid, False otherwise.
        """
        if "action" not in payload or payload["action"] != "selectInput":
            self.logger.error("Invalid or missing 'action' key for input change.")
            return False
        if "input" not in payload:
            self.logger.error("Payload missing 'input' key for input change.")
            return False

        return True
