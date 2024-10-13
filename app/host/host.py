import asyncio
import base64
import json
import logging
import os
from typing import Optional
import uvicorn
from fastapi import FastAPI, Header, HTTPException, Query, Request
from app.config import Config
from app.models import CommandLineArgs
from app.services.mqtt_service import MqttService 

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

        # Access the configuration via properties
        self.host = self.config.HOST
        self.port = self.config.PORT

        # Initialize FastAPI
        self.app = FastAPI()
        self.setup_routes()

        # Initialize MqttService (Singleton)
        self.mqtt_service = MqttService(client_id="mqtt_service_host")

    def setup_routes(self):
        """
        Setup FastAPI routes.
        """
        @self.app.get("/")
        async def read_root():
            return {"message": "Here be dragons... and IoT connections. Welcome to Frostfire IoT Hub, where flames of data light up the digital skies!"}

        @self.app.get("/mqtt/status")
        async def mqtt_status():
            # Use MqttService to check the connection status
            status = "connected" if self.mqtt_service.client.is_connected() else "disconnected"
            return {"status": status}

        @self.app.post("/topics/{url_encoded_topic_name:path}")
        async def mqtt_topics_publish(
            request: Request,
            qos: int = Query(0, description="The Quality of Service level"),
            retain: bool = Query(False, description="Set the RETAIN flag when the message is published"),
            x_amz_mqtt5_user_properties: Optional[str] = Header(None),
            x_api_key: Optional[str] = Header(None, description="API Key for authorization"),
            authorization: Optional[str] = Header(None, description="Bearer Token for authorization")
        ):
           
            # Prioritize validation for x_amz_mqtt5_user_properties first
            if x_amz_mqtt5_user_properties:
                decoded_properties = self.decode_user_properties(x_amz_mqtt5_user_properties)
                api_key = next(
                    (prop.get("API_KEY") for prop in decoded_properties if "API_KEY" in prop), None
                )
                if api_key and api_key not in self.load_api_keys():
                    raise HTTPException(status_code=401, detail="Invalid API Key from user properties")
            # If no x_amz_mqtt5_user_properties, proceed with Bearer Token validation
            elif authorization:
                if not self.validate_bearer_token(authorization):
                    raise HTTPException(status_code=401, detail="Invalid Bearer Token")
            # If no Bearer Token, validate API Key
            elif x_api_key:
                if x_api_key not in self.load_api_keys():
                    raise HTTPException(status_code=401, detail="Invalid API Key")
            else:
                # If none of the above headers are provided, raise an error
                raise HTTPException(status_code=401, detail="API key, Authorization header, or user properties required")

            # Extract the topic from the URL
            full_path = request.url.path
            topic = full_path.split("/topics/", 1)[-1]

            # Validate that the topic is not empty
            if not topic or topic.isspace():
                raise HTTPException(status_code=400, detail="MQTT topic is required and cannot be empty")
            
            # Extract the raw body of the request
            body = await request.body()
            message = body.decode("utf-8")

            # Use MqttService to publish the message
            await self.mqtt_service.publish(topic, message)

            return {"message": f"Message '{message}' published to topic '{topic}' with QoS {qos}."}

    @staticmethod
    def validate_bearer_token(authorization_header: str) -> bool:
        """
        Validate Bearer token from the Authorization header.
        """
        if authorization_header.startswith("Bearer "):
            token = authorization_header.split("Bearer ")[-1]
            # Check if the token exists in the API keys
            return token in Host.load_api_keys() 
        return False
    
    @staticmethod
    def decode_user_properties(encoded_user_properties: str):
        """
        Decode a base64-encoded string and parse it into a JSON object.
        """
        try:
            decoded_bytes = base64.b64decode(encoded_user_properties)
            decoded_string = decoded_bytes.decode("utf-8")

            if decoded_string.startswith('"') and decoded_string.endswith('"'):
                decoded_string = json.loads(decoded_string)

            return json.loads(decoded_string)
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
        Asynchronous method to start both MQTT and FastAPI server concurrently.
        """
        self.logger.info("Starting host process.")
        fastapi_task = None  # Initialize fastapi_task to None

        try:
            # Start MQTT connection asynchronously
            #self.mqtt_service.connect()
            await self.mqtt_service.async_connect()

            # Wait for MQTT connection asynchronously
            await self.mqtt_service.wait_for_connection()

            # Start the heartbeat task
            heartbeat_task = asyncio.create_task(self.mqtt_service.heartbeat())

            # Start FastAPI server as a task
            fastapi_task = asyncio.create_task(self.start_fastapi())

            # Keep the process running until interrupted
            while True:
                await asyncio.sleep(1)

        except asyncio.CancelledError:
            self.logger.info("Stopping host process.")
        finally:
            if fastapi_task:  # Check if fastapi_task is initialized
                fastapi_task.cancel()
                await fastapi_task
            await self.mqtt_service.shutdown()

    async def start_fastapi(self):
        """
        Run the FastAPI application using Uvicorn.
        """
        config = uvicorn.Config(
            self.app,
            host=self.host,
            port=self.port,
            log_level="info",
            ssl_keyfile=self.config.SSL_KEYFILE,
            ssl_certfile=self.config.SSL_CERTFILE,
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
        await instance.run_async()
    except ValueError as e:
        logger.error("Error: %s", e)
    except Exception as e:
        logger.error("Unexpected error: %s", e)


def main():
    asyncio.run(main_async())
