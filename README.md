# Frostfire IoT Hub

Frostfire IoT Hub is an advanced and scalable IoT hub designed to facilitate reliable communication and data management for IoT devices. Utilizing MQTT protocol, it provides efficient messaging capabilities suitable for various IoT applications.

- [Frostfire IoT Hub](#frostfire-iot-hub)
  - [Features](#features)
  - [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
    - [Configuration](#configuration)
    - [Setting Up the MQTT Hub](#setting-up-the-mqtt-hub)
      - [Install Mosquitto MQTT Broker](#install-mosquitto-mqtt-broker)
      - [Configure Mosquitto](#configure-mosquitto)
      - [Configure Mosquitto (Example on Raspberry Pi 5)](#configure-mosquitto-example-on-raspberry-pi-5)
    - [Usage](#usage)
    - [Running with Docker Compose](#running-with-docker-compose)
    - [Docker Troubleshooting](#docker-troubleshooting)
      - [Address Already in Use](#address-already-in-use)
      - [Allowing Remote Connections](#allowing-remote-connections)
    - [Configuration](#configuration-1)
  - [Contributing](#contributing)
  - [License](#license)
  - [Sample `publisher.py`](#sample-publisherpy)
  - [Sample `subscriber.py`](#sample-subscriberpy)

## Features

- **Efficient Data Handling:** Optimized for resource-constrained environments.
- **Reliable Messaging:** Uses MQTT protocol for reliable and efficient communication.
- **Scalable Architecture:** Supports multiple devices and scalable message handling.
- **Configurable:** Easy to configure via environment variables.

## Getting Started

### Prerequisites

- Python 3.7+
- MQTT broker (e.g., Mosquitto)
- pip (Python package installer)
- Docker (Optional)
- Docker Compose (Optional)

### Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/kjpou1/frostfire-iot-hub.git
   cd frostfire-iot-hub
   ```

2. Install the required dependencies:
   ```sh
   pip install -r requirements.txt
   ```

3. Configure environment variables by copying `example_env` to `.env` and updating the values:
   ```sh
   cp example_env .env
   ```

### Configuration

All configuration settings are managed through environment variables. Here are the variables you need to set in the `.env` file:

- `MQTT_BROKER`: The address of your MQTT broker.
- `MQTT_PORT`: The port your MQTT broker is listening on.
- `MQTT_TOPIC`: The topic to which the hub subscribes and publishes.

Example `.env` file:
```ini
MQTT_BROKER=mqtt.example.com
MQTT_PORT=1883
MQTT_TOPIC=iot/devices
```

Refer to `app/config/config.py` for more configuration details.

### Setting Up the MQTT Hub

#### Install Mosquitto MQTT Broker

Mosquitto is a popular MQTT broker. Below are the installation steps for various operating systems, including Raspberry Pi:

**For Ubuntu/Debian/Raspberry Pi:**
```sh
sudo apt update
sudo apt install mosquitto mosquitto-clients
sudo systemctl enable mosquitto
sudo systemctl start mosquitto
```

**For macOS (using Homebrew):**
```sh
brew update
brew install mosquitto
brew services start mosquitto
```

**For Windows:**
1. Download the Mosquitto installer from the [Mosquitto website](https://mosquitto.org/download/).
2. Run the installer and follow the instructions.
3. Start the Mosquitto service from the command prompt:
   ```sh
   net start mosquitto
   ```

#### Configure Mosquitto

Edit the Mosquitto configuration file (usually located at `/etc/mosquitto/mosquitto.conf` on Linux/Raspberry Pi) to set your desired configurations. Below is a basic configuration example:

```conf
listener 1883
allow_anonymous true
```

After editing the configuration file, restart Mosquitto:

**For Ubuntu/Debian/Raspberry Pi:**
```sh
sudo systemctl restart mosquitto
```

**For macOS:**
```sh
brew services restart mosquitto
```

**For Windows:**
```sh
net stop mosquitto
net start mosquitto
```

#### Configure Mosquitto (Example on Raspberry Pi 5)

1. Edit the main configuration file (`/etc/mosquitto/mosquitto.conf`) to ensure it includes the following settings:

   ```conf
   pid_file /run/mosquitto/mosquitto.pid

   persistence true
   persistence_location /var/lib/mosquitto/

   log_dest file /var/log/mosquitto/mosquitto.log

   include_dir /etc/mosquitto/conf.d
   ```

2. Create a custom configuration file in `/etc/mosquitto/conf.d/local.conf`:

   ```sh
   sudo nano /etc/mosquitto/conf.d/local.conf
   ```

   Add the following configuration:

   ```conf
   listener 1883
   allow_anonymous true

   # Optional: Set logging verbosity for development
   log_type error
   log_type warning
   log_type notice
   log_type information
   ```

3. Restart Mosquitto to apply the changes:

   ```sh
   sudo systemctl restart mosquitto
   ```

### Usage

1. Run the IoT Hub:
   ```sh
   python run.py
   ```

### Running with Docker Compose

You can set up and run the Frostfire IoT Hub with Mosquitto MQTT broker using Docker Compose. Follow these steps:

1. Ensure you have Docker and Docker Compose installed on your machine.

2. Create the necessary Docker files (`Dockerfile` and `Dockerfile.mosquitto`) as described in the repository.

3. The `docker-compose.yml` file is already included in the root of the project.

4. Run the following command to build and start the services:
   ```sh
   sudo docker compose up --build
   ```

5. The Mosquitto MQTT broker will be accessible on port 1883, and the Frostfire IoT Hub will run and connect to it automatically.

### Docker Troubleshooting

#### Address Already in Use

If you encounter an error indicating that the address is already in use, it means that another process is using the port. Follow these steps to resolve the issue:

1. **Identify the Process Using the Port**

   You can identify which process is using port `1883` with the following command:

   ```sh
   sudo lsof -i -P -n | grep LISTEN | grep 1883
   ```

2. **Stop the Process**

   If the process is Mosquitto, you can stop it with:

   ```sh
   sudo systemctl stop mosquitto
   ```

3. **Retry Docker Compose**

   After stopping the existing service, try running the Docker Compose command again:

   ```sh
   sudo docker compose up --build
   ```

If stopping the existing process is not an option, you can run the MQTT broker on a different port:

1. **Edit the `docker-compose.yml` File**

   Change the port mapping for the MQTT broker to use a different external port, for example, `1884`:

   ```yaml
   version: '3.8'

   services:
     mqtt-broker:
       image: eclipse-mosquitto:latest
       ports:
         - "1884:1883"

     frostfire-iot-hub:
       build:
         context: .
       environment:
         MQTT_BROKER: mqtt-broker
         MQTT_PORT: 1883
         MQTT_TOPIC: iot/devices
       depends_on:
         - mqtt-broker
       ports:
         - "5000:5000"  # Adjust if needed, though this is just for example
   ```

2. **Update Environment Variables**

   Ensure that your environment variables or configuration for the IoT hub points to the new port if necessary.

3. **Retry Docker Compose**

   Run the Docker Compose command again:

   ```sh
   sudo docker compose up --build
   ```

#### Allowing Remote Connections

If the MQTT broker is only allowing local connections, you need to update the Mosquitto configuration to allow remote connections:

1. **Create a Custom Configuration File**

   Create a file named `mosquitto.conf` in the `./mosquitto/config` directory:

   ```sh
   mkdir -p ./mosquitto/config
   nano ./mosquitto/config/mosquitto.conf
   ```

   Add the following content to allow remote connections:

   ```conf
   listener 1883
   allow_anonymous true
   ```

2. **Update `docker-compose.yml`**

   Update your `docker-compose.yml` file to mount the custom configuration:

   ```yaml
   version: '3.8'

   services:
     mqtt-broker:
       image: eclipse-mosquitto:latest
       ports:
         - "1883:1883"
       volumes:
         - ./mosquitto/config/mosquitto.conf:/mosquitto/config/mosquitto.conf

     frostfire-iot-hub:
       build:
         context: .
       environment:
         MQTT_BROKER: mqtt-broker
         MQTT_PORT: 1883
         MQTT_TOPIC: iot/devices
       depends_on:
         - mqtt-broker
       ports:
         - "5000:5000"  # Adjust if needed, though this is just for example
   ```

3. **Restart Docker Compose**

   Run the Docker Compose command again to rebuild and start the services:

   ```sh
   sudo docker compose up --build
   ```

### Configuration

All configuration settings are managed through environment variables. Refer to `app/config/config.py` for more details.

## Contributing

We welcome contributions! Please read our [contributing guidelines](CONTRIBUTING.md) for more details.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Sample `publisher.py`

```python
import logging

import paho.mqtt.client as mqtt

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# MQTT settings
MQTT_BROKER = (
    "localhost"  # Change this to the IP address or hostname of your Raspberry Pi
)
MQTT_PORT = 1883
MQTT_TOPIC = "iot/devices"


def main():
    # Create an MQTT client instance
    client = mqtt.Client()

    # Connect to the MQTT broker
    client.connect(MQTT_BROKER, MQTT_PORT, 60)

    # Publish a test message
    message = "Hello from the publisher!"
    client.publish(MQTT_TOPIC, message)
    logger.info(f"Published message: {message} to topic: {MQTT_TOPIC}")

    # Disconnect from the broker
    client.disconnect()


if __name__ == "__main__":
    main()

```

## Sample `subscriber.py`

```python
import logging

import paho.mqtt.client as mqtt

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# MQTT settings
MQTT_BROKER = (
    "localhost"  # Change this to the IP address or hostname of your Raspberry Pi
)
MQTT_PORT = 1883
MQTT_TOPIC = "iot/devices"


def on_connect(client, userdata, flags, rc):
    """
    Callback for when the client receives a CONNACK response from the server.
    """
    if rc == 0:
        logger.info("Connected to MQTT broker.")
        client.subscribe(MQTT_TOPIC)
    else:
        logger.error("Failed to connect, return code %d\n", rc)


def on_message(client, userdata, msg):
    """
    Callback for when a PUBLISH message is received from the server.
    """
    logger.info(f"Received message: {msg.payload.decode()} on topic {msg.topic}")


def main():
    # Create an MQTT client instance
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message

    # Connect to the MQTT broker
    client.connect(MQTT_BROKER, MQTT_PORT, 60)

    # Start the MQTT client loop
    client.loop_forever()


if __name__ == "__main__":
    main()

```
