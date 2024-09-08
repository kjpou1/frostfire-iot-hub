import asyncio
import logging
from app.config import Config
from app.models import CommandLineArgs
from app.services.mqtt_service import MqttService

class IotHandler:
    """
    IoT Handler responsible for managing the connection to the MQTT broker and handling
    messages related to various IoT devices such as TVs, lights, thermostats, etc.
    """

    def __init__(self, args: CommandLineArgs):
        """
        Initializes the IotHandler class with command line arguments and an MQTT service.

        Parameters:
        - args (CommandLineArgs): Command line arguments passed to the script.
        
        Attributes:
        - self.mqtt_service: Instance of the MqttService class for handling MQTT connections.
        - self.iot_topics: List of MQTT topics related to various IoT devices.
        """
        self.args = args
        self.config = Config()
        self.logger = logging.getLogger(__name__)

        # Initialize MqttService for the IoT handler
        self.mqtt_service = MqttService(client_id="mqtt_service_iot_handler")

        # Define the topics this handler will subscribe to, including TV-related topics
        self.iot_topics = [
            "domus/devices/tv/#",       # TV-related topics
            "domus/devices/lights/#",   # Lights-related topics
            "domus/devices/thermostat/#"  # Thermostat-related topics
        ]

        # Store the current asyncio event loop to schedule tasks
        self.loop = asyncio.get_event_loop()

    def on_message_sync(self, client, userdata, message):
        """
        Synchronous message handler for MQTT messages. When a message is received,
        it schedules the async handler on the event loop.

        Parameters:
        - client: The MQTT client instance.
        - userdata: User data provided at the time of subscription.
        - message: The message received on the subscribed topic.
        """
        # Use asyncio.run_coroutine_threadsafe to run the async handler on the event loop
        asyncio.run_coroutine_threadsafe(self.on_message_async(client, userdata, message), self.loop)

    async def on_message_async(self, client, userdata, message):
        """
        Asynchronous handler for processing MQTT messages received on subscribed topics.
        Handles specific messages for various IoT devices.

        Parameters:
        - client: The MQTT client instance.
        - userdata: User data provided at the time of subscription.
        - message: The message received on the subscribed topic.
        """
        topic = message.topic
        payload = message.payload.decode("utf-8")  # Decode message payload to a string

        self.logger.info("Received message on topic %s: %s", topic, payload)

        # Route the message to the appropriate handler based on the topic
        if "tv" in topic:
            await self.handle_tv_message(payload)
        elif "lights" in topic:
            await self.handle_lights_message(payload)
        elif "thermostat" in topic:
            await self.handle_thermostat_message(payload)
        else:
            self.logger.warning("Unrecognized topic: %s", topic)

    async def handle_tv_message(self, payload):
        """
        Processes messages related to TV IoT control. Handles commands like power on/off.

        Parameters:
        - payload: The message payload, typically a command (e.g., "power_on", "power_off").
        """
        if payload == "power_on":
            self.logger.info("Turning TV on")
            # Add logic to send the power on command to the TV
        elif payload == "power_off":
            self.logger.info("Turning TV off")
            # Add logic to send the power off command to the TV
        else:
            self.logger.warning("Unrecognized TV command: %s", payload)

    async def handle_lights_message(self, payload):
        """
        Processes messages related to lights IoT control.

        Parameters:
        - payload: The message payload, typically a command like "lights_on" or "lights_off".
        """
        if payload == "lights_on":
            self.logger.info("Turning lights on")
            # Add logic to turn on the lights
        elif payload == "lights_off":
            self.logger.info("Turning lights off")
            # Add logic to turn off the lights
        else:
            self.logger.warning("Unrecognized lights command: %s", payload)

    async def handle_thermostat_message(self, payload):
        """
        Processes messages related to thermostat IoT control.

        Parameters:
        - payload: The message payload, typically a temperature setting (e.g., "set_temp:21").
        """
        try:
            if payload.startswith("set_temp:"):
                temp = int(payload.split(":")[1])
                self.logger.info("Setting thermostat to %d°C", temp)
                # Add logic to set the thermostat temperature
            else:
                self.logger.warning("Unrecognized thermostat command: %s", payload)
        except ValueError:
            self.logger.error("Invalid temperature value: %s", payload)

    async def run_async(self):
        """
        Asynchronous method to start and manage the MQTT service. It connects to the broker,
        maintains the connection with a heartbeat, and runs indefinitely until interrupted.
        """
        self.logger.info("Starting IOT Handler process.")

        try:
            # Asynchronously connect to the MQTT broker
            await self.mqtt_service.async_connect()

            # Wait until the connection is successfully established
            await self.mqtt_service.wait_for_connection()

            # Start the heartbeat task to maintain the MQTT connection
            heartbeat_task = asyncio.create_task(self.mqtt_service.heartbeat())

            # Subscribe to all IoT topics (e.g., TV, lights, thermostat)
            for topic in self.iot_topics:
                self.mqtt_service.client.subscribe(topic)
                self.logger.info("Subscribed to topic: %s", topic)

            # Set the synchronous message handler for MQTT messages
            self.mqtt_service.client.on_message = self.on_message_sync
        
            # Keep the process running until interrupted
            while True:
                await asyncio.sleep(1)

        except asyncio.CancelledError:
            # Handle process cancellation gracefully
            self.logger.info("Stopping IOT Handler process.")
        finally:
            # Ensure graceful disconnection from the MQTT broker
            await self.mqtt_service.shutdown()

    def run(self):
        """
        Entry point to run the asynchronous 'run_async' method. This function runs the
        IoT handler's MQTT service in an asyncio event loop.
        """
        return asyncio.run(self.run_async())

async def main_async():
    """
    Asynchronous main function to initialize and run the IoT handler.
    """
    logger = logging.getLogger(__name__)
    try:
        # Create an instance of the IoT handler with parsed arguments
        args = CommandLineArgs()  # Ensure CommandLineArgs is properly initialized
        instance = IotHandler(args)
        await instance.run_async()
    except ValueError as e:
        logger.error("Error: %s", e)
    except Exception as e:
        logger.error("Unexpected error: %s", e)

def main():
    """
    Main function that sets up the asyncio event loop for the IoT handler process.
    """
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
