# NOTE: this file is deliberately NOT called dht.py -- that would shadow the
# built-in `dht` module imported below.
from machine import Pin
import dht


def create(pin):
    """Initialise a DHT22 on the given GPIO and return the sensor object."""
    return dht.DHT22(Pin(pin))


def read_and_report(sensor, location):
    try:
        # Trigger measurement
        sensor.measure()
        # Read values
        temperature = sensor.temperature()  # In Celsius
        humidity = sensor.humidity()  # In Percent
        # Print values
        print("[{}] Temperature: {} °C Humidity: {} %".format(
            location, temperature, humidity))
    except OSError as e:
        print("Failed to read sensor DHT22. {}".format(e))
