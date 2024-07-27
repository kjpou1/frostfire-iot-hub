import asyncio
import logging
import os
import paho.mqtt.client as mqtt
from app.config import Config
from app.models import CommandLineArgs

class Host:
    def __init__(self, args: CommandLineArgs):
        """
        Initialize the Host class with command line arguments and configuration.

        Parameters:
        args (CommandLineArgs): Command line arguments passed to the script.
        """
        self.args = args
        self.config = Config()

        self.logger = logging.getLogger(__name__)

        # MQTT client setup
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        """
        Callback for when the client receives a CONNACK response from the server.
        """
        if rc == 0:
            self.logger.info("Connected to MQTT broker.")
            self.client.subscribe(self.config.MQTT_TOPIC)
        else:
            self.logger.error("Failed to connect, return code %d\n", rc)

    def on_message(self, client, userdata, msg):
        """
        Callback for when a PUBLISH message is received from the server.
        """
        self.logger.info(f"Received message: {msg.payload.decode()} on topic {msg.topic}")

    async def run_async(self):
        """
        Asynchronous method to perform the main logic.
        """
        self.logger.info("Starting host process.")

        # Connect to MQTT broker
        self.client.connect(self.config.MQTT_BROKER, self.config.MQTT_PORT, 60)

        # Start the MQTT loop
        self.client.loop_start()

        try:
            while True:
                await asyncio.sleep(1)  # Keep the loop running
        except asyncio.CancelledError:
            self.logger.info("Stopping host process.")
        finally:
            self.client.loop_stop()
            self.client.disconnect()

    def run(self):
        """
        Run the asynchronous run_async method.
        """
        return asyncio.run(self.run_async())
