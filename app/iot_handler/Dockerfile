# Use the official Python 3.11.2 image
FROM python:3.11.2-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the required dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Set environment variables
ENV MQTT_BROKER=localhost
ENV MQTT_PORT=1883
ENV MQTT_TOPIC=iot/devices

# Expose the port the app runs on
#EXPOSE 5000

# Command to run the application
CMD ["python", "run_iot_handler.py"]
