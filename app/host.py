import asyncio
import base64
import json
import logging
import os
import paho.mqtt.client as mqtt
import uvicorn
from fastapi import FastAPI, Header, HTTPException, Query, Request
from app.config import Config
from app.models import CommandLineArgs

class Host:
    def __init__(self, args: CommandLineArgs):
        """
        Initialize the Host class with command line arguments, configuration, and FastAPI setup.
        
        Parameters:
        args (CommandLineArgs): Command line arguments passed to the script.
        """
        self.args = args
        self.config = Config()
        self.logger = logging.getLogger(__name__)

        # MQTT client setup
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        #self.client.on_message = self.on_message

        # Initialize FastAPI
        self.app = FastAPI()
        self.setup_routes()

    def on_connect(self, client, userdata, flags, rc):
        """
        Callback for when the client receives a CONNACK response from the server.
        """
        if rc == 0:
            self.logger.info("Connected to MQTT broker.")
            self.client.subscribe(self.config.MQTT_TOPIC)
        else:
            self.logger.error("Failed to connect, return code %d\n", rc)

    # def on_message(self, client, userdata, msg):
    #     """
    #     Callback for when a PUBLISH message is received from the server.
    #     """
    #     self.logger.info(f"Received message: {msg.payload.decode()} on topic {msg.topic}")

    def setup_routes(self):
        """
        Setup FastAPI routes.
        """
        @self.app.get("/")
        async def read_root():
            return {"message": "Welcome to the Host API!"}

        @self.app.get("/mqtt/status")
        async def mqtt_status():
            return {
                "status": (
                    "connected"
                    if self.client.is_connected()
                    else "disconnected"
                )
            }

        @self.app.post("/topics/{url_encoded_topic_name:path}")
        async def mqtt_topics_publish(
            request: Request,
            qos: int = Query(0, description="The Quality of Service level"),
            retain: bool = Query(
                False, description="Set the RETAIN flag when the message is published"
            ),
            x_amz_mqtt5_user_properties: str = Header(None),
        ):
            # Check if the header exists
            if not x_amz_mqtt5_user_properties:
                # Return 401 Unauthorized if the header is missing
                raise HTTPException(status_code=401, detail="Not authorized")

            # Extract the full path from the request
            full_path = request.url.path

            # Extract the topic part after '/topics/'
            topic = full_path.split("/topics/", 1)[-1]

            # Extract the raw body of the request
            body = await request.body()
            message = body.decode("utf-8")  # Decode bytes to string

            # Decode the base64 encoded header value for user properties
            decoded_properties = self.decode_user_properties(x_amz_mqtt5_user_properties)

            # Check if the API_KEY is present and valid
            api_key = next(
                (
                    prop.get("API_KEY")
                    for prop in decoded_properties
                    if "API_KEY" in prop
                ),
                None,
            )
            if not api_key or api_key not in self.load_api_keys():
                # Return 401 Unauthorized if API_KEY is missing or not valid
                raise HTTPException(status_code=401, detail="Not authorized")

            # Publish the message to the MQTT topic with the specified QoS
            self.client.publish(topic, message, qos, retain=retain)
            return {
                "message": f"Message '{message}' published to topic '{topic}' with QoS {qos}."
            }

    @staticmethod
    def decode_user_properties(encoded_user_properties):
        """
        Decode a base64-encoded string and parse it into a JSON object.
        """
        try:
            # Step 1: Decode from base64
            decoded_bytes = base64.b64decode(encoded_user_properties)
            decoded_string = decoded_bytes.decode("utf-8")

            # Step 2: Check if the decoded string is a valid JSON format or needs further decoding
            if decoded_string.startswith('"') and decoded_string.endswith('"'):
                # The string has an additional layer of quotes, indicating it needs further decoding
                decoded_string = json.loads(decoded_string)

            # Step 3: Parse the decoded string into a Python object (list or dictionary)
            user_properties_json = json.loads(decoded_string)

            return user_properties_json
        except (base64.binascii.Error, json.JSONDecodeError) as e:
            logging.error(f"Error decoding user properties: {e}")
            return None

    @staticmethod
    def load_api_keys(file_path="app/resources/api_keys.txt"):
        """
        Loads the valid API keys from a file.

        Parameters:
        file_path (str): Path to the API keys file.

        Returns:
        set: A set of valid API keys.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                keys = {line.strip() for line in file if line.strip()}
            return keys
        except Exception as e:
            logging.error(f"Error loading API keys from file: {e}")
            return set()

    async def run_async(self):
        """
        Asynchronous method to perform the main logic.
        """
        self.logger.info("Starting host process.")

        # Connect to MQTT broker
        self.client.connect(self.config.MQTT_BROKER, self.config.MQTT_PORT, 60)

        # Start the MQTT loop
        self.client.loop_start()

        # Start FastAPI server
        fastapi_task = asyncio.create_task(self.start_fastapi())

        try:
            while True:
                await asyncio.sleep(1)  # Keep the loop running
        except asyncio.CancelledError:
            self.logger.info("Stopping host process.")
        finally:
            fastapi_task.cancel()
            await fastapi_task
            self.client.loop_stop()
            self.client.disconnect()

    async def start_fastapi(self):
        """
        Run the FastAPI application using Uvicorn.
        """
        config = uvicorn.Config(
            self.app,
            host="0.0.0.0",
            port=8083,
            log_level="debug",
            # ssl_keyfile="letscerts/mosquitto.key",  # Path to your SSL key file
            # ssl_certfile="letscerts/mosquitto.crt",  # Path to your SSL certificate file
            # ssl_keyfile="/etc/letsencrypt/live/hicsvntdracons.xyz/privkey.pem",  # Path to your private key file
            # ssl_certfile="/etc/letsencrypt/live/hicsvntdracons.xyz/fullchain.pem",  # Path to your full chain certificate file
            ssl_keyfile="mosquitto/letscerts/privkey.pem",  # Path to your private key file
            ssl_certfile="mosquitto/letscerts/fullchain.pem",  # Path to your full chain certificate file
            # ssl_keyfile="ssl/private/insecure.key",  # Path to your private key file
            # ssl_certfile="ssl/certs/insecure.pem",  # Path to your full chain certificate file
        )
        server = uvicorn.Server(config)
        await server.serve()

    def run(self):
        """
        Run the asynchronous run_async method.
        """
        return asyncio.run(self.run_async())

async def main_async():
    logger = logging.getLogger(__name__)
    try:
        # Create an instance of Host with parsed arguments
        args = CommandLineArgs()  # Ensure CommandLineArgs is properly initialized
        instance = Host(args)
        # Run the async main function with the parsed arguments
        await instance.run_async()
    except ValueError as e:
        logger.error("Error: %s", e)
    except Exception as e:
        logger.error("Unexpected error: %s", e)

def main():
    asyncio.run(main_async())

# if __name__ == "__main__":
#     # Setup logging configuration
#     logging.basicConfig(
#         level=logging.INFO,
#         format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
#     )

#     main()
