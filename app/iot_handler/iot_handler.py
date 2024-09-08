import asyncio
import logging
import importlib
import inspect
import os
from app.plugins.plugin_interface import IotPlugin
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
        self.plugin_dir = self.config.PLUGINS_DIR

        # Store the current asyncio event loop to schedule tasks
        self.loop = asyncio.get_event_loop()

    async def load_plugins(self):
        """
        Dynamically load all plugins from the 'plugins' directory that implement the IPlugin interface,
        and call their initialize method.
        """
        plugins = []

        for module_name in os.listdir(self.plugin_dir):
            if module_name.endswith('.py') and not module_name.startswith('__'):
                # Import module dynamically
                module_path = f"app.plugins.{module_name[:-3]}"
                try:
                    module = importlib.import_module(module_path)

                    # Find all classes in the module that implement the IotPlugin interface
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if issubclass(obj, IotPlugin) and obj is not IotPlugin:
                            plugin_instance = obj()  # Instantiate plugin
                            await plugin_instance.initialize()  # Call initialize on the plugin
                            plugins.append(plugin_instance)
                            # Log the plugin that has been loaded
                            self.logger.debug(f"Loaded plugin: {name}")
                except Exception as e:
                    self.logger.error(f"Error loading plugin {module_name}: {e}")

        return plugins

    def subscribe_plugin_topics(self):
        """
        Subscribe the MQTT client to all topics handled by the loaded plugins.
        """
        for plugin in self.plugins:
            for topic in plugin.get_topics():
                self.mqtt_service.client.subscribe(topic)
                self.logger.info("Subscribed to topic: %s", topic)
                
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

        # Loop through each plugin and find the one that can handle this topic
        for plugin in self.plugins:
            if plugin.can_handle_topic(topic):
                self.logger.info(f"Delegating message on topic {topic} to plugin {plugin.__class__.__name__}")
                await plugin.process_message(topic, payload)
                break
        else:
            self.logger.warning(f"No plugin found to handle topic: {topic}")
        
    
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

            # Load plugins and subscribe to their topics
            self.plugins = await self.load_plugins()  # Ensure plugins are loaded and initialized
            self.subscribe_plugin_topics()  # Subscribe the loaded plugins' topics

            # Start the heartbeat task to maintain the MQTT connection
            heartbeat_task = asyncio.create_task(self.mqtt_service.heartbeat())

            # Set the synchronous message handler for MQTT messages
            self.mqtt_service.client.on_message = self.on_message_sync
        
            # Keep the process running until interrupted
            while True:
                await asyncio.sleep(1)

        except asyncio.CancelledError:
            # Handle process cancellation gracefully
            self.logger.info("Stopping IOT Handler process.")
        finally:
            for plugin in self.plugins:
                await plugin.shutdown()            
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
