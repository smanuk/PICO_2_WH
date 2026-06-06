from machine import Pin, lightsleep, deepsleep
import dht
import json

# --- Config ----------------------------------------------------------------
# Settings live in config.json on the device, read at runtime. Edit that file
# (no code change needed) to tune behaviour. Keys:
#   location         label for this node, included in the reading output.
#   deep_sleep       False = lightsleep: resumes the loop, keeps the USB REPL
#                          alive (use in dev).
#                    True  = deepsleep: lowest power, but RESETS the board each
#                          cycle (production).
#   interval_seconds delay between reads (DHT22 needs at least 2 seconds).
#   dht_pin          GPIO the sensor's data line is wired to.
DEFAULTS = {
    "location": "unknown",
    "deep_sleep": False,
    "interval_seconds": 15,
    "dht_pin": 16,
}


def load_config():
    try:
        with open("config.json") as f:
            cfg = json.load(f)
        # Fill in anything missing from the file with the defaults.
        return {**DEFAULTS, **cfg}
    except (OSError, ValueError) as e:
        print("Could not read config.json ({}); using defaults.".format(e))
        return dict(DEFAULTS)


def read_and_report():
    try:
        # Trigger measurement
        sensor.measure()
        # Read values
        temperature = sensor.temperature()  # In Celsius
        humidity = sensor.humidity()  # In Percent
        # Print values
        print("[{}] Temperature: {} °C Humidity: {} %".format(
            config["location"], temperature, humidity))
    except OSError as e:
        print("Failed to read sensor DHT22. {}".format(e))


def sleep(interval_seconds):
    interval = interval_seconds * 1000
    if interval < 2000:
        interval = 2000

    if config["deep_sleep"]:
        # deepsleep() powers down and RESETS the board, so it never returns --
        # the whole script re-runs from the top on wake.
        deepsleep(interval)
    else:
        # lightsleep() resumes on the next line, keeping the loop (and REPL) alive.
        lightsleep(interval)


config = load_config()

# Initialize the DHT22 sensor
sensor = dht.DHT22(Pin(config["dht_pin"]))

# Works for both modes: under deepsleep the board resets so the loop body runs
# once per wake; under lightsleep it iterates normally.
while True:
    sleep(config["interval_seconds"])
    read_and_report()
