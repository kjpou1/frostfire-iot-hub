import fnmatch
import json
import logging
from app.plugins.plugin_interface import IotPlugin

class NfcPlugin(IotPlugin):
    """
    NFC Plugin for handling IoT messages related to NFC tags. This plugin processes messages for 
    actions such as move, consume, add to shopping list, and open.
    """

    def __init__(self):
        """
        Initialize the NFC Plugin by defining the list of topics this plugin can handle.
        """
        self.logger = logging.getLogger(__name__)
        self.nfc_topics = [
            "domus/devices/nfc/+/move",
            "domus/devices/nfc/+/consume",
            "domus/devices/nfc/+/add_to_shopping_list",
            "domus/devices/nfc/+/open",
            "domus/devices/nfc/+/add"
        ]

    async def initialize(self):
        """
        Initialization logic for the NFC Plugin. This could include setting up any 
        necessary connections or loading configurations.
        """
        self.logger.info("NFC Plugin initialized.")

    def can_handle_topic(self, topic: str) -> bool:
        """
        Determine if this plugin can handle the given topic.

        This function uses the `fnmatch` module to match the incoming topic with the topics
        that the plugin is subscribed to. Since MQTT topics can contain wildcards (`+` and `#`),
        we translate those wildcards to the equivalent shell-style wildcards supported by `fnmatch`:
        
        - The `+` MQTT wildcard is converted to `*` in `fnmatch`, which matches any single-level element in the topic.
        - The `#` MQTT wildcard is converted to `**` in `fnmatch`, which matches multiple levels in the topic hierarchy.

        For example:
        - `domus/devices/nfc/+/move` will match `domus/devices/nfc/tag123/move`
        
        Parameters:
        - topic (str): The MQTT topic of the incoming message.
        
        Returns:
        - bool: True if the plugin can handle the topic, False otherwise.
        """
        for t in self.nfc_topics:
            # Convert MQTT wildcards (+ -> *, # -> **) to fnmatch-compatible wildcards
            pattern = t.replace("+", "*").replace("#", "**")
            if fnmatch.fnmatch(topic, pattern):
                return True
        return False

    def get_topics(self) -> list:
        """
        Return the list of topics that the NFC plugin is subscribed to.
        
        Returns:
        - list: List of MQTT topics that the plugin can handle.
        """
        return self.nfc_topics

    async def process_message(self, topic: str, payload: str):
        """
        Process the message received on a subscribed topic.

        This function handles the payload of the message and takes action based on the topic.
        
        Parameters:
        - topic (str): The MQTT topic on which the message was received.
        - payload (str): The payload of the message.
        """
        self.logger.info(f"Processing message on topic: {topic} with payload: {payload}")
        
        if "move" in topic:
            await self.handle_move(payload)
        elif "consume" in topic:
            await self.handle_consume(payload)
        elif "add_to_shopping_list" in topic:
            await self.handle_add_to_shopping_list(payload)
        elif "open" in topic:
            await self.handle_open(payload)
        elif "add" in topic:
            await self.handle_add(payload)
        else:
            self.logger.warning(f"Unrecognized topic action: {topic}")

    async def handle_move(self, payload: str):
        """
        Handle the 'move' action for the NFC tag.
        
        Parameters:
        - payload (str): The message payload for the move action, which contains
                        'from', 'to', and optional 'quantity' fields.
        """
        self.logger.info(f"Handling move action with payload: {payload}")

        try:
            # Parse the payload into a dictionary
            data = json.loads(payload)

            # Extract necessary fields
            from_location = data.get("from")
            to_location = data.get("to")
            quantity = data.get("quantity", 1)  # Default to 1 if quantity is not provided

            # Ensure both 'from' and 'to' locations are provided
            if not from_location or not to_location:
                self.logger.error("Missing 'from' or 'to' location in the payload.")
                return {"error": "Both 'from' and 'to' locations are required."}
            
            self.logger.info(f"Moving {quantity} item(s) from {from_location} to {to_location}.")

            # Add logic to handle the actual movement between locations here.
            # For example, interacting with an inventory system, updating records, etc.
            # This could be a call to an external service, database update, etc.
            success = True #await self.inventory_service.move_item(from_location, to_location, quantity)
            
            if success:
                self.logger.info(f"Successfully moved {quantity} item(s) from {from_location} to {to_location}.")
                return {"status": "success", "message": f"Moved {quantity} item(s) from {from_location} to {to_location}."}
            else:
                self.logger.error(f"Failed to move items from {from_location} to {to_location}.")
                return {"status": "failure", "message": "Failed to move items."}

        except json.JSONDecodeError as e:
            self.logger.error(f"JSON parsing error: {e}")
            return {"error": "Invalid payload format."}
    
    async def handle_consume(self, payload: str):
        """
        Handle the 'consume' action for the NFC tag.

        Parameters:
        - payload (str): The message payload for the consume action, which can be empty.
        """
        self.logger.info(f"Handling consume action with payload: {payload}")

        try:
            # Default consume quantity is 1 if not provided
            if not payload.strip():
                self.logger.info("No payload provided. Consuming 1 unit by default.")
                quantity = 1
            else:
                # Parse the payload (to check if the quantity or other information is provided)
                data = json.loads(payload)
                quantity = data.get("quantity", 1)  # Default to 1 if no quantity is specified
            
            self.logger.info(f"Consuming {quantity} units.")

            # Here, implement the logic to consume the item (e.g., reduce stock or update inventory)
            success = True #await self.inventory_service.consume_item(quantity)

            if success:
                self.logger.info(f"Successfully consumed {quantity} unit(s).")
                return {"status": "success", "message": f"Consumed {quantity} unit(s)."}
            else:
                self.logger.error(f"Failed to consume {quantity} unit(s).")
                return {"status": "failure", "message": f"Failed to consume {quantity} unit(s)."}

        except json.JSONDecodeError as e:
            self.logger.error(f"JSON parsing error: {e}")
            return {"error": "Invalid payload format."}


    async def handle_add_to_shopping_list(self, payload: str):
        """
        Handle the 'add to shopping list' action for the NFC tag.
        
        Parameters:
        - payload (str): The message payload for the add to shopping list action, which can be empty.
        """
        self.logger.info(f"Handling add to shopping list action with payload: {payload}")

        try:
            # Check if the payload is empty
            if not payload.strip():
                self.logger.info("No payload provided. Adding 1 unit to the shopping list by default.")
                quantity = 1
            else:
                # Parse the payload to check if a quantity or other data is provided
                data = json.loads(payload)
                quantity = data.get("quantity", 1)  # Default to 1 if no quantity is specified
            
            self.logger.info(f"Adding {quantity} unit(s) to the shopping list.")

            # Implement the logic to add the item to the shopping list
            success = True #await self.shopping_list_service.add_item(quantity)

            if success:
                self.logger.info(f"Successfully added {quantity} unit(s) to the shopping list.")
                return {"status": "success", "message": f"Added {quantity} unit(s) to the shopping list."}
            else:
                self.logger.error(f"Failed to add {quantity} unit(s) to the shopping list.")
                return {"status": "failure", "message": f"Failed to add {quantity} unit(s) to the shopping list."}

        except json.JSONDecodeError as e:
            self.logger.error(f"JSON parsing error: {e}")
            return {"error": "Invalid payload format."}


    async def handle_open(self, payload: str):
        """
        Handle the 'open' action for the NFC tag.

        Parameters:
        - payload (str): The message payload for the open action, which can be empty.
        """
        self.logger.info(f"Handling open action with payload: {payload}")

        try:
            # If the payload is empty, proceed to mark the item as opened by default
            if not payload.strip():
                self.logger.info("No payload provided. Marking item as opened.")
                item_status = "opened"
            else:
                # Parse the payload (in case we need extra data, for now, we mark it as opened)
                data = json.loads(payload)
                item_status = data.get("status", "opened")  # Default to 'opened'
            
            self.logger.info(f"Marking item as {item_status}.")

            # Here, implement the logic to mark the item as opened in the inventory
            success = True #await self.inventory_service.mark_item_as_opened()

            if success:
                self.logger.info(f"Successfully marked item as {item_status}.")
                return {"status": "success", "message": f"Item marked as {item_status}."}
            else:
                self.logger.error(f"Failed to mark item as {item_status}.")
                return {"status": "failure", "message": f"Failed to mark item as {item_status}."}

        except json.JSONDecodeError as e:
            self.logger.error(f"JSON parsing error: {e}")
            return {"error": "Invalid payload format."}

    async def handle_add(self, payload: str):
        """
        Handle the 'add' action for the NFC tag.
        
        Parameters:
        - payload (str): The message payload for the add action, which contains
                        an optional 'quantity' field or can be empty.
        """
        self.logger.info(f"Handling add action with payload: {payload}")
        
        try:
            # If the payload is empty, default to adding 1 item
            if not payload.strip():
                quantity = 1
                self.logger.info(f"No payload provided. Defaulting to adding {quantity} item.")
            else:
                # Parse the payload into a dictionary
                data = json.loads(payload)
                # Extract optional 'quantity' field, defaulting to 1 if not provided
                quantity = data.get("quantity", 1)
            
            self.logger.info(f"Adding {quantity} item(s) to inventory.")

            # Add logic to handle the actual adding to inventory here
            success = True #await self.inventory_service.add_item(quantity)

            if success:
                self.logger.info(f"Successfully added {quantity} item(s) to inventory.")
                return {"status": "success", "message": f"Added {quantity} item(s) to inventory."}
            else:
                self.logger.error(f"Failed to add items to inventory.")
                return {"status": "failure", "message": "Failed to add items to inventory."}

        except json.JSONDecodeError as e:
            self.logger.error(f"JSON parsing error: {e}")
            return {"error": "Invalid payload format."}



    async def shutdown(self):
        """
        Handle any necessary cleanup for the NFC plugin before shutdown.
        """
        self.logger.info("NFC Plugin shutting down.")
