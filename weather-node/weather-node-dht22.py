from machine import Pin, lightsleep, deepsleep
import dht

# --- Config ----------------------------------------------------------------
# False = lightsleep: resumes the loop, keeps the USB REPL alive (use in dev).
# True  = deepsleep: lowest power, but RESETS the board each cycle (production).
DEEP_SLEEP = False
INTERVAL_SECONDS = 15  # DHT22 needs at least 2 seconds between reads

# Initialize the DHT22 sensor
sensor = dht.DHT22(Pin(16))


def read_and_report():
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


def sleep(interval_seconds):
    interval = interval_seconds * 1000
    if interval < 2000:
        interval = 2000

    if DEEP_SLEEP:
        # deepsleep() powers down and RESETS the board, so it never returns --
        # the whole script re-runs from the top on wake.
        deepsleep(interval)
    else:
        # lightsleep() resumes on the next line, keeping the loop (and REPL) alive.
        lightsleep(interval)


# Works for both modes: under deepsleep the board resets so the loop body runs
# once per wake; under lightsleep it iterates normally.
while True:
    sleep(INTERVAL_SECONDS)
    read_and_report()

