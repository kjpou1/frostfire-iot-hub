import json
import logging
from ..services.power_intent_service import PowerIntentService


class PowerIntentHandler:
    """
    A handler class to process power set directives for devices.
    """

    POWER_ON = "ON"
    POWER_OFF = "OFF"
    POWER_INTENT = "PowerIntent"

    def __init__(self, power_intent_service: PowerIntentService):
        """Initialize the PowerIntentHandler with the PowerIntentService."""
        self.logger = logging.getLogger(__name__)
        self.power_intent_service = power_intent_service

    async def handle_power_set(self, device_type: str, device: dict, payload):
        """
        Handle the power set directive for a given device.

        :param device_type: Type of the device (e.g., 'tv').
        :param device: Dictionary containing the device's configuration, including device_id and other attributes.
        :param payload: JSON string or dictionary containing power state information.
        """
        device_id = device.get("device_id")
        self.logger.info(
            "Handling power set directive: Device Type: %s, Device ID: %s, Payload: %s",
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

        # Extract power state from the validated payload
        power_state = payload_dict["powerState"].strip().upper()

        # Pass the device structure to the PowerIntentService to handle the action
        success = False
        if power_state == self.POWER_ON:
            success = await self.power_intent_service.handle_power_on_intent(device)
        elif power_state == self.POWER_OFF:
            success = await self.power_intent_service.handle_power_off_intent(device)
        else:
            self.logger.error("Invalid power state received: %s", power_state)

        if success:
            self.logger.info(
                "Power state successfully set to %s for device %s.",
                power_state,
                device_id,
            )
        else:
            self.logger.error("Failed to set power state for device %s.", device_id)

    def validate_payload(self, payload: dict) -> bool:
        """
        Validate the structure and content of the payload.

        :param payload: The JSON payload dictionary to validate.
        :return: True if the payload is valid, False otherwise.
        """
        if "powerState" not in payload:
            self.logger.error("Payload missing 'powerState' key.")
            return False

        power_state = payload["powerState"].strip().upper()

        if power_state not in [self.POWER_ON, self.POWER_OFF]:
            self.logger.error("Invalid 'powerState' value: %s", power_state)
            return False

        return True
