from machine import Pin
import utime
import dht

# Initialize the DHT11 sensor
sensor = dht.DHT22(Pin(16))

while True:
    try:
        # Trigger measurement
        sensor.measure()
        # Read values
        temperature = sensor.temperature()  # In Celsius
        humidity = sensor.humidity()  # In Percent
        # Print values
        print("Temperature: {} °C Humidity: {} %".format(temperature, humidity))
    except OSError as e:
        print("Failed to read sensor DHT22. {}".format(e))
    utime.sleep(2)
