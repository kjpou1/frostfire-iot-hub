import asyncio
import logging

import paho.mqtt.client as mqtt
import time
from app.config.config import Config


class MqttService:
    def __init__(self, heartbeat_interval: int = 10):
        """
        Initialize the MQTT service with a heartbeat interval for connection checks.

        :param heartbeat_interval: Interval in seconds for heartbeat status checks.
        """
        self.logger = logging.getLogger(__name__)

        # Initialize the MQTT client and connection parameters
        self.client_id = "mqtt_service_singleton"
        config = Config()  # Load configuration
        self.broker = config.MQTT_BROKER
        self.port = config.MQTT_PORT
        self.topic = config.MQTT_TOPIC

        # Create an MQTT client
        self.client = mqtt.Client(client_id=self.client_id)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message  # Set the on_message callback
        self.client.on_disconnect = self.on_disconnect

        # Event loop and connection status
        try:
            self.loop = asyncio.get_running_loop()
        except RuntimeError:
            self.loop = asyncio.get_event_loop()

        self.connected_event = asyncio.Event()
        self._is_connected = False  # Track connection status
        self._initial_connection_attempt = False  # Track if we've tried the initial connection
        self.heartbeat_interval = heartbeat_interval  # Heartbeat check interval in seconds

    def connect(self) -> None:
        """Synchronous connect method."""
        self.logger.info("Connecting to MQTT broker synchronously.")
        try:
            self.client.connect(self.broker, self.port)
            self.client.loop_start()
            self.logger.info("Synchronous connection attempt made.")
        except Exception as e:
            self.logger.error("Synchronous connection failed: %s", e)

    async def async_connect(self) -> None:
        """Asynchronous method to connect to the MQTT broker."""
        self.logger.info("Asynchronously connecting to MQTT broker...")

        try:
            # Use asyncio.to_thread to run the connect method in a non-blocking manner
            await asyncio.to_thread(self.client.connect, self.broker, self.port)
            self.client.loop_start()  # Start the MQTT client loop after connecting
            self.logger.info("Asynchronous connection attempt made. Waiting for broker confirmation...")
        except Exception as e:
            self.logger.error("Async connection failed: %s", e)
                
    def on_connect(self, client, userdata, flags, rc) -> None:
        """Callback when the client connects to the broker."""
        if rc == 0:
            self.logger.info("Connected to MQTT broker.")
            self.client.subscribe(self.topic)
            self.logger.info("Subscribed to topic: %s", self.topic)
            # Set the initial connection attempt flag to True after the first connection
            self._initial_connection_attempt = True            
            asyncio.run_coroutine_threadsafe(self._set_connected_event(), self.loop)
        else:
            self.logger.error("Failed to connect, return code %d", rc)

    def on_disconnect(self, client, userdata, rc) -> None:
        """Callback when the client disconnects from the broker."""
        self.logger.warning("Disconnected from MQTT broker. Return code: %d", rc)
        self._is_connected = False  # Set connection status to False
        self.connected_event.clear()  # Clear the connection event
        
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

    async def _set_connected_event(self) -> None:
        """Set the connection event when connected."""
        self._is_connected = True  # Mark as connected
        self.connected_event.set()

    async def heartbeat(self) -> None:
        """
        Heartbeat task to check the connection status and attempt reconnection if disconnected.
        """
        while True:
            if not self._is_connected:
                self.logger.warning("MQTT client is not connected. Attempting to connect/reconnect...")

                try:
                    # Check if the initial connection has never been made
                    if not self._initial_connection_attempt:
                        self.logger.info("Initial connection attempt failed. Trying to connect again...")
                        self.connect()
                    else:
                        # If initial connection succeeded, attempt to reconnect
                        self.logger.info("Attempting to reconnect...")
                        self.client.reconnect()

                    self.logger.info("Connection/reconnection attempt made. Waiting for broker confirmation...")
                except Exception as e:
                    self.logger.error("Connection/reconnection failed: %s", e)
            else:
                self.logger.info("MQTT client is healthy and connected.")

            # Wait for the specified heartbeat interval before the next check
            await asyncio.sleep(self.heartbeat_interval)
            
    async def publish(self, topic: str, payload: dict) -> None:
        """Publish a message to a topic."""
        self.logger.info("Publishing message to topic %s", topic)
        result = await asyncio.to_thread(self.client.publish, topic, payload)

        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            self.logger.info("Message published to topic %s", topic)
        else:
            self.logger.error("Failed to publish message. Return code %d", result.rc)

    async def wait_for_connection(self, timeout: int = 10) -> None:
        """
        Wait until the connection to the MQTT broker is established or timeout occurs.

        :param timeout: The maximum time to wait for a connection, in seconds.
        """
        self.logger.info("Waiting for MQTT connection with timeout of %d seconds...", timeout)
        try:
            await asyncio.wait_for(self.connected_event.wait(), timeout=timeout)
            if self._is_connected:
                self.logger.info("Successfully connected to the MQTT broker.")
            else:
                self.logger.warning("Failed to connect within the timeout period.")
        except asyncio.TimeoutError:
            self.logger.warning("MQTT connection attempt timed out after %d seconds.", timeout)

    async def disconnect(self) -> None:
        """Disconnect from the broker."""
        self.client.loop_stop()
        self.client.disconnect()
        self.logger.info("Disconnected from MQTT broker.")
