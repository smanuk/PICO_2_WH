# NOTE: this file is deliberately NOT called dht.py -- that would shadow the
# built-in `dht` module imported below.
from machine import Pin
import dht


def create(pin):
    """Initialise a DHT22 on the given GPIO and return the sensor object."""
    return dht.DHT22(Pin(pin))


def read(sensor):
    """Measure the DHT22 and return the reading.

    Returns a dict {"temperature": <°C>, "humidity": <%>} on success, or
    None if the read fails (the only thing reported from here is the error).
    """
    try:
        print("[TEMP LOG] read: triggering measure()")  # TEMP: remove
        # Trigger measurement
        sensor.measure()

        temperature = sensor.temperature()  # In Celsius
        humidity = sensor.humidity()  # In Percent
        print("[TEMP LOG] read: temp={} humidity={}".format(  # TEMP: remove
            temperature, humidity))  # TEMP: remove
        return {
            "temperature": temperature,
            "humidity": humidity,
        }
    except OSError as e:
        print("[TEMP LOG] read: OSError -> returning None")  # TEMP: remove
        print("Failed to read sensor DHT22. {}".format(e))
        return None
