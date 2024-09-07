import asyncio
import logging

import paho.mqtt.client as mqtt

from app.config.config import Config


class MqttService:
    def __init__(self):
        # Initialize logger for the class.
        # Using logging.getLogger(__name__) ties the logger to the module's name,
        # which integrates with Python's logging hierarchy. This allows granular
        # control of logging at the module level.
        self.logger = logging.getLogger(__name__)
        # Initialize _is_initialized to False to avoid accessing it before it's defined
        self._is_initialized = False

        # Ensure that the class is only initialized once
        if not self._is_initialized:
            config = Config()  # Load configuration
            self.client_id = "mqtt_service_singleton"
            self.broker = config.MQTT_BROKER
            self.port = config.MQTT_PORT
            self.topic = config.MQTT_TOPIC

            # Create an MQTT client
            self.client = mqtt.Client(client_id=self.client_id)
            self.client.on_connect = self.on_connect
            self.client.on_message = self.on_message
            self.client.on_disconnect = self.on_disconnect

            # Get the current asyncio event loop or create one if necessary
            try:
                self.loop = asyncio.get_running_loop()
            except RuntimeError:  # No running loop
                self.loop = asyncio.get_event_loop()

            # Async event to track connection status
            self.connected_event = asyncio.Event()
            self._is_initialized = True

    def connect(self) -> None:
        """
        Initiate a connection to the MQTT broker and start the MQTT loop.
        """
        self.logger.info("Connecting to MQTT broker asynchronously.")
        self.loop.run_in_executor(None, self._connect_and_loop)

    def _connect_and_loop(self) -> None:
        """
        Private method to handle the connection and start the MQTT loop.
        """
        try:
            self.client.connect(self.broker, self.port)
            self.client.loop_start()  # Start the MQTT loop in a background thread
        except Exception as e:
            self.logger.error("Failed to connect to MQTT broker: %s", e)

    def on_connect(self, client, userdata, flags, rc) -> None:
        """
        Callback method when the client successfully connects to the broker.
        """
        if rc == 0:
            self.logger.info("Connected to MQTT broker.")
            self.client.subscribe(self.topic)
            self.logger.info("Subscribed to topic: %s", self.topic)
            # Set the asyncio event in the current event loop
            asyncio.run_coroutine_threadsafe(self._set_connected_event(), self.loop)
        else:
            self.logger.error("Failed to connect, return code %d", rc)

    async def _set_connected_event(self) -> None:
        """
        Set the asyncio event to indicate that the connection is established.
        """
        self.connected_event.set()

    def on_disconnect(self, client, userdata, rc) -> None:
        """
        Callback when the client disconnects from the broker.
        """
        self.logger.warning("Disconnected from MQTT broker. Return code: %d", rc)
        self.connected_event.clear()

    def on_message(self, client, userdata, message) -> None:
        """
        Callback when a message is received on a subscribed topic.
        """
        self.logger.info(
            "Received message on %s: %s", message.topic, message.payload.decode("utf-8")
        )
        asyncio.run_coroutine_threadsafe(self.process_message(message), self.loop)

    async def process_message(self, message) -> None:
        """
        Process the received MQTT message asynchronously.
        This method can be customized to handle different types of message processing.
        """
        self.logger.info("Processing message: %s", message.payload.decode("utf-8"))
        await asyncio.sleep(1)  # Simulate async processing (replace with actual logic)

    async def publish(self, topic: str, payload: dict) -> None:
        """
        Asynchronously publish a message to the MQTT broker.
        """
        self.logger.info("Publishing message to topic %s", topic)
        result = await asyncio.to_thread(self.client.publish, topic, payload)
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            self.logger.info("Message published to topic %s", topic)
        else:
            self.logger.error("Failed to publish message. Return code %d", result.rc)

    async def wait_for_connection(self) -> None:
        """
        Wait until the connection to the MQTT broker is established.
        """
        self.logger.info("Waiting for MQTT connection...")
        await self.connected_event.wait()

    async def disconnect(self) -> None:
        """
        Disconnect the client from the broker.
        """
        self.client.loop_stop()
        self.client.disconnect()
        self.logger.info("Disconnected from MQTT broker.")
